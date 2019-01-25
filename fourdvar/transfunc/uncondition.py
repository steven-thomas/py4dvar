"""
application: undo pre-conditioning to UnknownData, get back PhysicalData (format of prior/background)
like all transform in transfunc this is referenced from the transform function
eg: transform( unknown_instance, datadef.PhysicalData ) == uncondition( unknown_instance )
"""
from __future__ import absolute_import

import numpy as np

from fourdvar.datadef import UnknownData, PhysicalData
from fourdvar.params.input_defn import inc_icon

def uncondition( unknown ):
    """
    application: undo pre-conditioning of PhysicalData, add back any lost metadata
    input: UnknownData
    output: PhysicalData
    
    notes: this function must apply the prior error covariance
    """
    PhysicalData.assert_params()
    p = PhysicalData
    emis_len = p.nstep * p.nlays_emis * p.nrows * p.ncols
    emis_shape = ( p.nstep, p.nlays_emis, p.nrows, p.ncols )
    if inc_icon is True:
        icon_len = p.nlays_icon * p.nrows * p.ncols
        icon_shape = ( p.nlays_icon, p.nrows, p.ncols )
    del p
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    emis_dict = {}
    i = 0
    for spc in PhysicalData.spcs:
        if inc_icon is True:
            icon = vals[ i:i+icon_len ]
            i += icon_len
            icon = icon.reshape( icon_shape )
            icon = icon * PhysicalData.icon_unc[ spc ]
            icon_dict[ spc ] = icon
    
    emis_vector = vals[i:] * PhysicalData.emis_unc_vector
    emis_vector = np.matmul( PhysicalData.emis_corr_matrix, emis_vector )
    for ns,spc in enumerate( PhysicalData.spcs ):
        emis = emis_vector[ ns*emis_len : (ns+1)*emis_len ]
        emis = emis.reshape( emis_shape )
        emis_dict[ spc ] = emis
        
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict )

