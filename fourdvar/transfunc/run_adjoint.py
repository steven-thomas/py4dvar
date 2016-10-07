
import numpy as np

import _get_root
from fourdvar.datadef import AdjointForcingData, SensitivityData
from fourdvar.libshare.lorenz_63 import model_ad
from fourdvar.util.dim_defn import x_len
from fourdvar.util.file_handle import load_array

def run_adjoint( adjoint_forcing ):
    #run the adjoint model
    assert adjoint_forcing.data.shape[0] == x_len, 'invalid adjoint forcing'
    xtraj = load_array( label='ModelOutputData' )
    out_data = model_ad( xtraj, adjoint_forcing.data )
    return SensitivityData( out_data )

