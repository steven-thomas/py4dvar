"""
application: produce model input from physical data (prior/background format)
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.ModelInputData ) == prepare_model( physical_instance )
"""
from __future__ import absolute_import

import numpy as np

from fourdvar.datadef import PhysicalData, ModelInputData
from fourdvar.params.input_defn import inc_icon
import fourdvar.params.template_defn as template
import fourdvar.util.cmaq_handle as cmaq
import fourdvar.util.date_handle as dt
import fourdvar.util.netcdf_handle as ncf

#value to convert units for each days emissions
unit_convert = None

def get_unit_convert():
    """
    extension: get unit conversion value
    input: None
    output: scalar
    
    notes: PhysicalData.emis units = mol/(s*m^2)
           ModelInputData.emis units = mol/s
    """
    fname = dt.replace_date( template.emis, dt.start_date )
    xcell = ncf.get_attr( fname, 'XCELL' )
    ycell = ncf.get_attr( fname, 'YCELL' )
    return  float(xcell*ycell)

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """
    global unit_convert
    if unit_convert is None:
        unit_convert = get_unit_convert()

    if inc_icon is True:
        model_input_args = { 'icon': {} }
        #physical icon has no time dim, model input icon has time dim of len 1
        for spcs, icon_array in physical_data.icon.items():
            model_input_args['icon'][spcs] = icon_array.reshape( (1,)+icon_array.shape )
    else:
        model_input_args = {}

    
    #all emis files & spcs for model_input use same NSTEP dimension, get it's size
    emis_fname = dt.replace_date( template.emis, dt.start_date )
    m_daysize = ncf.get_variable( emis_fname, physical_data.spcs[0] ).shape[0] - 1
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
        for spcs_name in physical_data.spcs:
            phys_data = physical_data.emis[ spcs_name ][ start:end, ... ]
            if end < physical_data.nstep:
                last_slice = physical_data.emis[ spcs_name ][ end:end+1, ... ]
            else:
                last_slice = physical_data.emis[ spcs_name ][ end-1:end, ... ]
            mod_data = np.repeat( phys_data, m_daysize // (end-start), axis=0 )
            mod_data = np.append( mod_data, last_slice, axis=0 )
            spcs_dict[ spcs_name ] = mod_data * unit_convert
        emis_argname = dt.replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout()
    
    return ModelInputData.create_new( **model_input_args )
