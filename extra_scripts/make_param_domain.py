
import numpy as np
from netCDF4 import Dataset

import context
from fourdvar.params.model_data import param_fname

nvars = 2
nparam = 4
nrows = 3
ncols = 4
nmodel = 1
var_name = ['Cab','Vcmo']
par_name = ['LAI','LIDFa','LIDFb','Rin']

par_arr = np.zeros((nparam,nrows,ncols))
par_arr[0,:,:] = [[2.31,  5.522, 6.1,   3.259],
                  [3.651, 3.375, 2.88,  3.2  ],
                  [5.597, 3.329, 1.681, 1.54 ]]
par_arr[1,:,:] = [[ 0.17,  -0.228, -0.18,  -0.175],
                  [-0.323,  0.622, -0.065, -0.369],
                  [-0.355, -0.005,  0.077,  0.209]]
par_arr[2,:,:] = [[ 0.384,  0.307, -0.51,  -0.367],
                  [ 0.102,  0.314, -0.202, -0.235],
                  [ 0.603, -0.26,   0.015, -0.127]]
par_arr[3,:,:] = [[648.057, 435.233, 353.445, 237.451],
                  [336.941, 575.686, 443.995, 385.393],
                  [653.627, 567.159, 603.635, 502.98 ]]

mod_arr = np.zeros((nrows,ncols)).astype(int)
"""
var_arr[0,:,:] = [[56.904 61.056 75.151 57.831]
 [75.371 24.195 80.602 43.727]
 [26.272 36.009 68.707 41.713]]
var_arr[1,:,:] = [[118.334 192.    138.107 108.996]
 [212.818  42.379 188.674  43.97 ]
 [218.546 146.975  93.499 165.763]]
"""
assert mod_arr.max() == (nmodel-1), 'nIndex does not match array'
with Dataset( param_fname, 'w' ) as f:
    f.createDimension('PARAM',nparam)
    f.createDimension('ROW',nrows)
    f.createDimension('COL',ncols)
    f.setncattr('NMODEL', nmodel)
    f.setncattr('PAR_LIST',par_name)
    mod_map = f.createVariable('MODEL_MAP','i4',('ROW','COL',))
    mod_map[:] = mod_arr[:]
    par_map = f.createVariable('PARAM_MAP','f4',('PARAM','ROW','COL',))
    par_map[:] = par_arr[:]
print( 'created param map', param_fname )
