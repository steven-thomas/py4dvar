"""
application: calculate the adjoint forcing values from the weighted residual of observations
like all transform in transfunc this is referenced from the transform function
eg: transform( observation_instance, datadef.AdjointForcingData ) == calc_forcing( observation_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData
from fourdvar.libshare.obs_handle import mkfrc_map
from fourdvar.util.file_handle import read_array

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    vallist = w_residual.get_vector( 'value' )
    kindlist = w_residual.get_vector( 'kind' )
    timelist = w_residual.get_vector( 'time' )
    xtraj = read_array( ModelOutputData )
    frc = np.zeros_like( xtraj )
    for val, kind, time in zip( vallist, kindlist, timelist ):
        sparse = mkfrc_map[ kind ]( xtraj[ :, time ], val )
        for i,v in sparse.items():
            frc[ i, time ] += v
    return AdjointForcingData( frc )

