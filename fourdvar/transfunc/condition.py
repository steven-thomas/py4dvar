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
    return UnknownData( np.array( physical_adjoint.value )* PhysicalAbstractData.unc )

def condition( physical ):
    """
    application: apply pre-conditioning to PhysicalData, get vector to optimize
    input: PhysicalData
    output: UnknownData
    
    notes: this function must apply the inverse prior error covariance
    """
    return UnknownData( np.array( physical.value)/np.array( PhysicalAbstractData.unc) )
