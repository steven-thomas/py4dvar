"""
prepare_model.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import PhysicalData, ModelInputData
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.param.scope_em_file_defn import em_input_struct_fname

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """

    em_struct = [ EmulationInput.load( fname ) for fname in em_input_struct_fname ]

    coord = physical_data.coord
    model_index = physical_data.model_index

    m_in_list = []
    for p_val, p_opt, mod_i in zip( physical_data.value, physical_data.option_input,
                                    model_index ):
        vi,oi,mi = 0,0,0
        m_val = np.zeros( p_val.size + p_opt.size )
        var_meta = em_struct[ mod_i ]
        for var_dict in var_meta.var_param:
            size = var_dict['size']
            if var_dict['is_target']:
                m_val[mi:mi+size] = p_val[vi:vi+size]
                vi += size
            else:
                m_val[mi_mi+size] = p_opt[oi:oi+size]
                oi += size
            mi += size
        assert m_val.size == mi, 'Missed model input'
        assert p_val.size == vi, 'Missed target input'
        assert p_opt.size == oi, 'Missed option input'
        m_in_list.append( m_val )
    
    return ModelInputData.create_new( m_in_list, coord, model_index )
