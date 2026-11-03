"""Independent evaluation of the seven archived edits. See ../README.txt."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('VECLIB_MAXIMUM_THREADS','1')
import argparse,json
from pathlib import Path
import numpy as np
from nca import rollout,rgb
from edits import edits
from persistence import build_selected
ROOT=Path(__file__).resolve().parents[1]
def metrics(a,b):
    am=a[...,3]>.1; bm=b[...,3]>.1
    union=am|bm; inter=am&bm
    count=union.sum(axis=(1,2))
    iou=inter.sum(axis=(1,2))/np.maximum(count,1)
    err=((rgb(a)-rgb(b))**2).sum(axis=-1)
    rmse=np.sqrt((err*union).sum(axis=(1,2))/np.maximum(3*count,1))
    mass=np.clip(a[...,3],0,1).sum(axis=(1,2))/np.maximum(np.clip(b[...,3],0,1).sum(axis=(1,2)),1e-8)
    return {'iou':iou.tolist(),'foreground_rgb_rmse':rmse.tolist(),'alpha_mass_ratio':mass.tolist()}

def maturity(frames,ref):
    result=[None]*len(ref)
    for t in range(8,257,8):
        m=metrics(frames[t],ref)
        for b in range(len(ref)):
            if result[b] is None and m['iou'][b]>=.85 and m['foreground_rgb_rmse'][b]<=.15: result[b]=t
    return result

def transform(x,name):
    if name=='blue': return x[...,[0,2,1,3,*range(4,16)]]
    if name=='swap_red_green': return x[...,[1,0,2,3,*range(4,16)]]
    if name=='mirror_horizontal': return x[:,:,::-1,:]
    if name=='rotate_90_clockwise': return np.rot90(x,k=-1,axes=(1,2))
    if name=='rotate_180': return np.rot90(x,k=2,axes=(1,2))
    return x

def mask_transform(name):
    if name=='mirror_horizontal': return lambda m:m[:,:,::-1]
    if name=='rotate_90_clockwise': return lambda m:np.rot90(m,k=-1,axes=(1,2))
    if name=='rotate_180': return lambda m:np.rot90(m,k=2,axes=(1,2))
    return None


def main():
    p=argparse.ArgumentParser();p.add_argument('--experiment',choices=['check','symmetry','speed','persistence','all'],default='check');p.add_argument('--output',default='reproduced.json');a=p.parse_args()
    weights={f.stem:dict(np.load(f)) for f in (ROOT/'weights').glob('*.npz')};w=weights['original'];result={}
    rebuilt=edits(w);rebuilt['persistence']=build_selected(ROOT/'weights/original.npz')
    for n,v in rebuilt.items():
        assert all(np.array_equal(v[k],weights[n][k]) for k in v),n
    result['checkpoint_reconstruction']='All seven edits match the archived arrays exactly.'
    if a.experiment in ['symmetry','speed','all']:
        ts=range(8,257,8);base=rollout(w,steps=256,batch=8,capture=ts)
        if a.experiment in ['symmetry','all']:
            result['symmetry']={}
            for n in ['blue','swap_red_green','mirror_horizontal','rotate_90_clockwise','rotate_180']:
                frames=rollout(weights[n],steps=128,batch=8,capture=[96,128],mask_transform=mask_transform(n))
                independent=rollout(weights[n],steps=128,batch=8,capture=[96,128],rng_seed=20261104)
                result['symmetry'][n]={'matched':{str(t):metrics(frames[t],transform(base[t],n)) for t in [96,128]},'max_state_error_t128':float(np.max(np.abs(frames[128]-transform(base[128],n)))),'independent':{str(t):metrics(independent[t],transform(base[t],n)) for t in [96,128]}}
                print(n,'complete',flush=True)
        if a.experiment in ['speed','all']:
            frames=rollout(weights['grow_half_speed'],steps=256,batch=8,capture=ts)
            result['speed']={'original_maturity':maturity(base,base[96]),'edited_maturity':maturity(frames,base[96]),'metrics':{str(t):metrics(frames[t],base[96]) for t in ts}}
    if a.experiment in ['persistence','all']:
        checkpoints=[256,512,1024,2048,3072,4096,6144,8192];ts=sorted(set(range(8,257,8))|set(checkpoints));result['persistence']={}
        ref=rollout(w,steps=96,batch=8,rng_seed=73510991,capture=[96])[96]
        for n in ['original','persistence','trained_control']:
            frames=rollout(weights[n],steps=8192,batch=8,rng_seed=73510991,capture=ts)
            ms={str(t):metrics(frames[t],ref) for t in ts};mat=maturity(frames,ref);ok=np.array([t is not None for t in mat])
            for t in checkpoints:
                v=ms[str(t)];ok&=(np.array(v['iou'])>=.8)&(np.array(v['foreground_rgb_rmse'])<=.15)&(np.array(v['alpha_mass_ratio'])>=.8)&(np.array(v['alpha_mass_ratio'])<=1.2)
            result['persistence'][n]={'maturity_times':mat,'pass_runs':int(ok.sum()),'metrics':ms}
            print(n,'complete',flush=True)
    Path(a.output).write_text(json.dumps(result,indent=2));print(result['checkpoint_reconstruction'])
if __name__=='__main__':main()
