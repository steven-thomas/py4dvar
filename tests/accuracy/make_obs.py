#temporary solution for testing purposes, needs to be generalized
#produce a resonable set of observations for given background

import numpy as np
import os

import _get_root
from fourdvar.user_driver import get_background
from fourdvar._transform import transform
import fourdvar.datadef as d
import fourdvar.util.file_handle as fh

savename = 'observed.csv'
sigma = 1.0

phys = get_background()
mod_in = transform( phys, d.ModelInputData )
mod_out = transform( mod_in, d.ModelOutputData )
obs = transform( mod_out, d.ObservationData )

val = obs.get_vector( 'value' )
time = obs.get_vector( 'time' )
kind = obs.get_vector( 'kind' )

fobj = open( os.path.join( fh.data_loc, savename ), 'w' )
fobj.write( 'value,time,kind\n' )
for v,t,k in zip( val, time, kind ):
    delta = np.random.normal( 0, sigma )
    #delta = 0.0
    fobj.write( '{},{},{}\n'.format( v+delta, t, k) )
fobj.close()

