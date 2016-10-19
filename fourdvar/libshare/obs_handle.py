"""
extension: functions used by the obs_operator and make_forcing transforms
contains the original and adjoint function for every kind of observation
functions are saved to maps obsop_map & mkfrc_map for easy importing/referencing

for every original function:
    input: x - the state of the model at the time of observation.
    output: obs_val - the value of the simulated observation

for every adjoint function:
    input: x - the state of the model at the time of observation.
           val - the value of the weighted residual of the observation.
    output: sparse - a dictionary to simulate a sparse matrix of adjoint forcing values

The tangent linear functions are not used.
"""
import numpy as np

import _get_root
from fourdvar.util.dim_defn import nstep

def first( x ):
    return x[0]
def first_tl( x, x_tl ):
    return { 0:x_tl[0] }
def first_ad( x, val ):
    return { 0:val }

def second( x ):
    return x[1]
def second_tl( x, x_tl ):
    return { 1:x_tl[1] }
def second_ad( x, val ):
    return { 1:val }

def third( x ):
    return x[2]
def third_tl( x, x_tl ):
    return { 2:x_tl[2] }
def third_ad( x, val ):
    return { 2:val }

def squarefirst( x ):
    return x[0]**2
def squarefirst_tl( x, x_tl ):
    return { 0:2.0*x[0]*x_tl[0] }
def squarefirst_ad( x, val ):
    return { 0:2.0*x[0]*val }

def firstbysecond( x ):
    return x[0]*x[1]
def firstbysecond_tl( x, x_tl ):
    return { 0:x[1]*x_tl[0], 1:x[0]*x_tl[1] }
def firstbysecond_ad( x, val ):
    return { 0:x[1]*val, 1:x[0]*val }

def sumall( x ):
    return x.sum()
def sumall_tl( x, x_tl ):
    return { i:x_tl[i] for i,v in enumerate( x ) }
def sumall_ad( x, val ):
    return { i:val for i,v in enumerate( x ) }


obsop_map = { 0:first, 1:second, 2:third, 3:squarefirst, 4:firstbysecond, 5:sumall }
mkfrc_map = { 0:first_ad, 1:second_ad, 2:third_ad, 3:squarefirst_ad, 4:firstbysecond_ad, 5:sumall_ad }

