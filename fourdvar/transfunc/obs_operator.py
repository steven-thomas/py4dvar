"""
obs_operator.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import ModelOutputData, ObservationData
import fourdvar.params.model_data as model_data

def obs_operator( model_output ):
    """
    application: simulate set of observations from output of the forward model
    input: ModelOutputData
    output: ObservationData
    """
    if model_data.coord_index is None:
        c_dict = {}
        for i,c in enumerate( model_output.coord ):
            c_dict[ c ] = i
        model_data.coord_index = c_dict
    else:
        c_dict = model_data.coord_index
    
    obs_val_arr = np.zeros( ObservationData.length )
    for obs_i, w_dict in enumerate( ObservationData.weight_grid ):
        for coord, weight in w_dict.items():
            m_ind = c_dict[ coord ]
            m_val = model_output.value[ m_ind ]
            val = ( weight * m_val )
            obs_val_arr[ obs_i ] += val

    return ObservationData( obs_val_arr )
