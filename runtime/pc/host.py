"""AE4901 compact host/GSE estimator (NOT an on-Arduino V8 implementation).

Inputs: two SUN4 serial streams (one ADC per face from each Arduino).
Outputs: reconstructed body-frame Sun vector, diagnostics, validity state.
Calibration parameters are PLACEHOLDERS; no result is control-qualified.
Requires numpy + scipy; pyserial only when using live serial ports.
"""
import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

FACE_NORMALS = np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]], dtype=float)


def normals():
    k = np.ones(3) / np.sqrt(3)
    result = np.zeros((12, 3))
    for board in (0, 1):
        theta = np.deg2rad(10 if board == 0 else -10)
        for face, v in enumerate(FACE_NORMALS):
            result[2*face+board] = v*np.cos(theta)+np.cross(k,v)*np.sin(theta)+k*np.dot(k,v)*(1-np.cos(theta))
    return result


NORMALS = normals()


def crc16(data):
    crc = 0xFFFF
    for char in data.encode('ascii'):
        crc ^= char << 8
        for _ in range(8):
            crc = ((crc << 1) ^ (0x1021 if (crc & 0x8000) else 0)) & 0xFFFF
    return crc


def parse_packet(s):
    try:
        msg, check = s.strip().split('*')
        if crc16(msg) != int(check, 16):
            return None
        p = msg.split(',')
        if len(p) != 15 or p[0] != 'SUN4' or int(p[1]) not in (0, 1):
            return None
        vals = [int(x) for x in p[4:10]]
        if any(x < 0 or x > 1023 for x in vals):
            return None
        return dict(board=int(p[1]),seq=int(p[2]),ms=int(p[3]),adc=vals,
                    local=[int(x)/10000. for x in p[10:13]],rail=int(p[13]),
                    ready=bool(int(p[14])), received=time.monotonic())
    except (ValueError, UnicodeError):
        return None


def make_packet(board, counts, seq=0, ms=100, rail=0, ready=False):
    fields=['SUN4',str(board),str(seq),str(ms),*[str(int(c)) for c in counts],
            '0','0','0',str(rail),str(int(ready))]
    m=','.join(fields)
    return f'{m}*{crc16(m):X}'


class SunSensor:
    def __init__(self, config):
        self.c = config
        assert len(config['sensors']) == 12
        self.latest = {}
        self.last_direction = None
        self.last_time = None

    def ingest(self, packet):
        if packet is None:
            return False
        old=self.latest.get(packet['board'])
        # Ignore repeated or out-of-order packets in a continuous millisecond epoch.
        if old and packet['seq'] <= old['seq'] and packet['ms'] >= old['ms']:
            return False
        self.latest[packet['board']] = packet
        return True

    def estimate(self, now=None):
        if now is None:
            now=time.monotonic()
        lux=np.full(12,np.nan)
        online=[]
        for board in (0,1):
            packet=self.latest.get(board)
            if packet is None or now-packet['received']>self.c['timeout_s']:
                continue
            online.append(board)
            for face, adc in enumerate(packet['adc']):
                j=face*2+board
                if (packet['rail'] >> face)&1 or not 2<=adc<=1021:
                    continue
                s=self.c['sensors'][j]
                r=s['fixed_ohms']*adc/(1023-adc)
                e=10*(r/s['r10_ohms'])**(-1/s['gamma'])
                lux[j]=max(0.0,e-s.get('background_lux',0.0))
        idx=np.flatnonzero(np.isfinite(lux))
        base=dict(boards_online=online,good_channels=int(len(idx)),
                  calibration_verified=bool(self.c['calibration_verified']),
                  valid_for_control=False)
        if len(idx)<4:
            return dict(base,status='INSUFFICIENT_DATA',vector=None)
        obs=lux[idx]
        if float(obs.max()) < self.c['min_peak_lux']:
            return dict(base,status='DARK_OR_ECLIPSE',vector=None)
        dirs=NORMALS[idx]
        exponents=np.array([self.c['sensors'][i]['angular_exponent'] for i in idx])
        guess=np.sum(obs[:,None]*dirs,axis=0)
        if np.linalg.norm(guess)<1e-9:
            guess=np.array([1.,0.,0.])
        guess=guess/np.linalg.norm(guess)*max(obs)

        def residual(q):
            amp=max(np.linalg.norm(q),1e-9)
            pred=amp*np.maximum(dirs@(q/amp),0)**exponents
            return pred-obs

        sol=least_squares(residual,guess,loss='soft_l1',f_scale=max(1.,.05*obs.max()),max_nfev=70)
        amp=np.linalg.norm(sol.x)
        if not sol.success or amp<1e-9:
            return dict(base,status='ESTIMATOR_FAILED',vector=None)
        u=sol.x/amp
        normalized_fit=float(np.sqrt(np.mean(residual(sol.x)**2))/max(obs.max(),1.))
        status='DEGRADED_ONE_BOARD' if len(online)==1 else 'NORMAL'
        warnings=[]
        if normalized_fit>self.c['warn_residual_fraction']:
            status='SUSPECT_OPTICAL_FIT';warnings.append('One-source model poorly fits observations')
        if self.last_direction is not None and self.last_time is not None:
            delta=np.rad2deg(np.arccos(np.clip(np.dot(u,self.last_direction),-1,1)))
            elapsed=max(now-self.last_time,0.01)
            if delta>self.c['temporal_warning_deg'] and elapsed<self.c['temporal_warning_window_s']:
                warnings.append('Sudden vector change; motion/glint ambiguous')
        # Temporal warning is deliberately not a hard reject without gyro information.
        if status in ('NORMAL','DEGRADED_ONE_BOARD'):
            self.last_direction=u.copy();self.last_time=now
        verified=bool(self.c['calibration_verified'])
        # Never mark software estimates safe for autonomous control before physical checks.
        control_ok=verified and status in ('NORMAL','DEGRADED_ONE_BOARD') and not warnings
        if not verified:
            status='CALIBRATION_REQUIRED' if status in ('NORMAL','DEGRADED_ONE_BOARD') else status
        return dict(base,status=status,vector=u.round(5).tolist(),
                    normalized_fit_residual=round(normalized_fit,5),warnings=warnings,
                    valid_for_control=control_ok)


def synthetic_demo(config):
    sun=np.array([.5,-.3,.81]);sun=sun/np.linalg.norm(sun)
    model=SunSensor(config)
    for board in (0,1):
        counts=[]
        for face in range(6):
            j=2*face+board;s=config['sensors'][j]
            e=60.*max(np.dot(NORMALS[j],sun),0)**s['angular_exponent']
            # Dark readings are represented by saturated (invalid) samples in this demo.
            if e<0.001:counts.append(1023);continue
            r=s['r10_ohms']*(e/10)**(-s['gamma'])
            counts.append(int(np.clip(round(1023*r/(s['fixed_ohms']+r)),0,1023)))
        model.ingest(parse_packet(make_packet(board,counts)))
    return dict(true_sun=sun.round(5).tolist(),estimated=model.estimate())


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',default=str(Path(__file__).with_name('calibration_PLACEHOLDER.json')))
    p.add_argument('--demo',action='store_true')
    p.add_argument('--port-a');p.add_argument('--port-b')
    args=p.parse_args()
    config=json.loads(Path(args.config).read_text())
    if args.demo:
        print(json.dumps(synthetic_demo(config),indent=2));return
    if not args.port_a and not args.port_b:
        p.error('Use --demo or --port-a and/or --port-b')
    try:
        import serial
    except ImportError:
        p.error('Install pyserial to read actual Arduino serial ports')
    ports={board:serial.Serial(port,115200,timeout=.05) for board,port in ((0,args.port_a),(1,args.port_b)) if port}
    sensor=SunSensor(config)
    try:
        while True:
            for board,connection in ports.items():
                pkt=parse_packet(connection.readline().decode('ascii',errors='ignore'))
                if pkt is not None and pkt['board']==board:
                    sensor.ingest(pkt)
            print(json.dumps(sensor.estimate()))
            time.sleep(.1)
    finally:
        for connection in ports.values():connection.close()


if __name__=='__main__':
    main()
