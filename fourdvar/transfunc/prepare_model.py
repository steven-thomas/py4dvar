"""
prepare_model.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import PhysicalData, ModelInputData
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.cmaq_handle as cmaq
from fourdvar.params.cmaq_config import met_cro_3d
from fourdvar.params.input_defn import inc_icon

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

    diurnal = ncf.get_variable( template.diurnal, physical_data.spcs )
    
    #all emis files & spcs for model_input use same NSTEP dimension, get it's size
    emis_fname = dt.replace_date( template.emis, dt.start_date )
    m_daysize = ncf.get_variable( emis_fname, physical_data.spcs[0] ).shape[0] - 1
    dlist = dt.get_datelist()
    b_daysize = float(physical_data.nstep_bcon) / len( dlist )
    assert (b_daysize < 1) or (m_daysize % b_daysize == 0), 'physical & model input emis TSTEP incompatible.'
    nlay = physical_data.nlays_emis
    
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( dlist ):
        spcs_dict = {}
        estep = int( i // physical_data.tday_emis )
        for spcs_name in physical_data.spcs:
            model_arr = np.zeros( diurnal[ spcs_name ].shape )
            for c,_ in enumerate( physical_data.cat_emis ):
                phys_arr = physical_data.emis[ spcs_name ][ c, estep, ... ]
                phys_arr[ np.isnan( phys_arr ) ] = 0.
                di_filter = (diurnal[ spcs_name ][:,:nlay,:,:] == c)
                model_arr[:,:nlay,:,:] += phys_arr * di_filter
            spcs_dict[ spcs_name ] = model_arr * unit_convert_emis[ dt.replace_date( unit_key, date ) ]

        #add bcon values to emissons
        msg = 'Only setup for 8-region boundary conditions.'
        assert physical_data.bcon_region == 8, msg
        bcon_lay = physical_data.bcon_up_lay
        nrow, ncol = physical_data.nrows, physical_data.ncols
        bshape = (m_daysize+1,1,1)
        bcon_convert = unit_convert_bcon[ dt.replace_date( unit_key, date ) ]
        start = int(i * b_daysize)
        end = int( (i+1) * b_daysize )
        if start == end:
            end += 1
        for spc in physical_data.spcs:
            bcon_val = physical_data.bcon[ spc ][ start:end, : ]
            if end < physical_data.nstep_bcon:
                last_slice = physical_data.bcon[ spc ][ end:end+1, : ]
            else:
                last_slice = physical_data.bcon[ spc ][ end-1:end, : ]
            bcon_val = np.repeat( bcon_val, m_daysize // (end-start), axis=0 )
            bcon_val = np.append( bcon_val, last_slice, axis=0 )
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

        emis_argname = dt.replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout_fwd()
    
    return ModelInputData.create_new( **model_input_args )
