"""
make_prior.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

import context
import fourdvar.util.file_handle as fh
from fourdvar.params.input_defn import prior_file

params = np.array([1.,1.,0.2,0.1])
s0 = 0.01
x0 = np.array([0.,0.])
uncertainty = 0.1 * params

datalist = [ params, s0, x0, uncertainty ]
fh.save_list( datalist, prior_file )
