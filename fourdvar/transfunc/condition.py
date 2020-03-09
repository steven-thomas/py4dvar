"""
application: apply pre-conditioning to PhysicalData, get vector to optimize
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.UnknownData ) == condition( physical_instance )
"""

import numpy as np

from fourdvar.datadef import UnknownData
from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.params.input_defn import inc_icon

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
    emis_len = len(p.cat_emis) * p.nstep_emis * p.nlays_emis * p.nrows * p.ncols
    bcon_len = p.nstep_bcon * p.bcon_region
    if inc_icon is True:
        total_len = len(p.spcs) * (1 + emis_len + bcon_len)
    else:
        total_len = len(p.spcs) * (emis_len + bcon_len)
    del p
    
    #weighting function changes if is_adjoint
    if is_adjoint is True:
        weight = lambda val, sd: val * sd
    else:
        weight = lambda val, sd: val / sd
    
    arg = np.zeros( total_len )
    i = 0
    for spc in PhysicalAbstractData.spcs:
        if inc_icon is True:
            icon = weight( physical.icon[ spc ], physical.icon_unc[ spc ] )
            arg[ i ] = icon
            i += 1

        emis = weight( physical.emis[ spc ], physical.emis_unc[ spc ] )
        arg[ i:i+emis_len ] = emis.flatten()
        i += emis_len

        bcon = weight( physical.bcon[ spc ], physical.bcon_unc[ spc ] )
        arg[ i:i+bcon_len ] = bcon.flatten()
        i += bcon_len
    assert i == total_len, 'Some unknowns left unassigned!'
    #remove nan's
    arg = arg[ ~np.isnan( arg ) ]    
    return UnknownData( arg )
