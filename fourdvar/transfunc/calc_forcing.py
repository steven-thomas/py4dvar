"""
application: calculate the adjoint forcing values from the weighted residual of observations
like all transform in transfunc this is referenced from the transform function
eg: transform( observation_instance, datadef.AdjointForcingData ) == calc_forcing( observation_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    
    return AdjointForcingData.create_new( w_residual.value *np.array([1.,1.,1.]))
