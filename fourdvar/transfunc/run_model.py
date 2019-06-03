"""
application: run the forward model, save result to ModelOutputData
like all transform in transfunc this is referenced from the transform function
eg: transform( model_input_instance, datadef.ModelOutputData ) == run_model( model_input_instance )
"""

import numpy as np

from fourdvar.datadef import ModelInputData, ModelOutputData
import fourdvar.util.cmaq_handle as cmaq
import setup_logging

logger = setup_logging.get_logger( __file__ )

def run_model( model_input ):
    """
    application: run the forward model, save result to ModelOutputData
    input: ModelInputData
    output: ModelOutputData
    """
    #run the forward model
    assert isinstance( model_input, ModelInputData )
    cmaq.wipeout_fwd()
    cmaq.run_fwd()
    try:
        output = ModelOutputData()
    except AssertionError as assert_error:
        logger.error( 'cmaq_fwd_failed. logs exported.' )
        raise assert_error
    return ModelOutputData()
