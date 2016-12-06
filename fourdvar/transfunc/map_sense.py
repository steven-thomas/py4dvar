"""
application: convert output of adjoint function to sensitivities to physical variables
like all transform in transfunc this is referenced from the transform function
eg: transform( sensitivity_instance, datadef.PhysicalData ) == condition_adjoint( sensitivity_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import SensitivityData, PhysicalData
from fourdvar.util.date_handle import replace_date
import fourdvar.util.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.global_config as global_config

def map_sense( sensitivity ):
    """
    application: map adjoint sensitivities to physical grid of unknowns.
    input: SensitivityData
    output: PhysicalData
    """
    
    #check that:
    #- global_config dates exist
    #- PhysicalData params exist
    #- template.emis & template.sense_emis are compatible
    #- template.icon & template.sense_conc are compatible
    datelist = global_config.get_datelist()
    PhysicalData.assert_params()
    #all spcs use same dimension set, therefore only need to test 1.
    test_spc = PhysicalData.spcs[0]
    mod_shape = ncf.get_variable( template.emis, test_spc ).shape    
    
    #phys_params = ['tsec','nstep','nlays_icon','nlays_emis','nrows','ncols','spcs']
    #icon_dict = { spcs: np.ndarray( nlays_icon, nrows, ncols ) }
    #emis_dict = { spcs: np.ndarray( nstep, nlays_emis, nrows, ncols ) }
    
    #create blank constructors for PhysicalData
    p = PhysicalData
    icon_shape = ( p.nlays_icon, p.nrows, p.ncols, )
    emis_shape = ( p.nstep, p.nlays_emis, p.nrows, p.ncols, )
    icon_dict = { spc: np.zeros( icon_shape ) for spc in p.spcs }
    emis_dict = { spc: np.zeros( emis_shape ) for spc in p.spcs }
    del p
    
    #construct icon_dict
    icon_label = replace_date( 'conc.<YYYYMMDD>', datelist[0] )
    icon_fname = sensitivity.file_data[ icon_label ][ 'actual' ]
    icon_vars = ncf.get_variable( icon_fname, icon_dict.keys() )
    for spc in PhysicalData.spcs:
        data = icon_vars[ spc ][ 0, :, :, : ]
        ilays, irows, icols = data.shape
        msg = 'conc_sense and PhysicalData.{} are incompatible'
        assert ilays >= PhysicalData.nlays_icon, msg.format( 'nlays_icon' )
        assert irows == PhysicalData.nrows, msg.format( 'nrows' )
        assert icols == PhysicalData.ncols, msg.format( 'ncols' )
        icon_dict[ spc ] = data[ 0:PhysicalData.nlays_icon, :, : ].copy()
    
    p_daysize = (24*60*60) / PhysicalData.tsec
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( datelist ):
        label = replace_date( emis_pattern, date )
        sense_fname = sensitivity.file_data[ label ][ 'actual' ]
        sense_data_dict = ncf.get_variable( sense_fname, PhysicalData.spcs )
        start = i * p_daysize
        end = (i+1) * p_daysize
        for spc in PhysicalData.spcs:
            #note: sensitivity has 1 extra step at end of day. model_input does NOT.
            #slice off that extra step
            sdata = sense_data_dict[ spc ][ :-1, ... ]
            sstep, slay, srow, scol = sdata.shape
            #recast to match mod_shape
            mstep, mlay, mrow, mcol = mod_shape
            msg = 'emis_sense and ModelInputData {} are incompatible.'
            assert (sstep >= mstep) and (sstep % mstep == 0), msg.format( 'TSTEP' )
            assert slay >= mlay, msg.format( 'NLAYS' )
            assert srow == mrow, msg.format( 'NROWS' )
            assert scol == mcol, msg.format( 'NCOLS' )
            fac = sstep // mstep
            tmp = np.array([ sdata[ i::fac, 0:mlay ,... ]
                             for i in range( fac ) ]).mean( axis=0 )
            #adjoint prepare_model
            msg = 'ModelInputData and PhysicalData.{} are incompatible.'
            assert (mstep >= p_daysize) and (mstep % p_daysize == 0), msg.format('nstep')
            assert mlay >= PhysicalData.nlays_emis, msg.format( 'nlays_emis' )
            assert mrow == PhysicalData.nrows, msg.format( 'nrows' )
            assert mcol == PhysicalData.ncols, msg.format( 'ncols' )
            fac = mstep // p_daysize
            pdata = np.array([ tmp[ i::fac, 0:PhysicalData.nlays_emis, ... ]
                               for i in range( fac ) ]).sum( axis=0 )
            emis_dict[ spc ][ start:end, ... ] = pdata.copy()
    
    return PhysicalData( icon_dict, emis_dict )
