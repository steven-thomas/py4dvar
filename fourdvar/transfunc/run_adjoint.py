
import numpy as np

import _get_root
from fourdvar.datadef import AdjointForcingData, SensitivityData
from fourdvar.util.dim_label import label_x, label_t, deltat

def run_adjoint( adjoint_forcing ):
    #run the adjoint model
    
    #ensure data formats are compatible with this function
    if adjoint_forcing.label_x != label_x or adjoint_forcing.label_t != label_t:
        raise TypeError( 'invalid AdjointForcingData for run_adjoint transform.' )
    if SensitivityData.label_x != label_x or SensitivityData.label_t != label_t:
        raise TypeError( 'invalid SensitivityData for run_adjoint transform.' )
    
    frc = adjoint_forcing.frc
    d_icon = frc.sum(axis=1)
    d_emis = deltat * frc[ :, ::-1 ].cumsum( axis=1 )[ :, ::-1 ]
        
    return SensitivityData( d_icon, d_emis )

