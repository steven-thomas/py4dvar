"""
application: convert output of adjoint function to sensitivities to physical variables
like all transform in transfunc this is referenced from the transform function
eg: transform( sensitivity_instance, datadef.PhysicalAdjointData ) == condition_adjoint( sensitivity_instance )
"""

import numpy as np

from fourdvar.datadef import SensitivityData, PhysicalAdjointData

def map_sense( sensitivity ):
    """
    application: map adjoint sensitivities to physical grid of unknowns.
    input: SensitivityData
    output: PhysicalAdjointData
    """
    #only solving for 4 parameters: p1,p2,k1,k2
    sens_p = sensitivity.p
    return PhysicalAdjointData( sens_p[:4] )
