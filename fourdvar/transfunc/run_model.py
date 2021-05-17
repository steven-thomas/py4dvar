"""
run_model.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
import gp_emulator

from fourdvar.datadef import ModelInputData, ModelOutputData
from fourdvar.params.scope_em_file_defn import emulation_fname_list
import fourdvar.params.model_data as model_data
import fourdvar.util.netcdf_handle as ncf
import setup_logging

logger = setup_logging.get_logger( __file__ )

def run_model( model_input ):
    """
    application: run the forward model, save result to ModelOutputData
    input: ModelInputData
    output: ModelOutputData
    """
    gp_list =[ gp_emulator.GaussianProcess( emulator_file=f )
               for f in emulation_fname_list ]
    model_map = ncf.get_variable( model_data.param_fname, 'MODEL_MAP' )
    (ninput,nrow,ncol,) = model_input.value.shape
    output = np.zeros( model_map.shape )
    gradient = np.zeros( model_input.value.shape )
    for r in range(nrow):
        for c in range(ncol):
            gp = gp_list[ model_map[r,c] ]
            em_in = np.array( model_input.value[:,r,c] ).reshape((1,-1))
            p_out = gp.predict( em_in, do_deriv=True, do_unc=True )
            output[r,c] = p_out[0][0]
            #uncertainty = p_out[1]
            gradient[:,r,c] = p_out[2][:]

    model_data.gradient = gradient

    return ModelOutputData( output )
