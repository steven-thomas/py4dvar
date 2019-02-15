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
    emis_len = p.nstep * p.nlays_emis * p.nrows * p.ncols
    if inc_icon is True:
        icon_len = p.nlays_icon * p.nrows * p.ncols
        total_len = len( p.spcs ) * ( icon_len + emis_len )
    else:
        total_len = len( p.spcs ) * emis_len
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
        emis = vals[ i:i+emis_len ]
        i += emis_len
        
        p = PhysicalData
        if inc_icon is True:
            icon = icon.reshape(( p.nlays_icon, p.nrows, p.ncols, ))
            icon = icon * p.icon_unc[ spc ]
            icon_dict[ spc ] = icon
        emis = emis.reshape(( p.nstep, p.nlays_emis, p.nrows, p.ncols, ))
        emis = emis * p.emis_unc[ spc ]
        emis_dict[ spc ] = emis
        del p
    
    assert i == total_len, 'Some physical data left unassigned!'
    
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict )

