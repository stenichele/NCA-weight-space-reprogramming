"""Float32 standard NCA recurrence; loads weights published for Distill WebGL.

Unlike the WebGL runtime, intermediate activations are not texture-quantized,
and the finite grid uses zero padding, as in the original training notebook.
"""
import base64, json
from pathlib import Path
import numpy as np
from scipy.ndimage import maximum_filter

def decode(path):
    layers=json.loads(Path(path).read_text())
    result={}
    for i,layer in enumerate(layers,1):
        a=np.frombuffer(base64.b64decode(layer['data_b64']),np.uint8).reshape(layer['in_ch']+1,layer['out_ch']).astype(np.float32)/255-.5
        result[f'W{i}']=a[:-1]*layer['weight_scale']
        result[f'b{i}']=a[-1]*layer['bias_scale']
    return result

def seed(batch=1,size=65):
    x=np.zeros((batch,size,size,16),np.float32)
    x[:,size//2,size//2,3:]=1
    return x

def perceive(x):
    # Zero padding, cross-correlation Sobel, screen coordinates: x right, y down.
    p=np.pad(x,((0,0),(1,1),(1,1),(0,0)))
    dx=(p[:,:-2,2:]+2*p[:,1:-1,2:]+p[:,2:,2:]-p[:,:-2,:-2]-2*p[:,1:-1,:-2]-p[:,2:,:-2])/8
    dy=(p[:,2:,:-2]+2*p[:,2:,1:-1]+p[:,2:,2:]-p[:,:-2,:-2]-2*p[:,:-2,1:-1]-p[:,:-2,2:])/8
    return np.concatenate([x,dx,dy],axis=-1)

def alive(x):
    return maximum_filter(x[...,3],size=(1,3,3),mode='constant',cval=0)>=.1

def step(x,w,mask):
    pre=alive(x)
    h=np.maximum(perceive(x)@w['W1']+w['b1'],0)
    y=x+(h@w['W2']+w['b2'])*mask[...,None]
    return y*(pre & alive(y))[...,None]

def rgb(x):
    rgba=np.clip(x[...,:4],0,1)
    return np.clip(rgba[...,:3]+1-rgba[...,3:4],0,1)

def rollout(w,steps=1024,batch=4,size=65,rng_seed=20261103,capture=(64,96,128,192,256,512,1024),mask_transform=None):
    x=seed(batch,size); rng=np.random.default_rng(rng_seed); frames={0:x.copy()}
    for t in range(1,steps+1):
        mask=rng.random(x.shape[:-1])<.5
        if mask_transform is not None: mask=mask_transform(mask)
        x=step(x,w,mask)
        if t in capture: frames[t]=x.copy()
    return frames

if __name__=='__main__':
    root=Path(__file__).parent
    for path in (root/'originals').glob('*.json'):
        w=decode(path); np.savez(root/'originals'/f'{path.stem}.npz',**w)
