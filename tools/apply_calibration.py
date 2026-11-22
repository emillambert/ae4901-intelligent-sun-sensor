"""Transfer real fitted CSV parameters to host and firmware calibration tables.

Does not mark the device qualified. Angles/temperature/illumination must be tested.
Firmware constants require manual review/update; this updates only host JSON.
"""
import argparse
import csv
import json
from pathlib import Path


def apply(source, initial, output):
    config=json.loads(Path(initial).read_text())
    rows=list(csv.DictReader(Path(source).open(newline='')))
    found=set()
    for row in rows:
        i=int(row['sensor_id'])
        if i in found or i not in range(12):
            raise ValueError('Duplicate or unknown sensor id')
        found.add(i)
        gamma=float(row['gamma']);r10=float(row['r10_ohm']);p=float(row['angular_exponent'])
        if r10<=0 or gamma<=0 or p<=0:
            raise ValueError('Nonphysical calibration')
        config['sensors'][i]['r10_ohms']=r10
        config['sensors'][i]['gamma']=gamma
        config['sensors'][i]['angular_exponent']=p
    if found!=set(range(12)):
        raise ValueError('All twelve sensor IDs 0–11 are required')
    config['calibration_verified']=False # deliberate interlock
    Path(output).write_text(json.dumps(config,indent=2)+'\n')
    return config


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--fitted',required=True)
    p.add_argument('--config',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    apply(a.fitted,a.config,a.output)
    print('Host configuration updated; physical verification remains required.')
