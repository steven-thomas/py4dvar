"""
calc_forcing.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData
import fourdvar.util.cmaq_handle as cmaq

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    
    kwargs = AdjointForcingData.get_kwargs_dict()
    for ymd, ilist in ObservationData.ind_by_date.items():
        spc_dict = kwargs[ 'force.'+ymd ]
        for i in ilist:
            for coord,weight in ObservationData.weight_grid[i].items():
                if str( coord[0] ) == ymd:
                    step,lay,row,col,spc = coord[1:]
                    w_val = w_residual.value[i] * weight
                    spc_dict[spc][step,lay,row,col] += w_val

    cmaq.wipeout_bwd()
    
    return AdjointForcingData.create_new( **kwargs )
