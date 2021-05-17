
import numpy as np
from netCDF4 import Dataset

import context
from fourdvar.params.input_defn import prior_file

nvars = 2
nrows = 3
ncols = 4
var_name = ['Cab','Vcmo']

val_arr = np.zeros((nvars,nrows,ncols))
val_arr[0,:,:2] = 56.904
val_arr[0,:,2:] = 61.056
val_arr[1,0,:] = 118.334
val_arr[1,1,:] = 192.
val_arr[1,2,:] = 138.107

unc_arr = np.zeros((nvars,nrows,ncols))
unc_arr[0,:,:2] = 20.
unc_arr[0,:,2:] = 20.
unc_arr[1,0,:] = 50.
unc_arr[1,1,:] = 50.
unc_arr[1,2,:] = 50.

with Dataset( prior_file, 'w' ) as f:
    f.createDimension('VAR',nvars)
    f.createDimension('ROW',nrows)
    f.createDimension('COL',ncols)
    f.setncattr('VAR_LIST',var_name)
    val = f.createVariable('VALUE','f4',('VAR','ROW','COL',))
    val[:] = val_arr[:]
    unc = f.createVariable('UNCERTAINTY','f4',('VAR','ROW','COL',))
    unc[:] = unc_arr[:]
print( 'created prior', prior_file )
