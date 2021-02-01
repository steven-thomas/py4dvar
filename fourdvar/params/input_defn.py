"""
input_defn.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os

from fourdvar.params.root_path_defn import store_path

#full path to the prior file used by user_driver.get_background
prior_file = os.path.join( store_path, 'input/prior.pic.gz' )

#full path to the obs file used by user_driver.get_observed
obs_file = os.path.join( store_path, 'input/test_obs.pic.gz' )
