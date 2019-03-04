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
unit_convert_dict = None

def get_unit_convert():
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
        
        rhoj_mapped = rhoj[ :-1, ... ].repeat( reps, axis=0 )
        rhoj_mapped = np.append( rhoj_mapped, rhoj[ -1:, ... ], axis=0 )
        unit_array = (ppm_scale*kg_scale*mwair) / (rhoj_mapped*lay_thick)
        
        day_label = dt.replace_date( unit_key, date )
        unit_dict[ day_label ] = unit_array
    return unit_dict

def map_sense( sensitivity ):
    """
    application: map adjoint sensitivities to physical grid of unknowns.
    input: SensitivityData
    output: PhysicalAdjointData
    """
    global unit_convert_dict
    global unit_key
    if unit_convert_dict is None:
        unit_convert_dict = get_unit_convert()
    
    #check that:
    #- date_handle dates exist
    #- PhysicalAdjointData params exist
    #- template.emis & template.sense_emis are compatible
    #- template.icon & template.sense_conc are compatible
    datelist = dt.get_datelist()
    PhysicalAdjointData.assert_params()
    #all spcs use same dimension set, therefore only need to test 1.
    test_spc = PhysicalAdjointData.spcs_out_emis[0]
    test_fname = dt.replace_date( template.emis, dt.start_date )
    mod_shape = ncf.get_variable( test_fname, test_spc ).shape    
    xcell = float( ncf.get_attr( test_fname, 'XCELL' ) )
    ycell = float( ncf.get_attr( test_fname, 'YCELL' ) )
    cell_area = xcell*ycell
    
    #create blank constructors for PhysicalAdjointData
    p = PhysicalAdjointData
    if inc_icon is True:
        raise ValueError('setup is not configured for ICON')
        #icon_shape = ( p.nlays_icon, p.nrows, p.ncols, )
        #icon_dict = { spc: np.zeros( icon_shape ) for spc in p.spcs_icon }
    ncat = len( p.cat_emis )
    emis_shape = ( ncat, p.nstep_emis, p.nlays_emis, p.nrows, p.ncols, )
    emis_dict = { spc: np.zeros( emis_shape ) for spc in p.spcs_out_emis }
    prop_shape = ( p.nstep_prop, p.nlays_emis, p.nrows, p.ncols, )
    prop_dict = { spc: np.zeros( prop_shape ) for spc in p.spcs_out_prop }

    diurnal = ncf.get_variable( template.diurnal, p.spcs_out_emis )
    del p
        
    p_daysize = float(24*60*60) / PhysicalAdjointData.tsec_prop
    nlay = PhysicalAdjointData.nlays_emis
    model_step = mod_shape[0]
    nrow = mod_shape[2]
    ncol = mod_shape[3]
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( datelist ):
        label = dt.replace_date( emis_pattern, date )
        sense_fname = sensitivity.file_data[ label ][ 'actual' ]
        sense_emis_dict = ncf.get_variable( sense_fname,
                                            PhysicalAdjointData.spcs_out_emis )
        sense_prop_dict = ncf.get_variable( sense_fname,
                                            PhysicalAdjointData.spcs_out_prop )
        emis_fname = dt.replace_date( cmaq_config.emis_file, date )
        emis_input_dict = ncf.get_variable( emis_fname,
                                            PhysicalAdjointData.spcs_in_prop )

        pstep = i // PhysicalAdjointData.tday_emis
        unit_convert = unit_convert_dict[ dt.replace_date( unit_key, date ) ]
        for spc in PhysicalAdjointData.spcs_out_emis:
            cat_arr = diurnal[ spc ][ :-1, :nlay, :, : ]
            sense_arr = (sense_emis_dict[spc] * unit_convert)[ :-1, :nlay, :, : ]
            model_avg = sense_arr.reshape((model_step-1,-1,
                                           nlay,nrow,ncol,)).mean(axis=1)
            for c in range( ncat ):
                data = model_avg.copy()
                data[ cat_arr != c ] = np.nan
                data = np.nansum( data, axis=0 )
                #insert NaN's if cell never had category c
                nan_arr = (cat_arr == c).sum( axis=0 )
                nan_arr = np.where( (nan_arr==0), np.nan, 0. )
                data += nan_arr
                emis_dict[spc][c,pstep,:,:,:] += data

        start = int( i * p_daysize )
        end = int( (i+1) * p_daysize )
        if start == end:
            end += 1
        spcs_pair_list = zip( PhysicalAdjointData.spcs_out_prop,
                              PhysicalAdjointData.spcs_in_prop )
        for spc_out, spc_in in spcs_pair_list:
            sdata = (sense_prop_dict[ spc_out ][:] * unit_convert)[:-1,...]
            edata = (emis_input_dict[ spc_in ][:] / cell_area)[:-1,...]
            mod_avg = sdata[:,:nlay,:,:]
            mod_avg = mod_avg.reshape((model_step-1,-1,nlay,nrow,ncol)).mean( axis=1 )
            assert mod_avg.shape == edata.shape, 'Error in shape re-casting.'
            prop_arr = mod_avg / edata
            prop_arr = prop_arr.reshape((end-start,-1,nlay,nrow,ncol)).sum( axis=1 )
            prop_dict[ spc_out ][ start:end, ... ] += prop_arr[:]
            
    return PhysicalAdjointData( emis_dict, prop_dict )
