"""
application: calculate the adjoint forcing values from the weighted residual of observations
like all transform in transfunc this is referenced from the transform function
eg: transform( observation_instance, datadef.AdjointForcingData ) == calc_forcing( observation_instance )
"""

import numpy as np

from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    
    kwargs = AdjointForcingData.get_kwargs_dict()
    for ymd, ilist in ObservationData.ind_by_date.items():
        spc_dict = kwargs[ 'force.'+ymd ]
        for i in ilist:
            for coord,weight in ObservationData.weight_grid[i].items():
                if str( coord[0] ) == ymd:
                    step,lay,row,col,spc = coord[1:]
                    w_val = w_residual.value[i] * weight
                    spc_dict[spc][step,lay,row,col] += w_val
    
    return AdjointForcingData.create_new( **kwargs )
