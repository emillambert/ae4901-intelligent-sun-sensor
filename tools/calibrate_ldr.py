#!/usr/bin/env python3
"""Fit per-LDR electrical, angle, and optional temperature calibration from
measured lab CSV. Fits log(R)=log(R10)-gamma*log(lux/10)-gamma*p*log(cos theta)
+kT*(temperature_C-20). This is a *model*, not guaranteed to fit GL5537-1.
Input must contain independent measured lux and reference angles; no real
samples were provided. The synthetic example is explicitly labelled.
"""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
REQUIRED=('sensor_id','lux','angle_deg','temp_c','adc','vref_v','vcc_v','rfixed_ohm','split')

def resistance_from_adc(df):
    v=df.adc.to_numpy(float)*df.vref_v.to_numpy(float)/1023
    cc=df.vcc_v.to_numpy(float)
    rr=df.rfixed_ohm.to_numpy(float)*v/(cc-v)
    return rr

def fit_one(df):
    if len(df)<12: raise ValueError('Insufficient calibration samples')
    if df.temp_c.max()-df.temp_c.min()<8:
        use_temp=False
    else:use_temp=True
    c=np.cos(np.deg2rad(df.angle_deg.to_numpy(float)))
    X=np.column_stack((np.ones(len(df)),np.log(df.lux.to_numpy(float)/10),np.log(c)))
    if use_temp:X=np.column_stack((X,df.temp_c.to_numpy(float)-20))
    y=np.log(df.r_ohm.to_numpy(float))
    w=np.ones(len(y))
    for _ in range(8):
        b=np.linalg.lstsq(X*np.sqrt(w)[:,None],y*np.sqrt(w),rcond=None)[0]
        r=y-X@b
        sd=max(0.008,1.4826*np.median(np.abs(r-np.median(r))))
        w=np.minimum(1,1.5*sd/np.maximum(abs(r),1e-8))
    gamma=-b[1]
    if not(.1<gamma<2):raise ValueError('Invalid fitted gamma; measurements or model may be incompatible')
    p=b[2]/b[1]
    if not(.2<p<4): raise ValueError('Invalid fitted angular exponent')
    return dict(r10_ohm=float(np.exp(b[0])),gamma=float(gamma),angular_exponent=float(p),
                temp_logR_per_C=float(b[3]) if use_temp else None,n_train=int(len(df)))

def predict_r(df,par):
    c=np.cos(np.deg2rad(df.angle_deg.to_numpy(float)))
    result=par['r10_ohm']*(df.lux.to_numpy(float)/10)**(-par['gamma'])*c**(-par['gamma']*par['angular_exponent'])
    if par['temp_logR_per_C'] is not None:
        result=result*np.exp(par['temp_logR_per_C']*(df.temp_c.to_numpy(float)-20))
    return result

def validate_and_fit(file,output):
    df=pd.read_csv(file)
    for field in REQUIRED:
        if field not in df:raise ValueError('Missing '+field)
    if not np.isfinite(df[['lux','angle_deg','temp_c','adc','vref_v','vcc_v','rfixed_ohm']].to_numpy(float)).all():
        raise ValueError('NaN/Inf input')
    if not ((df.lux>=10)&(df.lux<=100)).all():raise ValueError('Only validated 10–100 lux regime accepted for initial fit')
    if not ((df.angle_deg>=0)&(df.angle_deg<=75)).all():raise ValueError('Use 0–75°; back-face response needs a different model')
    if not ((df.adc>1)&(df.adc<1022)).all():raise ValueError('Clipped ADC input, cannot calibrate')
    if not ((df.vref_v>0)&(df.vref_v<=df.vcc_v)&(df.rfixed_ohm>0)).all():raise ValueError('Invalid divider')
    if not set(df.split.unique()).issubset({'train','test'}):raise ValueError('split must be train/test')
    df=df.copy();df['r_ohm']=resistance_from_adc(df)
    if not ((df.r_ohm>0)&np.isfinite(df.r_ohm)).all():raise ValueError('Invalid resistance inversion')
    out=[];scores=[]
    for sid,d in df.groupby('sensor_id'):
        tr=d[d.split=='train'];te=d[d.split=='test']
        if len(te)==0 or len(tr)<12:raise ValueError(f'Need train/test for sensor {sid}')
        fit=fit_one(tr);fit['sensor_id']=str(sid);out.append(fit)
        for split,subset in [('train',tr),('test',te)]:
            pr=predict_r(subset,fit)
            rel=abs(pr-subset.r_ohm.to_numpy(float))/subset.r_ohm.to_numpy(float)
            # nominal comparator assumes R10=25k, gamma=.6, optical exponent=1.0
            nominal=predict_r(subset,dict(r10_ohm=25000.,gamma=.60,angular_exponent=1.,temp_logR_per_C=None))
            rel_nom=abs(nominal-subset.r_ohm.to_numpy(float))/subset.r_ohm.to_numpy(float)
            scores.append(dict(sensor_id=str(sid),split=split,n=len(subset),
                model_median_relative_error_pct=float(100*np.median(rel)),
                model_p95_relative_error_pct=float(100*np.quantile(rel,.95)),
                nominal_p95_relative_error_pct=float(100*np.quantile(rel_nom,.95))))
    output=Path(output);output.mkdir(exist_ok=True,parents=True)
    pd.DataFrame(out).to_csv(output/'fitted_calibrations.csv',index=False)
    pd.DataFrame(scores).to_csv(output/'calibration_validation.csv',index=False)
    print(pd.DataFrame(scores).groupby('split')[['model_p95_relative_error_pct','nominal_p95_relative_error_pct']].mean().round(2))
    return pd.DataFrame(out),pd.DataFrame(scores)

def create_synthetic_example(path,seed=1337):
    rng=np.random.default_rng(seed);rows=[]
    for k in range(12):
        r10=rng.uniform(20000,30000);gamma=rng.uniform(.56,.64);p=rng.uniform(1.05,1.3);tcoef=rng.uniform(-.004,.004)
        for split,angles in [('train',[0,15,30,45,60,75]),('test',[7.5,22.5,37.5,52.5,67.5])]:
            for ang in angles:
                for lux in (10,20,50,100):
                    for temp in (-10,20,55):
                        # Synthetic response obeys exactly the fit family plus 1% random measurement noise.
                        R=r10*(lux/10)**(-gamma)*np.cos(np.deg2rad(ang))**(-gamma*p)*np.exp(tcoef*(temp-20))
                        R*=np.exp(rng.normal(0,.01))
                        v=5*R/(R+30000);ref=1.1 if v<.96 else 5.
                        adc=np.clip(round(v/ref*1023+rng.normal(0,.55)),2,1021)
                        rows.append(dict(sensor_id=k,lux=lux,angle_deg=ang,temp_c=temp,adc=adc,vref_v=ref,vcc_v=5.,rfixed_ohm=30000,split=split))
    pd.DataFrame(rows).to_csv(path,index=False)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--input');a.add_argument('--output',default='calibration_results');a.add_argument('--synthetic-example',action='store_true');args=a.parse_args()
    if args.synthetic_example:
        target=Path(args.output);target.mkdir(exist_ok=True,parents=True)
        create_synthetic_example(target/'SYNTHETIC_example_calibration.csv')
        validate_and_fit(target/'SYNTHETIC_example_calibration.csv',target)
    else:
        if not args.input:a.error('provide --input or --synthetic-example')
        validate_and_fit(args.input,args.output)
