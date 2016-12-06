"""
application: produce model input from physical data (prior/background format)
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.ModelInputData ) == prepare_model( physical_instance )
"""

import numpy as np
import datetime as dt

import _get_root
from fourdvar.datadef import PhysicalData, ModelInputData
from fourdvar.util.date_handle import replace_date
import fourdvar.util.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.global_config as global_config
import fourdvar.libshare.cmaq_handle as cmaq

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """
    
    model_input_args = { 'icon': {} }
    #physical icon had no time dimensions, model input icon has time dimension of len 1
    for spcs, icon_array in physical_data.icon.items():
        model_input_args['icon'][spcs] = icon_array.reshape( (1,)+icon_array.shape )
    
    #all emis files & spcs for model_input use same NSTEP dimension, get it's size
    m_daysize = ncf.get_variable( template.emis, physical_data.spcs[0] ).shape[0]
    dlist = global_config.get_datelist()
    p_daysize = physical_data.nstep // len( dlist )
    assert m_daysize % p_daysize == 0, 'physical & model input emis TSTEP incompatible.'
    
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( dlist ):
        spcs_dict = {}
        start = i * p_daysize
        end = (i+1) * p_daysize
        for spcs_name in physical_data.spcs:
            phys_data = physical_data.emis[ spcs_name ][ start:end, :, :, : ]
            mod_data = np.repeat( phys_data, m_daysize // p_daysize, axis=0 )
            spcs_dict[ spcs_name ] = mod_data
        emis_argname = replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout()
    
    return ModelInputData( **model_input_args )

