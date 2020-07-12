"""
run_adjoint.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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
