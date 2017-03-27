"""
application: calculate the adjoint forcing values from the weighted residual of observations
like all transform in transfunc this is referenced from the transform function
eg: transform( observation_instance, datadef.AdjointForcingData ) == calc_forcing( observation_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData
import fourdvar.util.obs_handle as obs_handle

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    
    obs_by_date = obs_handle.get_obs_by_date( w_residual )
    kwargs = AdjointForcingData.get_kwargs_dict()
    for ymd, obslist in obs_by_date.items():
        spcs_dict = kwargs[ 'force.'+ymd ]
        for obs in obslist:
            for coord,weight in obs.weight_grid.items():
                if str( coord[0] ) == ymd:
                    step,lay,row,col,spc = coord[1:]
                    w_val = obs.value * weight
                    spcs_dict[spc][step,lay,row,col] += w_val
    return AdjointForcingData( **kwargs )
