"""
add_obs_err.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

import context
import fourdvar.util.file_handle as fh
from fourdvar.params.input_defn import obs_file

#obs_file = 'path/to/obs_file.pic.gz' #If modifying other obs

perr = .05 #prior prob of gross error.
dlen = 10. #size of gross error dist. (in sigma)

#add perr and dlen to existing obs file
obs_data = fh.load_list( obs_file )
for odict in obs_data[1:]:
    odict['perr'] = perr
    odict['dlen'] = dlen
fh.save_list( obs_data, obs_file )
