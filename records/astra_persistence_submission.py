"""Exact static reconstruction of selected evaluation32 from original.npz.
Usage: python build_selected.py /path/to/original.npz /path/to/output.npz
Only NumPy weight algebra; no model or layer forward calls.
The float32 operation order is deliberate and reproduces the archived arrays.
"""
import numpy as np
def build(r=.6,g=0,rate=3e-7,gate=500,threshold=1e-5,width=1e-5,gain=1000,carrier=.1,donors=(7,16,6),base_path='original.npz'):
 w=dict(np.load(base_path));p=np.zeros(16,dtype='float32');p[0]=r;p[1]=g
 for off in [0,16,32]:
  row=w['W1'][off+2].copy();w['W1'][off:off+16]+=p[:,None]*row;w['W1'][off+2]=0
 w['W2'][:,2]=r*w['W2'][:,0]+g*w['W2'][:,1];w['b2'][2]=r*w['b2'][0]+g*w['b2'][1]
 b=w['b2'].copy();q=-p;q[2]=1
 w['W1'][:16]+=gate*q[:,None]
 for j in donors:w['W1'][:,j]=0;w['b1'][j]=0;w['W2'][j]=0
 for j,bb,c in [(donors[0],-threshold,-gain),(donors[1],-threshold-width,gain+1)]:
  w['W1'][:16,j]=-q;w['b1'][j]=bb;w['W2'][j,2]=c
 j=donors[2];w['W1'][:16,j]=gate*q;w['b1'][j]=carrier;w['W2'][j]=b/carrier
 w['b2']*=0;w['b2'][2]=-rate
 return w


def build_selected(original_path):
    w=build(r=1,g=-.2,donors=(100,16,6),rate=2.5e-7,
            gain=250,width=(.01002-.00001)/251,base_path=original_path)
    w['W1'][3,6]+=.02
    w['b1'][6]-=.016
    return w

if __name__ == '__main__':
    import sys
    if len(sys.argv)!=3:
        raise SystemExit('Usage: python build_selected.py original.npz output.npz')
    np.savez(sys.argv[2],**build_selected(sys.argv[1]))
