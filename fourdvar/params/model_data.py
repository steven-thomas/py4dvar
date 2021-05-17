"""
model_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os

from fourdvar.params.root_path_defn import store_path

#unknown index mapping file
index_fname = os.path.join( store_path, 'domain', 'index_map.nc' )
#scope model parameter mapping file
param_fname = os.path.join( store_path, 'domain', 'param_map.nc' )

gradient = None

minim_bounds = None
