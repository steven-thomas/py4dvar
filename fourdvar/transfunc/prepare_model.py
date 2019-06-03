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
        for spcs, icon_scale in physical_data.icon.items():
            icon_array = ncf.get_variable( template.icon, spcs )
            #ModelInput adds array values to template, change icon_scale accordingly
            model_input_args['icon'][spcs] = (icon_scale-1.)*icon_array
    else:
        model_input_args = {}
    
    # work with emis timesteps in seconds
    daysec = 24*60*60
    emis_fname = dt.replace_date( template.emis, dt.start_date )
    t = int( ncf.get_attr( emis_fname, 'TSTEP' ) )
    m_tstep = 3600*( t//10000 ) + 60*( (t//100) % 100 ) + ( t%100 )

    p_tstep = physical_data.tstep
    msg = 'physical & model input emis TSTEP incompatible.'
    assert all([ t % m_tstep == 0 for t in p_tstep ]), msg

    e_count = [ p//m_tstep for p in p_tstep ] #emis count per phys timestep
    t = 0 #current phys time index
    m_len = daysec // m_tstep #No. emis steps per model day
    emis_pattern = 'emis.<YYYYMMDD>'
    for date in dt.get_datelist():
        p_ind = [] #time index of phys data
        p_rep = [] #No. repeats of phys index above (for today)
        r = 0
        #drain phys reps until a full day is filled, record which index's used
        while r < m_len:
            p_ind.append( t )
            p_rep.append( min(e_count[t],m_len) )
            r += p_rep[-1]
            e_count[t] -= p_rep[-1]
            if e_count[t] <= 0:
                t += 1
        #handle final timestep, repeat of next day OR last phys tstep
        if (t == len(e_count)) or (e_count[t] > 0):
            p_rep[-1] += 1
        else:
            p_ind.append( t )
            p_rep.append( 1 )
        #check index & rep
        assert (np.diff( p_ind ) == 1).all(), 'index out of alignment'
        assert sum( p_rep ) == ( m_len+1 ), 'reps do not sum to emis requirements'

        #build days emis spcs dict from phys
        spcs_dict = {}
        for spc in physical_data.spcs:
            start = p_ind[0]
            end = p_ind[-1] + 1
            phys_data = physical_data.emis[spc][ start:end, ... ]
            mod_data = np.repeat( phys_data, p_rep, axis=0 )
            spcs_dict[ spc ] = mod_data * unit_convert
        # attach species dict to model input args
        emis_argname = dt.replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout_fwd()
    
    return ModelInputData.create_new( **model_input_args )
