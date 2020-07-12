"""
make_emis_layers.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
from netCDF4 import Dataset

icon_file = 'test_icon.nc'
emis_file = 'test_emis.nc'
output_file = 'new_emis.nc'

with Dataset( icon_file, 'r' ) as f:
    vgtop = f.getncattr('VGTOP')
    vglvls = f.getncattr('VGLVLS')
    nlay = f.getncattr('NLAYS')
    assert f.dimensions['LAY'].size == nlay, 'wrong NLAY'

src = Dataset( emis_file, 'r' )
dst = Dataset( output_file, 'w' )

for dim_name, dim_obj in src.dimensions.items():
    if dim_name == 'LAY':
        dim_val = nlay
    else if dim_obj.isunlimited():
        dim_val = None
    else:
        dim_val = dim_obj.size
    dst.createDimension( dim_name, dim_val )

for var_name, var_obj in src.variables.items():
    var_dim = var_obj.dimensions 
    dst_var = dst.createVariable( var_name, var_obj.dtype, var_dim, zlib=True )
    if 'LAY' == var_dim[1]:
        dst_var[:,:1,:,:] = var_obj[:]
        dst_var[:,1:,:,:] = 0
    else:
        dst_var[:] = var_obj[:]
    for var_attr_name in var_obj.ncattrs():
        dst_var.setncattr( var_attr_name,
                           var_obj.getncattr( var_attr_name ) )

for attr_name in src.ncattrs():
    if attr_name == 'VGTOP':
        attr_val = vgtop
    elif attr_name == 'VGLVLS':
        attr_val = vglvls
    elif attr_name == 'NLAYS':
        attr_val = nlay
    else:
        attr_val = src.getncattr( attr_name )
    dst.setncattr( attr_name, attr_val )
