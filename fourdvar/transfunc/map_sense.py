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
    sensitivity.value #list of arrays

    em_struct = [ EmulationInput.load( fname ) for fname in em_input_struct_fname ]

    sensitivity.coord
    sensitivity.model_index

    target_vals = []
    for s_val, mod_i, p_size in zip( sensitivity.value,
                                     sensitivity.model_index,
                                     d.PhysicalAdjointData.size ):
        si,pi = 0,0
        p_arr = np.zeros( p_size )
        var_meta = em_struct[ mod_i ]
        for var_dict in var_meta.var_param:
            #only add target data to the PhysicalData input
            size = var_dict['size']
            if var_dict['is_target']:
                p_arr[pi:pi+size] = s_val.flatten()[si:si+size]
                pi += size
            si += size
        assert pi == p_size, 'Missed target data'
        assert si == s_val.size, 'Missed source data'
        target_vals.append( p_arr )
    
    return d.PhysicalAdjointData( target_vals )
