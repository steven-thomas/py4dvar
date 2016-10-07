
import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData
from fourdvar.libshare.obs_handle import mkfrc_map
from fourdvar.util.file_handle import load_array

def calc_forcing( w_residual ):
    #from the weighted residuals of observations calculate the forcing for the adjoint model
    vallist = w_residual.get_vector( 'value' )
    kindlist = w_residual.get_vector( 'kind' )
    timelist = w_residual.get_vector( 'time' )
    xtraj = load_array( label='ModelOutputData' )
    frc = np.zeros_like( xtraj )
    for val, kind, time in zip( vallist, kindlist, timelist ):
        #frc[ :, time ] = mkfrc_map[ kind ]( xtraj[ :, time ], val )
        sparse = mkfrc_map[ kind ]( xtraj[ :, time ], val )
        for i,v in sparse.items():
            frc[ i, time ] = v
    return AdjointForcingData( frc )

