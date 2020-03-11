"""
application: run the forward model, save result to ModelOutputData
like all transform in transfunc this is referenced from the transform function
eg: transform( model_input_instance, datadef.ModelOutputData ) == run_model( model_input_instance )
"""

import numpy as np

from fourdvar.datadef import ModelInputData, ModelOutputData
from fourdvar.util.optic_code import optic_model
import fourdvar.params.model_data as md
import setup_logging

logger = setup_logging.get_logger( __file__ )

def run_model( model_input ):
    """
    application: run the forward model, save result to ModelOutputData
    input: ModelInputData
    output: ModelOutputData
    """
    # store model input for use by adjoint
    md.op_cur_input = model_input
    
    rd_arr = model_input.rainfall_driver
    p = model_input.p
    x = model_input.x
    dt = md.op_timestep
    model_output_arr = optic_model( rd_arr, p, x, dt )
    return ModelOutputData( model_output_arr )
