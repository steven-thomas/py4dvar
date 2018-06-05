"""
application: run the forward model, save result to ModelOutputData
like all transform in transfunc this is referenced from the transform function
eg: transform( model_input_instance, datadef.ModelOutputData ) == run_model( model_input_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import ModelInputData, ModelOutputData
import fourdvar.util.model_data as model_data
import setup_logging

logger = setup_logging.get_logger( __file__ )

def run_model( model_input ):
    """
    application: run the forward model, save result to ModelOutputData
    input: ModelInputData
    output: ModelOutputData
    """
    # store model input for use by adjoint
    model_data.value = model_input.value
    return ModelOutputData(model_input.value**3)
