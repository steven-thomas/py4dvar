"""
optic_code.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

def dxdt(rd,p,x):
    """Calculate gradients for OptIC model for single timestep
    input:
        rd: rainfall driver term (real)
        p: array of input parameters [pa1,pa2,pk1,pk2,ps0]
        x: array of current model states [xx1,xx2]
    output:
        dx: array of model state gradients"""
    pa1,pa2,pk1,pk2,ps0 = np.array(p, dtype=np.float64)
    xx1,xx2 = np.array(x, dtype=np.float64)
    dx1 = rd*(xx1/(pa1+xx1))*(xx2/(pa2+xx2)) - pk1*xx1 + ps0
    dx2 = pk1*xx1 - pk2*xx2
    return np.array([dx1,dx2])

def dxdt_AD(rd,p,p_AD,x,x_AD,dx_AD):
    """Adjoint of dxdt"""
    pa1,pa2,pk1,pk2,ps0 = np.array(p, dtype=np.float64)
    xx1,xx2 = np.array(x, dtype=np.float64)
    pa1_AD,pa2_AD,pk1_AD,pk2_AD,ps0_AD = np.array(p_AD, dtype=np.float64)
    xx1_AD,xx2_AD = np.array(x_AD, dtype=np.float64)
    dx1_AD,dx2_AD = np.array(dx_AD, dtype=np.float64)

    pk1_AD = pk1_AD + xx1 * dx2_AD
    pk2_AD = pk2_AD - xx2 * dx2_AD
    xx1_AD = xx1_AD + pk1 * dx2_AD
    xx2_AD = xx2_AD - pk2 * dx2_AD

    pa1_AD = pa1_AD - rd*(xx1/(pa1+xx1)**2)*(xx2/(pa2+xx2)) * dx1_AD
    pa2_AD = pa2_AD - rd*(xx1/(pa1+xx1))*(xx2/(pa2+xx2)**2) * dx1_AD
    pk1_AD = pk1_AD - xx1 * dx1_AD
    ps0_AD = ps0_AD + 1 * dx1_AD
    xx1_AD = xx1_AD + (rd*(pa1/(pa1+xx1)**2)*(xx2/(pa2+xx2)) - pk1) * dx1_AD
    xx2_AD = xx2_AD + rd*(xx1/(pa1+xx1))*(pa2/(pa2+xx2)**2) * dx1_AD

    p_AD = np.array([pa1_AD,pa2_AD,pk1_AD,pk2_AD,ps0_AD], dtype=np.float64)
    x_AD = np.array([xx1_AD,xx2_AD], dtype=np.float64)
    dx_AD = np.array([dx1_AD,dx2_AD], dtype=np.float64)
    return p_AD,x_AD


def optic_model(rd_arr, p, x, dt):
    """ forward model of OptIC
    input:
        rd: rainfall driver, real array
        p: parameters, array of [pa1,pa2,pk1,pk2,ps0]
        x: inital model state, array [xx1,xx2]
    output:
        x_out: model state for every timestep"""
    x_out = [np.array(x, dtype=np.float64)]
    for rd in rd_arr:
        x = x + dt*dxdt(rd,p,x)
        x_out.append(x)
    return np.array(x_out)

def optic_model_AD(rd_arr, p, x0, x_out_AD, dt):
    """Adjoint of forward model of OptIC"""
    #run OptIC forwards first
    x = x0
    x_out = np.zeros( (len(rd_arr)+1,len(x),), dtype=np.float64 )
    x_out[0,:] = x
    for i,rd in enumerate(rd_arr):
        x_next = x + dt*dxdt(rd,p,x)
        x_out[i+1,:] = x_next[:]
        x = x_next

    p_AD = np.zeros( p.shape, dtype=np.float64 )
    x_AD = np.zeros( x.shape, dtype=np.float64 )

    for i in range(rd_arr.size)[::-1]:
        rd = rd_arr[i]
        x = x_out[i,:]

        x_AD = x_AD + x_out_AD[i+1,:]
        dx_AD = dt*x_AD
        p_AD,x_AD = dxdt_AD(rd,p,p_AD,x,x_AD,dx_AD)

    x_AD = x_AD + x_out_AD[0,:]

    return p_AD, x_AD
