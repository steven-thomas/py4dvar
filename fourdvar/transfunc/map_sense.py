"""
map_sense.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

import fourdvar.datadef as d
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import em_input_struct_fname

def map_sense( sensitivity ):
    """
    application: map adjoint sensitivities to physical grid of unknowns.
    input: SensitivityData
    output: PhysicalAdjointData
    """
    ninput,nrow,ncol = sensitivity.value.shape
    input_name = sensitivity.input_name
    nvar = d.PhysicalAdjointData.nvars
    var_name = d.PhysicalAdjointData.var_name

    adj_arr = np.zeros((nvar,nrow,ncol,))
    for i,name in enumerate(var_name):
        loc = input_name.index(name)
        adj_arr[i,:,:] = sensitivity.value[loc,:,:]
    
    return d.PhysicalAdjointData( adj_arr )
