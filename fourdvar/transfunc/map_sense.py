"""
application: convert output of adjoint function to sensitivities to physical variables
like all transform in transfunc this is referenced from the transform function
eg: transform( sensitivity_instance, datadef.PhysicalAdjointData ) == condition_adjoint( sensitivity_instance )
"""

import numpy as np

from fourdvar.datadef import SensitivityData, PhysicalAdjointData
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.params.cmaq_config as cmaq_config
from fourdvar.params.input_defn import inc_icon

unit_key = 'units.<YYYYMMDD>'
unit_convert_emis = None
unit_convert_bcon = None

def get_unit_convert_emis():
    """
    extension: get unit conversion dictionary for sensitivity to each days emissions
    input: None
    output: dict ('units.<YYYYMMDD>': np.ndarray( shape_of( template.sense_emis ) )
    
    notes: SensitivityData.emis units = CF/(ppm/s)
           PhysicalAdjointData.emis units = CF/(mol/(s*m^2))
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
    #all spcs have same shape, get from 1st
    tmp_spc = ncf.get_attr( template.sense_emis, 'VAR-LIST' ).split()[0]
    target_shape = ncf.get_variable( template.sense_emis, tmp_spc )[:].shape
    #layer thickness constant between files
    lay_sigma = list( ncf.get_attr( template.sense_emis, 'VGLVLS' ) )
    #layer thickness measured in scaled pressure units
    lay_thick = [ lay_sigma[ i ] - lay_sigma[ i+1 ] for i in range( len( lay_sigma ) - 1 ) ]
    lay_thick = np.array(lay_thick).reshape(( 1, len(lay_thick), 1, 1 ))
    
    for date in dt.get_datelist():
        met_file = dt.replace_date( cmaq_config.met_cro_3d, date )
        #slice off any extra layers above area of interest
        rhoj = ncf.get_variable( met_file, 'DENSA_J' )[ :, :len( lay_thick ), ... ]
        #assert timesteps are compatible
        assert (target_shape[0]-1) >= (rhoj.shape[0]-1), 'incompatible timesteps'
        assert (target_shape[0]-1) % (rhoj.shape[0]-1) == 0, 'incompatible timesteps'
        reps = (target_shape[0]-1) // (rhoj.shape[0]-1)
        
        rhoj_interp = np.zeros(target_shape)
        for r in range(reps):
            frac = float(2*r+1) / float(2*reps)
            rhoj_interp[r:-1:reps,...] = (1-frac)*rhoj[:-1,...] + frac*rhoj[1:,...]
        rhoj_interp[-1,...] = rhoj[-1,...]
        unit_array = (ppm_scale*kg_scale*mwair) / (rhoj_interp*lay_thick)
        
        day_label = dt.replace_date( unit_key, date )
        unit_dict[ day_label ] = unit_array
    return unit_dict

def get_unit_convert_bcon():
    """
    SensitivityData.emis units = CF/(ppm/s)
    PhysicalAdjointData.bcon units = CF/(ppm/s)
    """
    unit_dict = { dt.replace_date( unit_key, date ): 1.
                  for date in dt.get_datelist() }
    return unit_dict

def map_sense( sensitivity ):
    """
    application: map adjoint sensitivities to physical grid of unknowns.
    input: SensitivityData
    output: PhysicalAdjointData
    """
    global unit_key
    global unit_convert_emis
    global unit_convert_bcon
    if unit_convert_emis is None:
        unit_convert_emis = get_unit_convert_emis()
    if unit_convert_bcon is None:
        unit_convert_bcon = get_unit_convert_bcon()
    
    #check that:
    #- date_handle dates exist
    #- PhysicalAdjointData params exist
    #- template.emis & template.sense_emis are compatible
    #- template.icon & template.sense_conc are compatible
    datelist = dt.get_datelist()
    PhysicalAdjointData.assert_params()
    #all spcs use same dimension set, therefore only need to test 1.
    test_spc = PhysicalAdjointData.spcs[0]
    test_fname = dt.replace_date( template.emis, dt.start_date )
    mod_shape = ncf.get_variable( test_fname, test_spc ).shape    
        
    #create blank constructors for PhysicalAdjointData
    p = PhysicalAdjointData
    if inc_icon is True:
        icon_dict = { spc: 1. for spc in p.spcs }
    ncat = len( p.cat_emis )
    emis_shape = ( ncat, p.nstep_emis, p.nlays_emis, p.nrows, p.ncols, )
    emis_dict = { spc: np.zeros( emis_shape ) for spc in p.spcs }
    bcon_shape = ( p.nstep_bcon, p.bcon_region, )
    bcon_dict = { spc: np.zeros( bcon_shape ) for spc in p.spcs }

    diurnal = ncf.get_variable( template.diurnal, p.spcs )
    del p
    
    #construct icon_dict
    if inc_icon is True:
        i_sense_label = dt.replace_date( 'conc.<YYYYMMDD>', datelist[0] )
        i_sense_fname = sensitivity.file_data[ i_sense_label ][ 'actual' ]
        i_sense_vars = ncf.get_variable( i_sense_fname, icon_dict.keys() )
        icon_vars = ncf.get_variable( template.icon, icon_dict.keys() )
        for spc in PhysicalAdjointData.spcs:
            sense_data = i_sense_vars[ spc ][ 0, ... ]
            icon_data = icon_vars[ spc ] [ 0, ... ]
            msg = 'conc_sense and template.icon are incompatible'
            assert sense_data.shape == icon_data.shape, msg
            icon_dict[ spc ] = (sense_data * icon_data).sum()
    
    b_daysize = float(24*60*60) / PhysicalAdjointData.tsec_bcon
    nlay = PhysicalAdjointData.nlays_emis
    blay = PhysicalAdjointData.bcon_up_lay
    model_step = mod_shape[0]
    nrow = mod_shape[2]
    ncol = mod_shape[3]
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( datelist ):
        label = dt.replace_date( emis_pattern, date )
        sense_fname = sensitivity.file_data[ label ][ 'actual' ]
        sense_data_dict = ncf.get_variable( sense_fname, PhysicalAdjointData.spcs )

        pstep = i // PhysicalAdjointData.tday_emis
        b_start = int( i * b_daysize )
        b_end = int( (i+1) * b_daysize )
        if b_start == b_end:
            b_end += 1
        emis_unit = unit_convert_emis[ dt.replace_date( unit_key, date ) ]
        bcon_unit = unit_convert_bcon[ dt.replace_date( unit_key, date ) ]
        for spc in PhysicalAdjointData.spcs:
            cat_arr = diurnal[ spc ][ :-1, :nlay, :, : ]
            sense_arr_emis = (sense_data_dict[ spc ] * emis_unit)[:-1,:nlay,:,:]
            model_arr_emis = sense_arr_emis.reshape((model_step-1,-1,nlay,nrow,ncol,)).sum(axis=1)
            for c in range( ncat ):
                data = model_arr_emis.copy()
                data[ cat_arr != c ] = np.nan
                data = np.nansum( data, axis=0 )
                #insert NaN's if cell never had category c
                nan_arr = (cat_arr == c).sum( axis=0 )
                nan_arr = np.where( (nan_arr==0), np.nan, 0. )
                data += nan_arr
                emis_dict[spc][c,pstep,:,:,:] += data

            sense_arr_bcon = (sense_data_dict[ spc ][:] * bcon_unit)[:-1,:,:,:]
            tot_lay = sense_arr_bcon.shape[1]
            model_arr_bcon = sense_arr_bcon.reshape((model_step-1,-1,tot_lay,nrow,ncol)).sum( axis=1 )
            bcon_arr = model_arr_bcon.reshape((b_end-b_start,-1,tot_lay,nrow,ncol)).sum( axis=1 )
            bcon_SL = bcon_arr[:,:blay,0,1:].sum( axis=(1,2,) )
            bcon_SH = bcon_arr[:,blay:,0,1:].sum( axis=(1,2,) )
            bcon_EL = bcon_arr[:,:blay,1:,ncol-1].sum( axis=(1,2,) )
            bcon_EH = bcon_arr[:,blay:,1:,ncol-1].sum( axis=(1,2,) )
            bcon_NL = bcon_arr[:,:blay,nrow-1,:-1].sum( axis=(1,2,) )
            bcon_NH = bcon_arr[:,blay:,nrow-1,:-1].sum( axis=(1,2,) )
            bcon_WL = bcon_arr[:,:blay,:-1,0].sum( axis=(1,2,) )
            bcon_WH = bcon_arr[:,blay:,:-1,0].sum( axis=(1,2,) )
            bcon_merge = np.stack( [bcon_SL,bcon_SH,bcon_EL,bcon_EH,
                                    bcon_NL,bcon_NH,bcon_WL,bcon_WH], axis=1 )
            bcon_dict[spc][ b_start:b_end, : ] += bcon_merge[:,:]

    if inc_icon is False:
        icon_dict = None
    return PhysicalAdjointData( icon_dict, emis_dict, bcon_dict )
