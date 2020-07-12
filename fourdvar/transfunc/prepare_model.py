"""
prepare_model.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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
unit_key = 'units.<YYYYMMDD>'
unit_convert_emis = None
unit_convert_bcon = None

def get_unit_convert_emis():
    """
    extension: get unit conversion value
    input: None
    output: scalar
    
    notes: PhysicalData.emis units = mol/(s*m^2)
           ModelInputData.emis units = mol/s
    """
    global unit_key
    
    fname = dt.replace_date( template.emis, dt.start_date )
    xcell = ncf.get_attr( fname, 'XCELL' )
    ycell = ncf.get_attr( fname, 'YCELL' )
    area = float( xcell*ycell )
    unit_dict = { dt.replace_date( unit_key, date ): area
                  for date in dt.get_datelist() }
    return unit_dict

def get_unit_convert_bcon():
    """
    PhysicalData.bcon units = ppm/day
    ModelInputData.emis units = mol/s
    """
    global unit_key
    
    #physical constants:
    #molar weight of dry air (precision matches cmaq)
    mwair = 28.9628
    #convert proportion to ppm
    ppm_scale = 1E6
    #convert g to kg
    kg_scale = 1E-3
    
    unit_dict = {}
    efile = dt.replace_date( template.emis, dt.start_date )
    xcell = ncf.get_attr( efile, 'XCELL' )
    ycell = ncf.get_attr( efile, 'YCELL' )
    area = float( xcell*ycell )
    lay_sigma = list( ncf.get_attr( efile, 'VGLVLS' ) )
    lay_thick = [ l0 - l1 for l0,l1 in zip(lay_sigma[:-1],lay_sigma[1:]) ]
    lay_thick = np.array(lay_thick).reshape(( 1, len(lay_thick), 1, 1 ))
    
    for date in dt.get_datelist():
        met_file = dt.replace_date( met_cro_3d, date )
        rhoj = ncf.get_variable( met_file, 'DENSA_J' )[:, :len(lay_thick ), ... ]
        unit_array = (rhoj*lay_thick*area) / (kg_scale*ppm_scale*mwair)
        day_label = dt.replace_date( unit_key, date )
        unit_dict[ day_label ] = unit_array.copy()
    return unit_dict


def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """
    global unit_key
    global unit_convert_emis
    global unit_convert_bcon
    if unit_convert_emis is None:
        unit_convert_emis = get_unit_convert_emis()
    if unit_convert_bcon is None:
        unit_convert_bcon = get_unit_convert_bcon()

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
    m_shape = ncf.get_variable( emis_fname, physical_data.spcs[0] ).shape
    t = int( ncf.get_attr( emis_fname, 'TSTEP' ) )
    m_tstep = 3600*( t//10000 ) + 60*( (t//100) % 100 ) + ( t%100 )

    p_tstep = physical_data.tstep
    b_tstep = physical_data.tstep_bcon
    msg = 'physical & model input emis TSTEP incompatible.'
    assert all([ t % m_tstep == 0 for t in p_tstep ]), msg
    msg = 'physical BCON & model input emis TSTEP incompatible.'
    assert all([ t % m_tstep == 0 for t in b_tstep ]), msg
    nlay = physical_data.nlays_emis

    e_count = [ p//m_tstep for p in p_tstep ] #emis count per phys timestep
    b_count = [ b//m_tstep for b in b_tstep ] #emis count per phys-BCON timestep
    te = 0 #current phys time index
    tb = 0 #current phys-BCON time index
    m_len = daysec // m_tstep #No. emis steps per model day
    emis_pattern = 'emis.<YYYYMMDD>'
    for date in dt.get_datelist():
        p_ind = [] #time index of phys data
        p_rep = [] #No. repeats of phys index above (for today)
        r = 0
        #drain phys reps until a full day is filled, record which index's used
        while r < m_len:
            p_ind.append( te )
            p_rep.append( min(e_count[te],m_len) )
            r += p_rep[-1]
            e_count[te] -= p_rep[-1]
            if e_count[te] <= 0:
                te += 1
        #handle final timestep, repeat of next day OR last phys tstep
        if (te == len(e_count)) or (e_count[te] > 0):
            p_rep[-1] += 1
        else:
            p_ind.append( te )
            p_rep.append( 1 )
        #check index & rep
        assert (np.diff( p_ind ) == 1).all(), 'index out of alignment'
        assert sum( p_rep ) == ( m_len+1 ), 'reps do not sum to emis requirements'

        #build days emis spcs dict from phys
        spcs_dict = {}
        for spc in physical_data.spcs:
            model_arr = np.zeros( m_shape )
            start = p_ind[0]
            end = p_ind[-1] + 1
            phys_data = physical_data.emis[spc][ start:end, ... ]
            mod_data = np.repeat( phys_data, p_rep, axis=0 )
            model_arr[:,:nlay,:,:] += mod_data
            spcs_dict[ spc ] = model_arr * unit_convert_emis[ dt.replace_date( unit_key, date ) ]

        b_ind = [] #time index of phys-BCON data
        b_rep = [] #No. repeats of phys-BCON index above (for today)
        r = 0
        #drain phys reps until a full day is filled, record which index's used
        while r < m_len:
            b_ind.append( tb )
            b_rep.append( min(b_count[tb],m_len) )
            r += b_rep[-1]
            b_count[tb] -= b_rep[-1]
            if b_count[tb] <= 0:
                tb += 1
        #handle final timestep, repeat of next day OR last phys-BCON tstep
        if (tb == len(b_count)) or (b_count[tb] > 0):
            b_rep[-1] += 1
        else:
            b_ind.append( tb )
            b_rep.append( 1 )
        #check index & rep
        assert (np.diff( b_ind ) == 1).all(), 'index out of alignment'
        assert sum( b_rep ) == ( m_len+1 ), 'reps do not sum to emis requirements'

        #add bcon values to emissions
        bcon_lay = physical_data.bcon_up_lay
        nrow, ncol = physical_data.nrows, physical_data.ncols
        bshape = (m_len+1,1,1)
        bcon_convert = unit_convert_bcon[ dt.replace_date( unit_key, date ) ]
        for spc in physical_data.spcs:
            start = b_ind[0]
            end = b_ind[-1] + 1
            bcon_val = physical_data.bcon[spc][ start:end, : ]
            bcon_val = np.repeat( bcon_val, b_rep, axis=0 )
            #bcon_val = [SL,SH,EL,EH,NL,NH,WL,WH]
            bcon_arr = np.zeros( bcon_convert.shape )
            bcon_arr[:,:bcon_lay,0,1:] = bcon_val[:,0].reshape(bshape)
            bcon_arr[:,bcon_lay:,0,1:] = bcon_val[:,1].reshape(bshape)
            bcon_arr[:,:bcon_lay,1:,ncol-1] = bcon_val[:,2].reshape(bshape)
            bcon_arr[:,bcon_lay:,1:,ncol-1] = bcon_val[:,3].reshape(bshape)
            bcon_arr[:,:bcon_lay,nrow-1,:-1] = bcon_val[:,4].reshape(bshape)
            bcon_arr[:,bcon_lay:,nrow-1,:-1] = bcon_val[:,5].reshape(bshape)
            bcon_arr[:,:bcon_lay,:-1,0] = bcon_val[:,6].reshape(bshape)
            bcon_arr[:,bcon_lay:,:-1,0] = bcon_val[:,7].reshape(bshape)

            base_arr = spcs_dict.get( spc, 0. )
            spcs_dict[ spc ] = base_arr + (bcon_arr*bcon_convert)


        # attach species dict to model input args
        emis_argname = dt.replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout_fwd()
    
    return ModelInputData.create_new( **model_input_args )
