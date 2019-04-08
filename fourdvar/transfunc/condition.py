"""
application: apply pre-conditioning to PhysicalData, get vector to optimize
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.UnknownData ) == condition( physical_instance )
"""
from __future__ import absolute_import

import numpy as np

from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.datadef import UnknownData
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
    emis_len = p.nall_cells
    if inc_icon is True:
        total_len = len( p.spcs ) + p.nunknowns
    else:
        total_len = p.nunknowns
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

    emis_vector = np.zeros( emis_len )
    for ns,spc in enumerate( PhysicalAbstractData.spcs ):
        emis = physical.emis[ spc ].flatten()
        emis_vector[ ns*emis.size : (ns+1)*emis.size ] = emis
    emis_vector = np.dot( emis_vector, PhysicalAbstractData.emis_corr_matrix )
    emis_vector = weight( emis_vector, PhysicalAbstractData.emis_unc_vector )
    arg[ i: ] = emis_vector
    
    return UnknownData( arg )
