"""AE4901 six-face, twelve-channel Sun-sensor geometry comparison.

Illustrative normalized irradiance model, NOT a calibrated GL5537-1 model.
Run: python ae4901_sun_geometry_simulation.py
Saves csv summary, per-direction npz, and figures in /mnt/data/ae4901_geometry_results.
"""
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path('/mnt/data/ae4901_geometry_results'); OUT.mkdir(exist_ok=True,parents=True)
RNG=np.random.default_rng(4901)
FACES=np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]], dtype=float)
FACES_NAMES=['+X','-X','+Y','-Y','+Z','-Z']

def fibonacci_sphere(k):
    i=np.arange(k,dtype=float)
    z=1-2*(i+0.5)/k
    theta=np.pi*(3-np.sqrt(5))*i
    r=np.sqrt(1-z*z)
    return np.column_stack([r*np.cos(theta),r*np.sin(theta),z])

SUN=np.vstack((fibonacci_sphere(30000), FACES, (FACES[[0,0,0,1,1,1]]+FACES[[2,4,3,2,4,5]])/np.sqrt(2)))
NUM=len(SUN)

def normalize_rows(x):
    return x/np.linalg.norm(x,axis=-1,keepdims=True)

def rodrigues(axis,theta):
    axis=np.asarray(axis,dtype=float); axis/=np.linalg.norm(axis)
    a,b,c=axis
    K=np.array([[0,-c,b],[c,0,-a],[-b,a,0]])
    return np.eye(3)+np.sin(theta)*K+(1-np.cos(theta))*(K@K)

def build_flat():
    return np.repeat(FACES,2,axis=0)

def build_dual_rotated():
    R=rodrigues([1,1,1], np.deg2rad(30))
    N=np.empty((12,3))
    for i,n in enumerate(FACES):
        N[i*2]=R@n
        N[i*2+1]=R.T@n
    return N

def build_icosa_candidates():
    phi=(1+np.sqrt(5))/2
    v=[]
    for a in (-1,1):
        for b in (-1,1):
            v.extend([[a*phi,0,b],[a,b*phi,0],[0,a,b*phi]])
    v=normalize_rows(np.array(v,dtype=float))
    groups=[]
    for face in FACES:
        scores=v@face
        ids=np.flatnonzero(np.isclose(scores, np.max(scores)))
        assert len(ids)==2
        groups.append(v[ids])
    return groups

def build_ico(bits, groups):
    n=np.empty((12,3))
    for i,bit in enumerate(bits):
        n[2*i]=groups[i][bit]
        n[2*i+1]=groups[i][1-bit]
    return n

def compute_gram(sun, N, threshold, indices=None):
    if indices is None: indices=np.arange(12)
    M=N[indices]
    mu=sun@M.T
    mask=mu>threshold
    gram=np.einsum('bi,ij,ik->bjk',mask.astype(float),M,M,optimize=True)
    vals=np.linalg.eigvalsh(gram)
    valid=vals[:,0]>1e-7
    cond=np.full(len(sun),np.inf)
    cond[valid]=np.sqrt(vals[valid,-1]/vals[valid,0])
    return valid,cond,mask.sum(axis=1)

def best_ico_split(groups):
    # Choose the pair-to-board mapping based on ability of each *individual* board
    # to reconstruct a direction when only high-signal measurements are considered.
    test=fibonacci_sphere(3000)
    choices=[]
    for bits in itertools.product((0,1),repeat=6):
        N=build_ico(bits,groups)
        a=compute_gram(test,N,0.05,np.arange(0,12,2))
        b=compute_gram(test,N,0.05,np.arange(1,12,2))
        validity=min(a[0].mean(),b[0].mean())
        # Penalize both non-valid configurations and poor conditioning
        finite=np.hstack([a[1][a[0]],b[1][b[0]]])
        p95=np.quantile(finite,0.95) if len(finite) else 1e6
        choices.append((validity,-p95,bits))
    chosen=max(choices,key=lambda a:(a[0],a[1]))
    return build_ico(chosen[2],groups),chosen

ICO,ICO_SPLIT=best_ico_split(build_icosa_candidates())
DESIGNS={'Flat, duplicated':build_flat(), 'Icosahedral, split-optimized':ICO,'Dual rotated cubes (±30°)':build_dual_rotated()}

def estimate(N, sun, threshold, sigma, drop=None, rng=None, power=1.0):
    if rng is None: rng=RNG
    illumination=np.maximum(0,sun@N.T)
    y=illumination**power
    if sigma: y+=rng.normal(0,sigma,y.shape)
    y=np.maximum(y,0)
    if drop is not None:
        if isinstance(drop,str):
            if drop=='A': y[:,::2]=0
            if drop=='B': y[:,1::2]=0
            if drop=='one_random': y[np.arange(len(y)),rng.integers(0,12,len(y))]=0
        else:
            y[:,drop]=0
    mask=y>threshold
    H=np.einsum('bi,ij,ik->bjk',mask.astype(float),N,N,optimize=True)
    # rank condition is strict: a numerical three-dimensional solution must exist.
    eig=np.linalg.eigvalsh(H)
    valid=eig[:,0]>1e-7
    rhs=(y*mask)@N
    q=np.zeros((len(sun),3))
    if valid.any(): q[valid]=np.linalg.solve(H[valid],rhs[valid,:,None])[...,0]
    qmag=np.linalg.norm(q,axis=1)
    valid&=qmag>1e-8
    qhat=np.zeros_like(q)
    qhat[valid]=q[valid]/qmag[valid,None]
    cos=np.clip(np.einsum('ij,ij->i',qhat,sun),-1,1)
    err=np.degrees(np.arccos(cos))
    err[~valid]=np.nan
    return valid,err,mask.sum(axis=1)

rows=[]; directions={}
for name,N in DESIGNS.items():
    # Condition theorem / symmetry diagnostic
    sym=np.linalg.eigvalsh(N.T@N)
    s={'design':name,'N.TN eigenvalues':','.join(f'{x:.3f}' for x in sym)}
    # Geometry-only conditional rank measure based on ideal illuminated channels.
    for threshold in (0.01,0.05,0.10):
        full,cond,counts=compute_gram(SUN,N,threshold)
        s[f'geometric full-rank at {threshold:.0%} threshold (%)']=round(100*full.mean(),2)
        s[f'median channels above {threshold:.0%} threshold']=round(float(np.median(counts)),1)
        if threshold==0.05:
            s['geometry median condition | valid']=round(float(np.median(cond[full])),3)
            s['geometry p95 condition | valid']=round(float(np.quantile(cond[full],.95)),3)
        for grp,ix in (('A',np.arange(0,12,2)),('B',np.arange(1,12,2))):
            if threshold==0.05:
                vb,cb,_=compute_gram(SUN,N,threshold,ix)
                s[f'board {grp} full-rank at 5% (%)']=round(100*vb.mean(),2)
                s[f'board {grp} p95 condition | valid']=round(float(np.quantile(cb[vb],.95)),3) if vb.any() else np.nan
    for test,noise,threshold,drop,power in [
        ('ideal 1% threshold',0,0.01,None,1.),
        ('noise 1%, threshold 5%',0.01,0.05,None,1.),
        ('noise 1%, threshold 1%',0.01,0.01,None,1.),
        ('noise 1%, threshold 10%',0.01,0.1,None,1.),
        ('noise 1%, threshold 5%, random sensor dead',0.01,0.05,'one_random',1.),
        ('noise 1%, threshold 5%, board A dead',0.01,0.05,'A',1.),
        ('noise 1%, threshold 5%, board B dead',0.01,0.05,'B',1.),
        ('cos^1.3 mismatch, threshold 5%',0.0,0.05,None,1.3),
    ]:
        seed=4910+int(100*noise)+int(100*threshold)+sum(ord(x) for x in test)
        v,e,c=estimate(N,SUN,threshold,noise,drop,np.random.default_rng(seed),power)
        s[f'{test}: valid (%)']=round(100*v.mean(),2)
        s[f'{test}: median error (deg)']=round(float(np.nanmedian(e)),3) if v.any() else np.nan
        s[f'{test}: p95 error (deg)']=round(float(np.nanquantile(e,.95)),3) if v.any() else np.nan
        if test=='noise 1%, threshold 5%': directions[name]={'sun':SUN,'err':e,'valid':v,'count':c}
    rows.append(s)

df=pd.DataFrame(rows).set_index('design').T
df.to_csv(OUT/'comparison_metrics.csv')
np.savez_compressed(OUT/'directional_results.npz',**{f'{key}__{suffix}':v for key,obj in directions.items() for suffix,v in obj.items()})
print('ICO split',ICO_SPLIT)
print('ALL SENSOR NORMALS PER FACE, A then B:')
for name,N in DESIGNS.items():
    print('\n',name)
    for i,face in enumerate(FACES_NAMES):
        print(face, 'A',np.round(N[2*i],4), 'B',np.round(N[2*i+1],4))
print('\nMETRICS:')
with pd.option_context('display.max_rows',200,'display.max_columns',6,'display.width',240):
    print(df.to_string())

# Figure 1: concise summary: bar fractions and angular errors conditional on valid results.
fig,ax=plt.subplots(1,3,figsize=(14,4.4),layout='constrained')
labels=['Flat\n12 sensors','Icosahedral\n12 sensors','Dual rotated\n12 sensors']
xs=np.arange(3)
colors=['#5C6E80','#C18B4B','#357F82']
metric='geometric full-rank at 5% threshold (%)'
ax[0].bar(xs,[df.loc[metric,n] for n in DESIGNS],color=colors)
ax[0].set_title('Observable directions, all channels')
ax[0].set_ylabel('Full-rank orientations (%)')
ax[0].set_ylim(0,105)
for j,n in enumerate(DESIGNS):ax[0].text(j,float(df.loc[metric,n])+1,f'{df.loc[metric,n]:.1f}%',ha='center',fontsize=9)
metric='noise 1%, threshold 5%: p95 error (deg)'
ax[1].bar(xs,[df.loc[metric,n] for n in DESIGNS],color=colors)
ax[1].set_title('p95 error among valid directions')
ax[1].set_ylabel('Angular error (degrees)')
metric='noise 1%, threshold 5%, board A dead: valid (%)'
ax[2].bar(xs,[df.loc[metric,n] for n in DESIGNS],color=colors)
ax[2].set_title('Recoverability: board A offline')
ax[2].set_ylabel('Full-rank orientations (%)')
ax[2].set_ylim(0,105)
for j,n in enumerate(DESIGNS):ax[2].text(j,float(df.loc[metric,n])+1,f'{df.loc[metric,n]:.1f}%',ha='center',fontsize=9)
for a in ax:a.set_xticks(xs,labels);a.spines[['top','right']].set_visible(False)
fig.suptitle('Ideal cosine LDR-equivalent simulation • 30,018 Sun directions • 5% threshold • 1% additive noise',fontsize=12)
fig.savefig(OUT/'geometry_comparison.png',dpi=180)
plt.close(fig)

# second figure: plotting the 12 sensor-normal directions in a simple 3D scatter.
fig=plt.figure(figsize=(13,4.4),layout='constrained')
for j,(name,N) in enumerate(DESIGNS.items(),start=1):
    ax=fig.add_subplot(1,3,j,projection='3d')
    for k in range(12):
        ax.plot([0,N[k,0]],[0,N[k,1]],[0,N[k,2]],c=colors[j-1],lw=1.4)
        ax.scatter(N[k,0],N[k,1],N[k,2],c=('#19283B' if k%2==0 else '#C9803C'),s=20)
    ax.set(xlim=(-1,1),ylim=(-1,1),zlim=(-1,1),xlabel='X',ylabel='Y',zlabel='Z')
    ax.set_title(name,fontsize=10)
    ax.set_box_aspect([1,1,1])
fig.suptitle('Sensor optical-axis directions (dark = board A; orange = board B)')
fig.savefig(OUT/'sensor_normal_directions.png',dpi=180)
plt.close(fig)

# concise human-readable record, assumptions and methodology
(OUT/'README.txt').write_text('''AE4901 sun-sensor geometries: reproducible preliminary simulation\n\nGEOMETRY\nFlat: two sensors normal to each of six cube faces.\nIcosahedral: 12 unit directions of a regular icosahedron; two assigned to each nearest cube face.\nDual rotated cubes: two independent ±XYZ sensor sets, each rotated 30 deg about the [1,1,1] body diagonal in opposite directions. Each mounted optical axis tilts approximately 24.4 deg from its physical face normal.\n\nMODEL\nI_i = max(0, n_i dot s), normalized face-on intensity = 1.\nOptional additive i.i.d. Gaussian noise sigma=0.01, clipped at zero. A sensor is INCLUDED in the fit when output > 0.05 (other threshold sweeps included). Estimate sun vector using ordinary least squares over included channels, with unknown common illumination scale and three vector components. No estimate is declared when the 3x3 normal-equation matrix is rank-deficient. Report angular error only for valid estimates; valid fraction separately.\n30,000 nearly-uniform Fibonacci directions plus 18 axes/edge directions. Reproducible random seeds.\n\nLIMITATIONS\nNo actual GL5537-1 angular response, resistance-light relationship, ADC quantization, lamp spectral characteristics, optical occlusion, mounted faces shadowing, per-channel calibration errors, albedo, or real thermal effects. These must be measured. 'Cos^1.3 mismatch' is a hypothetical model-error stress test, not a measured GL5537-1 exponent.\nSome icosahedral face-to-MCU assignments are poor under one-board failure; assignments evaluated by enumerating all 64 possible pair splits with a 5% threshold.\nSimulated angular error is conditional on valid orientations. Full rank of idealized positive measurements is stricter than a proper censored or Bayesian estimator using darkness information.\nThe dual rotated cube design is a proposed architecture, not a literature-validated optimal geometry.\n''')

# Sensitivity to dual-cube relative rotation about [1,1,1]; not an optimization
# of the actual GL5537-1 sensor because its angular response is unknown.
sweep=[]
for rot in range(0,61,5):
    RR=rodrigues([1,1,1],np.deg2rad(rot))
    N=np.empty((12,3))
    for k,f in enumerate(FACES):
        N[2*k]=RR@f;N[2*k+1]=RR.T@f
    tilt=np.degrees(np.arccos(np.clip(N[0]@FACES[0],-1,1)))
    va,_,_=compute_gram(SUN,N,0.05)
    vA,_,_=compute_gram(SUN,N,0.05,np.arange(0,12,2))
    vB,_,_=compute_gram(SUN,N,0.05,np.arange(1,12,2))
    noisy,err,_=estimate(N,SUN,0.05,0.01,rng=np.random.default_rng(1987))
    mis,miserr,_=estimate(N,SUN,0.05,0,rng=np.random.default_rng(1987),power=1.3)
    sweep.append(dict(rotation_deg=rot,face_tilt_deg=tilt,
        both_boards_geom_valid_pct=va.mean()*100,
        board_A_geom_valid_pct=vA.mean()*100,
        board_B_geom_valid_pct=vB.mean()*100,
        noisy_valid_pct=noisy.mean()*100,
        noisy_p95_error_deg=np.nanquantile(err,.95),
        hypothetical_power_mismatch_valid_pct=mis.mean()*100,
        hypothetical_power_mismatch_p95_error_deg=np.nanquantile(miserr,.95)))
sweep=pd.DataFrame(sweep)
sweep.to_csv(OUT/'rotated_geometry_angle_sweep.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(11,4.4),layout='constrained')
axs[0].plot(sweep.face_tilt_deg,sweep.both_boards_geom_valid_pct,'o-',label='Both boards')
axs[0].plot(sweep.face_tilt_deg,sweep.board_A_geom_valid_pct,'o--',label='One board')
axs[0].set(xlabel='Each sensor tilt from its face normal (deg)',ylabel='Full-rank directions (%)',ylim=(65,102),title='Directional coverage above a 5% threshold')
axs[0].legend(fontsize=8)
axs[1].plot(sweep.face_tilt_deg,sweep.noisy_p95_error_deg,'o-',label='Ideal cosine + 1% noise')
axs[1].plot(sweep.face_tilt_deg,sweep.hypothetical_power_mismatch_p95_error_deg,'o--',label='Hypothetical cos^1.3 model mismatch')
axs[1].set(xlabel='Each sensor tilt from its face normal (deg)',ylabel='p95 angular error, valid directions (deg)',title='Accuracy depends on response assumptions')
axs[1].legend(fontsize=8)
for ax in axs:ax.spines[['top','right']].set_visible(False)
fig.suptitle('Tilt sensitivity • 12 channels • three-vector least squares • illustrative optical model')
fig.savefig(OUT/'angle_sweep.png',dpi=180)
plt.close(fig)
print('\nROTATED GEOMETRY ANGLE SWEEP')
print(sweep.round(2).to_string(index=False))
