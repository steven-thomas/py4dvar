
import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData
from fourdvar.util.dim_label import label_x, label_t, label_i

def calc_forcing( w_residual ):
    #from the weighted residuals of observations calculate the forcing for the adjoint model
    
    #ensure data formats are compatible with this function
    if w_residual.label_i != label_i:
        raise TypeError( 'invalid ObservationData for calc_forcing transformation' )
    if AdjointForcingData.label_x != label_x or AdjointForcingData.label_t != label_t:
        raise TypeError( 'invalid AdjointForcingData for calc_forcing transformation' )
    
    res = np.array( w_residual.get_vector( 'value' ) )
    frc = np.zeros( ( len(label_x), len(label_t) ) )
    av_size = frc[ :, 0:3 ].size
    for val, i in zip( res, label_i ):
        frc[ :, i-1:i+2 ] += val * ( 1.0 / av_size )
    
    return AdjointForcingData( frc )

