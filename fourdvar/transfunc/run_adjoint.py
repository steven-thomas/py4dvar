"""
application: run the adjoint model, construct SensitivityData from results
like all transform in transfunc this is referenced from the transform function
eg: transform( adjoint_forcing_instance, datadef.SensitivityData ) == run_adjoint( adjoint_forcing_instance )
"""

import numpy as np

from fourdvar.datadef import AdjointForcingData, SensitivityData
from fourdvar.util.optic_code import optic_model_AD
import fourdvar.params.model_data as md

def run_adjoint( adjoint_forcing ):
    """
    application: run the adjoint model, construct SensitivityData from results
    input: AdjointForcingData
    output: SensitivityData
    """
    rd_arr = md.op_cur_input.rainfall_driver
    p = md.op_cur_input.p
    x0 = md.op_cur_input.x
    x_out_AD = adjoint_forcing.value
    dt = md.op_timestep

    sens_p, sens_x = optic_model_AD( rd_arr, p, x0, x_out_AD, dt )
    return SensitivityData( sens_p, sens_x )
