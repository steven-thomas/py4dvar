
import numpy as np

import _get_root
from fourdvar.datadef import AdjointForcingData, SensitivityData
from fourdvar.libshare.lorenz_63 import model_ad
from fourdvar.util.dim_defn import x_len
import fourdvar.util.file_handle as fh

def run_adjoint( adjoint_forcing ):
    #run the adjoint model
    assert adjoint_forcing.data.shape[0] == x_len, 'invalid adjoint forcing'
    xtraj = fh.load_array( fh.fnames[ 'ModelOutputData' ] )
    out_data = model_ad( xtraj, adjoint_forcing.data )
    return SensitivityData( out_data )

