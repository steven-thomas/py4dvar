"""
application: apply pre-conditioning to PhysicalData, get vector to optimize
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.UnknownData ) == condition( physical_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, UnknownData

def condition( physical ):
    """
    application: apply pre-conditioning to PhysicalData, get vector to optimize
    input: PhysicalData
    output: UnknownData
    
    notes: this function must apply the inverse prior error covariance
    """
    p = PhysicalData
    icon_len = p.nlays_icon * p.nrows * p.ncols
    emis_len = p.nstep * p.nlays_emis * p.nrows * p.ncols
    total_len = len( p.spcs ) * ( icon_len + emis_len )
    del p
    
    arg = np.zeros( total_len )
    i = 0
    for spc in PhysicalData.spcs:
        icon = physical.icon[ spc ] / physical.icon_unc[ spc ]
        emis = physical.emis[ spc ] / physical.emis_unc[ spc ]
        arg[ i:i+icon_len ] = icon.flatten()
        i += icon_len
        arg[ i:i+emis_len ] = emis.flatten()
        i += emis_len
    assert i == total_len, 'Some unknowns left unassigned!'
    
    return UnknownData( arg )
