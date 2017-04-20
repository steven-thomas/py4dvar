"""
application: undo pre-conditioning to UnknownData, get back PhysicalData (format of prior/background)
like all transform in transfunc this is referenced from the transform function
eg: transform( unknown_instance, datadef.PhysicalData ) == uncondition( unknown_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import UnknownData, PhysicalData

def uncondition( unknown ):
    """
    application: undo pre-conditioning of PhysicalData, add back any lost metadata
    input: UnknownData
    output: PhysicalData
    
    notes: this function must apply the prior error covariance
    """
    PhysicalData.assert_params()
    p = PhysicalData
    icon_len = p.nlays_icon * p.nrows * p.ncols
    emis_len = p.nstep * p.nlays_emis * p.nrows * p.ncols
    total_len = len( p.spcs ) * ( icon_len + emis_len )
    del p
    
    vals = unknown.get_vector()
    icon_dict = {}
    emis_dict = {}
    i = 0
    for spc in PhysicalData.spcs:
        icon = vals[ i:i+icon_len ]
        i += icon_len
        emis = vals[ i:i+emis_len ]
        i += emis_len
        
        p = PhysicalData
        icon = icon.reshape(( p.nlays_icon, p.nrows, p.ncols, ))
        emis = emis.reshape(( p.nstep, p.nlays_emis, p.nrows, p.ncols, ))
        icon = icon * p.icon_unc[ spc ]
        emis = emis * p.emis_unc[ spc ]
        del p
        
        icon_dict[ spc ] = icon
        emis_dict[ spc ] = emis
    
    assert i == total_len, 'Some physical data left unassigned!'
    
    return PhysicalData( icon_dict, emis_dict )

