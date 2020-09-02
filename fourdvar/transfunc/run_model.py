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
