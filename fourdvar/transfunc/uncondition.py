"""
application: undo pre-conditioning to UnknownData, get back PhysicalData (format of prior/background)
like all transform in transfunc this is referenced from the transform function
eg: transform( unknown_instance, datadef.PhysicalData ) == uncondition( unknown_instance )
"""

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
    emis_shape = ( p.nstep, p.nlays_emis, p.nrows, p.ncols, )
    emis_len = np.prod( emis_shape )
    if inc_icon is True:
        icon_shape = ( p.nlays_icon, p.nrows, p.ncols, )
        icon_len = np.prod( icon_shape )
        total_len = len( p.spcs_icon )*icon_len + len( p.spcs_out )*emis_len
    else:
        total_len = len( p.spcs_out ) * emis_len
    del p
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    emis_dict = {}
    i = 0
    if inc_icon is True:
        for spc in PhysicalData.spcs_icon:
            icon = vals[ i:i+icon_len ]
            i += icon_len
            icon = icon.reshape( icon_shape )
            icon = icon * PhysicalData.icon_unc[ spc ]
            icon_dict[ spc ] = icon
    for spc in PhysicalData.spcs_out:
        emis = vals[ i:i+emis_len ]
        i += emis_len        
        emis = emis.reshape( emis_shape )
        emis = emis * PhysicalData.emis_unc[ spc ]
        emis_dict[ spc ] = emis
    
    assert i == total_len, 'Some physical data left unassigned!'
    
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict )
