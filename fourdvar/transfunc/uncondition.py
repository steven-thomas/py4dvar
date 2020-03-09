"""
application: undo pre-conditioning to UnknownData, get back PhysicalData (format of prior/background)
like all transform in transfunc this is referenced from the transform function
eg: transform( unknown_instance, datadef.PhysicalData ) == uncondition( unknown_instance )
"""

import numpy as np

from fourdvar.datadef import UnknownData, PhysicalData
import fourdvar.util.netcdf_handle as ncf
from fourdvar.params.input_defn import inc_icon
import fourdvar.params.template_defn as template

def uncondition( unknown ):
    """
    application: undo pre-conditioning of PhysicalData, add back any lost metadata
    input: UnknownData
    output: PhysicalData
    
    notes: this function must apply the prior error covariance
    """
    PhysicalData.assert_params()
    p = PhysicalData
    ncat = len( p.cat_emis )
    emis_shape = ( ncat, p.nstep_emis, p.nlays_emis, p.nrows, p.ncols, )
    bcon_shape = ( p.nstep_bcon, p.bcon_region, )
    bcon_len = np.prod( bcon_shape )
    del p

    diurnal = ncf.get_variable( template.diurnal, PhysicalData.spcs )
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    emis_dict = {}
    bcon_dict = {}
    i = 0
    for spc in PhysicalData.spcs:
        if inc_icon is True:
            icon = vals[ i ]
            i += 1
            icon_dict[ spc ] = icon * PhysicalData.icon_unc[ spc ]

        emis_arr = np.zeros( emis_shape )
        cat_arr = diurnal[ spc ][ :-1, :PhysicalData.nlays_emis, :, : ]
        for c in range( ncat ):
            nan_arr = (cat_arr == c).sum( axis=0, keepdims=True )
            nan_arr = np.where( (nan_arr==0), np.nan, 0. )
            emis_arr[ c, :, :, :, : ] = nan_arr

        emis_len = np.count_nonzero( ~np.isnan(emis_arr) )
        emis_vector = vals[ i:i+emis_len ]
        emis_arr[ ~np.isnan(emis_arr) ] = emis_vector
        emis_dict[ spc ] = emis_arr * PhysicalData.emis_unc[ spc ]
        i += emis_len

        bcon = vals[ i:i+bcon_len ]
        bcon = bcon.reshape( bcon_shape )
        bcon_dict[ spc ] = bcon * PhysicalData.bcon_unc[ spc ]
        i += bcon_len
    
    assert i == len(vals), 'Some physical data left unassigned!'
    
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict, bcon_dict )
