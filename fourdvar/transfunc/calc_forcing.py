"""
application: calculate the adjoint forcing values from the weighted residual of observations
like all transform in transfunc this is referenced from the transform function
eg: transform( observation_instance, datadef.AdjointForcingData ) == calc_forcing( observation_instance )
"""

import numpy as np

from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData
import fourdvar.params.model_data as md

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    force_arr = np.zeros((md.rd_sample+1,2))
    for obs_i, w_dict in enumerate( w_residual.weight_grid ):
        for coord, weight in w_dict.items():
            t,x = coord
            val = w_residual.value[obs_i] * weight
            force_arr[t,x] += val
    
    return AdjointForcingData.create_new( force_arr )
