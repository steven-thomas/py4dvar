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
import fourdvar.util.netcdf_handle as ncf

def obs_operator( model_output ):
    """
    application: simulate set of observations from output of the forward model
    input: ModelOutputData
    output: ObservationData
    """
    
    ObservationData.assert_params()
    
    val_list = [ o for o in ObservationData.offset_term ]
    for ymd, ilist in ObservationData.ind_by_date.items():
        conc_file = model_output.file_data['conc.'+ymd]['actual']
        var_dict = ncf.get_variable( conc_file, ObservationData.spcs )
        for i in ilist:
            for coord, weight in ObservationData.weight_grid[i].items():
                if str( coord[0] ) == ymd:
                    step,lay,row,col,spc = coord[1:]
                    conc = var_dict[spc][step,lay,row,col]
                    val_list[i] += (weight * conc)
    
    return ObservationData( val_list )
