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
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import em_input_struct_fname
import fourdvar.params.model_data as md

def run_adjoint( adjoint_forcing ):
    """
    application: run the adjoint model, construct SensitivityData from results
    input: AdjointForcingData
    output: SensitivityData
    """
    em_struct = EmulationInput.load( em_input_struct_fname )
    full_input_name = em_struct.get_list('name')
    input_name = [ name.split('.')[-1] for name in full_input_name ]

    nrow,ncol = adjoint_forcing.value.shape
    frc_arr = adjoint_forcing.value.reshape((1,nrow,ncol,))
    sens = frc_arr * md.gradient

    return SensitivityData( sens, input_name )
