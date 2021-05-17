
import numpy as np
from netCDF4 import Dataset

import context
from fourdvar.params.model_data import index_fname

nvars = 2
nrows = 3
ncols = 4
nindex = 5
var_name = ['Cab','Vcmo']

arr = np.zeros((nvars,nrows,ncols)).astype(int)
arr[0,:,:2] = 0
arr[0,:,2:] = 1
arr[1,0,:] = 2
arr[1,1,:] = 3
arr[1,2,:] = 4


assert arr.max() == (nindex-1), 'nIndex does not match array'
with Dataset( index_fname, 'w' ) as f:
    f.createDimension('VAR',nvars)
    f.createDimension('ROW',nrows)
    f.createDimension('COL',ncols)
    f.setncattr('NINDEX', nindex)
    f.setncattr('VAR_LIST',var_name)
    ind_map = f.createVariable('INDEX_MAP','i4',('VAR','ROW','COL',))
    ind_map[:] = arr[:]
print( 'created index map', index_fname )
