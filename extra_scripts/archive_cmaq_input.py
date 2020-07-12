"""
archive_cmaq_input.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import context
import fourdvar.util.archive_handle as archive_handle
import fourdvar.params.archive_defn as archive_defn
import fourdvar.datadef as d

# archive file name
archive_fname = 'original_CMAQ_input'

archive_handle.archive_path = archive_defn.archive_path
archive_handle.finished_setup = True

model_input = d.ModelInputData()
model_input.archive( archive_fname )
