"""
run_model.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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
