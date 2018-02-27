"""
application: produce model input from physical data (prior/background format)
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.ModelInputData ) == prepare_model( physical_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, ModelInputData
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.cmaq_handle as cmaq
from fourdvar.params.input_defn import inc_icon

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """
    
    if inc_icon is True:
        model_input_args = { 'icon': {} }
        #physical icon has no time dim, model input icon has time dim of len 1
        for spcs, icon_array in physical_data.icon.items():
            model_input_args['icon'][spcs] = icon_array.reshape( (1,)+icon_array.shape )
    else:
        model_input_args = {}

    
    #all emis files & spcs for model_input use same NSTEP dimension, get it's size
    emis_fname = dt.replace_date( template.emis, dt.start_date )
    m_daysize = ncf.get_variable( emis_fname, physical_data.spcs_out[0] ).shape[0] - 1
    dlist = dt.get_datelist()
    p_daysize = float(physical_data.nstep) / len( dlist )
    assert (p_daysize < 1) or (m_daysize % p_daysize == 0), 'physical & model input emis TSTEP incompatible.'
    
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( dlist ):
        spcs_dict = {}
        start = int(i * p_daysize)
        end = int( (i+1) * p_daysize )
        if start == end:
            end += 1
        spcs_pair_list = zip( physical_data.spcs_out, physical_data.spcs_in )
        for spc_out, spc_in in spcs_pair_list:
            fname = dt.replace_date( template.emis, date )
            in_arr = ncf.get_variable( fname, spc_in )
            phys_data = physical_data.emis[ spc_out ][ start:end, ... ]
            if end < physical_data.nstep:
                last_slice = physical_data.emis[ spc_out ][ end:end+1, ... ]
            else:
                last_slice = physical_data.emis[ spc_out ][ end-1:end, ... ]
            prop_data = np.repeat( phys_data, m_daysize // (end-start), axis=0 )
            prop_data = np.append( prop_data, last_slice ), axis=0 )
            spcs_dict[ spcs_name ] = prop_data * in_arr
        
        emis_argname = dt.replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout()
    
    return ModelInputData.create_new( **model_input_args )
