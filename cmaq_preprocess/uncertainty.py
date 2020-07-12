"""
uncertainty.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

import fourdvar.util.netcdf_handle as ncf

def convert_unc( unc, val ):
    """
    convert the uncertainty object provided into a valid dictionary
    uncertainty object is either a string (filepath), dictionary (of spcs) or a scalar
    """
    spc_list = val.keys()
    arr_shape = val.values()[0].shape
    
    if str(unc) == unc:
        try:
            unc_var = ncf.get_variable( unc, spc_list )
        except:
            print 'uncertainty file is not valid'
            raise
        for spc in spc_list:
            arr = unc_var[ spc ]
            msg = 'unc file has data with wrong shape, needs {:}'.format( str(arr_shape) )
            assert arr.shape == arr_shape, msg
        unc_dict = { s:unc_var[s] for s in spc_list }
    elif type(unc) == dict:
        msg = 'uncertainty dictionary is missing needed spcs.'
        assert set( spc_list ).issubset( unc.keys() ), msg
        unc_dict = {}
        for spc in spc_list:
            val = unc[ spc ]
            unc_dict[ spc ] = np.zeros(arr_shape) + val
    else:
        try:
            val = float( unc )
        except:
            print 'invalid uncertainty parameter'
            raise
        unc_dict = { s:(np.zeros(arr_shape)+val) for s in spc_list }

    for spc in spc_list:
        arr = unc_dict.pop( spc )
        assert (arr > 0).all(), 'uncertainty values must be greater than 0.'
        unc_dict[ spc + '_UNC' ] = arr
    
    return unc_dict
