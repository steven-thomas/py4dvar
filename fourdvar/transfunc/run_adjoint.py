"""
application: run the adjoint model, construct SensitivityData from results
like all transform in transfunc this is referenced from the transform function
eg: transform( adjoint_forcing_instance, datadef.SensitivityData ) == run_adjoint( adjoint_forcing_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import AdjointForcingData, SensitivityData, ModelOutputData
from fourdvar.libshare.lorenz_63 import model_ad
from fourdvar.util.dim_defn import x_len
from fourdvar.util.file_handle import read_array

def run_adjoint( adjoint_forcing ):
    """
    application: run the adjoint model, construct SensitivityData from results
    input: AdjointForcingData
    output: SensitivityData
    """
    assert adjoint_forcing.data.shape[0] == x_len, 'invalid adjoint forcing'
    xtraj = read_array( ModelOutputData )
    out_data = model_ad( xtraj, adjoint_forcing.data )
    return SensitivityData( out_data )

