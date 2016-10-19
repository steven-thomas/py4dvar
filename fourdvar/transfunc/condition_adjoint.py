"""
application: convert output of adjoint function to gradients of vector used in minimizer
like all transform in transfunc this is referenced from the transform function
eg: transform( sensitivity_instance, datadef.UnknownData ) == condition_adjoint( sensitivity_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import SensitivityData, UnknownData

def condition_adjoint( sensitivity ):
    """
    application: map adjoint sensitivities to unknowns used in minimizer
    input: SensitivityData
    output: UnknownData
    
    notes: this function must apply the adjoint inverse prior error covariance??
    """
    return UnknownData( sensitivity.data )

