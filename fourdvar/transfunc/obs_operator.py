"""
application: simulate set of observations from output of the forward model
like all transform in transfunc this is referenced from the transform function
eg: transform( model_output_instance, datadef.ObservationData ) == obs_operator( model_output_instance )
"""

import numpy as np

from fourdvar.datadef import ModelOutputData, ObservationData

def obs_operator( model_output ):
    """
    application: simulate set of observations from output of the forward model
    input: ModelOutputData
    output: ObservationData
    """
    model_arr = np.array( model_output.value )
    obs_val_arr = np.zeros( ObservationData.length )
    for obs_i, w_dict in enumerate( ObservationData.weight_grid ):
        for coord, weight in w_dict.items():
            t,x = coord
            val = ( weight * model_arr[t,x] )
            obs_val_arr[ obs_i ] += val

    return ObservationData( obs_val_arr )
