"""
model_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
# container for optic model data

import os

from fourdvar.params.root_path_defn import store_path

# parameters used for rainfall driver
rd_sample = 12000
rd_f0 = 1.
rd_stand_dev = 0.5
rd_timestep = 10.
rd_filename = os.path.join( store_path, 'optic', 'rainfall_driver.pic.gz' )

rainfall_driver = None #container for rainfall driver array

# parameters for optic model
op_timestep = 1.
op_cur_input = None #container for data needed for optic adjoint
