
import numpy as np

import _get_root
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
            assert (arr > 0).all(), 'uncertainty values must be greater than 0.'
        unc_dict = { s:unc_var[s] for s in spc_list }
    elif type(unc) == dict:
        msg = 'uncertainty dictionary is missing needed spcs.'
        assert set( spc_list ).issubset( unc.keys() ), msg
        unc_dict = {}
        for spc in spc_list:
            val = unc[ spc ]
            assert val > 0, 'uncertainty values must be greater than 0.'
            unc_dict[ spc ] = np.zeros(arr_shape) + val
    else:
        try:
            val = float( unc )
        except:
            print 'invalid uncertainty parameter'
            raise
        assert val > 0, 'uncertainty values must be greater than 0.'
        unc_dict = { s:(np.zeros(arr_shape)+val) for s in spc_list }

    for spc in spc_list:
        arr = unc_dict.pop( spc )
        unc_dict[ spc + '_UNC' ] = arr
    
    return unc_dict
