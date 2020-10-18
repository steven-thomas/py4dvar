"""
test_cost_verbose.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import time

import context
import fourdvar.datadef as d
from fourdvar._transform import transform
import fourdvar.util.archive_handle as archive
import fourdvar.params.archive_defn as archive_defn
import fourdvar.util.cmaq_handle as cmaq

archive_defn.experiment = 'tmp_cmaq_test'
archive_defn.desc_name = ''

archive_path = archive.get_archive_path()
print 'saving results in:\n{}'.format(archive_path)

model_in = d.ModelInputData()
model_in.archive( 'forward_model_input' )
print 'archived model input.'

print 'run forward model (get concentrations)'
st = time.time()
model_out = transform( model_in, d.ModelOutputData )
print 'completed in {}s'.format( int(time.time() - st) )
model_out.archive( 'forward_model_output' )
print 'archived model output.'

print 'cleanup files produced by CMAQ'
cmaq.wipeout_fwd()

print 'FINISHED!'
