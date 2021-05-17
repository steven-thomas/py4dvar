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
from fourdvar.params.scope_em_file_defn import em_input_struct_fname
from fourdvar.params.model_data import param_fname
import fourdvar.util.netcdf_handle as ncf

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """

    em_struct = EmulationInput.load( em_input_struct_fname )

    var_arr = physical_data.value
    var_name = physical_data.var_name
    par_arr = ncf.get_variable( param_fname, 'PARAM_MAP' )
    par_name = ncf.get_attr( param_fname, 'PAR_LIST' )

    full_input_name = em_struct.get_list('name')
    input_name = [ name.split('.')[-1] for name in full_input_name ]

    mod_in_arr = np.zeros( (len(input_name), var_arr.shape[1], var_arr.shape[2]) )
    for i,name in enumerate( input_name ):
        if name in var_name:
            loc = var_name.index(name)
            src_arr = var_arr[loc,:,:]
        elif name in par_name:
            loc = par_name.index(name)
            src_arr = par_arr[loc,:,:]
        else:
            raise ValueError("can't find {:} in value or parameters.".format(name))
        mod_in_arr[i,:,:] = src_arr[:,:]
    
    return ModelInputData.create_new( mod_in_arr, input_name )
