#!/apps/python/2.7.6/bin/python
#PBS -l wd
#PBS -l ncpus=16
#PBS -l mem=8gb
#PBS -q normal

import os
import numpy as np

rundir = '/home/563/spt563/fourdvar/cmaq_vsn1/tests'
os.chdir( rundir )

import _get_root
import fourdvar.datadef as d
import fourdvar.user_driver as user
import fourdvar._main_driver as main
from fourdvar._transform import transform

user.setup()
bg_phys = user.get_background()
bg_unk = transform( bg_phys, d.UnknownData )
bg_vec = np.array( bg_unk.get_vector() )
start_vec = np.zeros( bg_vec.size )
min_out = user.minim( main.cost_func,
                      main.gradient_func,
                      start_vec )
out_vec = min_out[0]
out_unk = d.UnknownData( out_vec )
out_phys = transform( out_unk, d.PhysicalData )
user.post_process( out_phys, min_output[1:] )
user.cleanup()
