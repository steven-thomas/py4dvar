
import numpy as np
from netCDF4 import Dataset

src_file = 'prior.nc'
dst_file = 'CO2_unc.nc'

#set CO2 emission uncertainties to:
# 30% of emission value for background cells
# 10% of emission value for power plant spike, at 72:75,28:31
# floored at 1e-6

bg_scale = 0.3 #background uncertainty scale
pp_scale = 0.1 #power plant uncertainty scale
floor_val = 1e-6 # minimum uncertainty value

with Dataset( src_file, 'r' ) as f:
    val_arr = f.groups['emis'].variables['CO2'][:]

cat,step,lay,row,col = val_arr.shape

unc_arr = bg_scale * abs(val_arr.copy())
unc_arr[:,:,0,72:75,28:31] = pp_scale * abs(val_arr[:,:,0,72:75,28:31].copy())
unc_arr[ unc_arr < floor_val ] = floor_val

with Dataset( dst_file, 'w' ) as f:
    f.createDimension('CAT',cat)
    f.createDimension('STEP',step)
    f.createDimension('LAY',lay)
    f.createDimension('ROW',row)
    f.createDimension('COL',col)
    var = f.createVariable('CO2','f4',('CAT','STEP','LAY','ROW','COL',))
    var[:] = unc_arr[:]