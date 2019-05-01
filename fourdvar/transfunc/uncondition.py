"""
application: undo pre-conditioning to UnknownData, get back PhysicalData (format of prior/background)
like all transform in transfunc this is referenced from the transform function
eg: transform( unknown_instance, datadef.PhysicalData ) == uncondition( unknown_instance )
"""

import numpy as np

import fourdvar.util.netcdf_handle as ncf
from fourdvar.datadef import UnknownData, PhysicalData
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
    ncat = len( p.cat )
    emis_len = ncat * p.nstep * p.nlays_emis * p.nrows * p.ncols
    emis_shape = ( ncat, p.nstep, p.nlays_emis, p.nrows, p.ncols, )
    if inc_icon is True:
        icon_len = p.nlays_icon * p.nrows * p.ncols
        icon_shape = ( p.nlays_icon, p.nrows, p.ncols, )
    del p
    
    diurnal = ncf.get_variable( template.diurnal, PhysicalData.spcs )
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    emis_dict = {}
    i = 0
    for spc in PhysicalData.spcs:
        if inc_icon is True:
            icon = vals[ i:i+icon_len ]
            icon = icon.reshape( icon_shape )
            icon_dict[ spc ] = icon
            i += icon_len
        
        emis_arr = np.zeros( emis_shape )
        cat_arr = diurnal[ spc ][ :-1, :PhysicalData.nlays_emis, :, : ]
        for c in range( ncat ):
            nan_arr = (cat_arr == c).sum( axis=0, keepdims=True )
            nan_arr = np.where( (nan_arr==0), np.nan, 0. )
            emis_arr[ c, :, :, :, : ] = nan_arr
        
        emis_len = np.count_nonzero( ~np.isnan(emis_arr) )
        emis_vector = vals[ i:i+emis_len ]
        emis_arr[ ~np.isnan(emis_arr) ] = emis_vector
        emis_dict[ spc ] = emis_arr
        i += emis_len
        
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict )

