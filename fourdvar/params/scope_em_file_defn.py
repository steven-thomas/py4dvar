"""
scope_em_file_defn.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os

from fourdvar.params.root_path_defn import store_path

em_path = os.path.join( store_path, 'emulate' )

#structure of vector scope / emulation input
em_input_struct_fname = os.path.join( em_path, 'test_input_alex_v2.pic' )

#list of emulation files, one for each model index
emulation_fname_list = [
    os.path.join( em_path, 'test_emulate_alex_v2.npz' )
]
