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
    prop_len = p.nstep_prop * p.nlays_emis * p.nrows * p.ncols
    if inc_icon is True:
        raise ValueError('Setup does not support ICON solving')
        #icon_len = p.nlays_icon * p.nrows * p.ncols
        #total_len = len( p.spcs_icon )*icon_len + len( p.spcs_out )*emis_len
    else:
        total_len = len(p.spcs_out_emis)*emis_len + len(p.spcs_out_prop)*prop_len
    del p
    
    #weighting function changes if is_adjoint
    if is_adjoint is True:
        weight = lambda val, sd: val * sd
    else:
        weight = lambda val, sd: val / sd
    
    arg = np.zeros( total_len )
    i = 0
    if inc_icon is True:
        raise ValueError('Setup does not support ICON solving')
        #for spc in PhysicalAbstractData.spcs_icon:
        #    icon = weight( physical.icon[ spc ], physical.icon_unc[ spc ] )
        #    arg[ i:i+icon_len ] = icon.flatten()
        #    i += icon_len
    for spc in PhysicalAbstractData.spcs_out_emis:
        emis = weight( physical.emis[ spc ], physical.emis_unc[ spc ] )
        arg[ i:i+emis_len ] = emis.flatten()
        i += emis_len
    for spc in PhysicalAbstractData.spcs_out_prop:
        prop = weight( physical.prop[ spc ], physical.prop_unc[ spc ] )
        arg[ i:i+prop_len ] = prop.flatten()
        i += prop_len
    assert i == total_len, 'Some unknowns left unassigned!'
    #remove nan's
    arg = arg[ ~np.isnan( arg ) ]
    return UnknownData( arg )
