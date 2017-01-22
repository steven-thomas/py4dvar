"""
application: apply pre-conditioning to PhysicalData, get vector to optimize
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.UnknownData ) == condition( physical_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import UnknownData
from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData

def condition_adjoint( physical_adjoint ):
    """
    application: apply pre-conditioning to PhysicalAdjointData, get vector gradient
    input: PhysicalAdjointData
    output: UnknownData
    
    notes: this function must apply the prior error covariance
    """
    return phys_to_unk( physical_adjoint, True )

def condition( physical ):
    """
    application: apply pre-conditioning to PhysicalData, get vector to optimize
    input: PhysicalData
    output: UnknownData
    
    notes: this function must apply the inverse prior error covariance
    """
    return phys_to_unk( physical, False )

def phys_to_unk( physical, is_adjoint ):
    """
    application: apply pre-conditioning to PhysicalData, get vector to optimize
    input: PhysicalData
    output: UnknownData
    
    notes: this function must apply the inverse prior error covariance
    """
    p = PhysicalAbstractData
    icon_len = p.nlays_icon * p.nrows * p.ncols
    emis_len = p.nstep * p.nlays_emis * p.nrows * p.ncols
    total_len = len( p.spcs ) * ( icon_len + emis_len )
    del p
    
    #weighting function changes if is_adjoint
    if is_adjoint is True:
        weight = lambda val, sd: val * sd
    else:
        weight = lambda val, sd: val / sd
    
    arg = np.zeros( total_len )
    i = 0
    for spc in PhysicalAbstractData.spcs:
        icon = weight( physical.icon[ spc ], physical.icon_unc[ spc ] )
        emis = weight( physical.emis[ spc ], physical.emis_unc[ spc ] )
        arg[ i:i+icon_len ] = icon.flatten()
        i += icon_len
        arg[ i:i+emis_len ] = emis.flatten()
        i += emis_len
    assert i == total_len, 'Some unknowns left unassigned!'
    
    return UnknownData( arg )
