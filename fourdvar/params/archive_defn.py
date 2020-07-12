"""
archive_defn.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
import _get_root

from fourdvar.params.root_path_defn import root_path

#Settings for archive processes

#location of archive directory
archive_path = os.path.join( root_path, 'SHORT_LN/archive' )

#experiment name & name of directory to save results in
experiment = 'example_experiment'

#description is copied into a txt file in the experiment directory
description = """This is a test of the fourdvar system.
The description here should contain details of the experiment
and is written to the description text file."""
#name of txt file holding the description, if empty string ('') file is not created.
desc_name = 'description.txt'

#if True, delete any existing archive with the same name.
#if False, create a new archive name to save results into.
overwrite = True

#pattern used to create new archive name if overwrite is False
#<E> is replaced with the experiment name
#<I> if replace with a number to make a unique directory name
#if a tag is missing the assumed format is: <E>extension<I>
extension = '<E>_vsn<I>'
