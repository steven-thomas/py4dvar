#lorenz 63 model and adjoint code

import numpy as np

import _get_root
from fourdvar.util.dim_defn import dt, nstep, x_len

#refer params
traj_file = 'xtraj_file.array'

#local params
p = 10.0
r = 28.0
b = 8.0/3.0

#ORIGINAL
def model( xin ):
    x = xin.copy()
    xtraj = np.zeros(( x_len, nstep+1 ))
    for j in range(nstep):
        xtraj[ :, j ] = x.copy()
        dxdt = lorenz( x )
        x = x + dt*dxdt #step
    xtraj[ :, nstep ] = x.copy()
    return xtraj

#ADJOINT
def model_ad( xtraj, xfrc ):
    x_ad = np.zeros( x_len )
    for j in range( nstep, 0, -1 ):
        x_ad = x_ad + xfrc[ :, j ]
        dxdt_ad = dt*x_ad #step_ad
        x_ad = lorenz_ad( xtraj[ :, j ], x_ad, dxdt_ad )
    return x_ad

def lorenz( x ):
    assert x_len == 3, 'lorenz 63 only works for x_len == 3'
    dxdt = np.zeros( 3 )
    dxdt[0] = -p*x[0] + p*x[1]
    dxdt[1] = x[0] * (r - x[2]) - x[1]
    dxdt[2] = x[0]*x[1] - b*x[2]
    return dxdt

def lorenz_ad( x, x_adin, dxdt_ad ):
    assert x_len == 3, 'lorenz 63 only works for x_len == 3'
    x_ad = x_adin.copy()
    x_ad[0] = x_ad[0] - p*dxdt_ad[0] + (r-x[2])*dxdt_ad[1] + x[1]*dxdt_ad[2]
    x_ad[1] = x_ad[1] + p*dxdt_ad[0] - dxdt_ad[1] + x[0]*dxdt_ad[2]
    x_ad[2] = x_ad[2] - x[0]*dxdt_ad[1] - b*dxdt_ad[2]
    return x_ad

