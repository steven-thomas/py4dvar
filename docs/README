"""
README

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

First use guide:

NOTE:
 The CMAQ-adj model and the benchmark data are not included in the Github repository. You will need to obtain these from another source.

To run your first test case you will need to:

1: change the parameter files (fourdvar/params/*.py) of particular importance is:
 - root_path_defn.py
	defines the project and storage directories, update if moving/creating a project.
 - date_defn.py
	defines the start and end dates of the simulation, update is changing the model domain.
 - cmaq_config.py
	defines all the parameters CMAQ will need to run,
	of particular note is all the CMAQ-relevant file paths
the others (template, input & archive) can be usually be left unchanged

2: go to cmaq_preprocess and run (in listed order):
 - make_template.py
	creates template files needed to for py4dvar to generate input files,
	assumes that all the input files defined in cmaq_config (MET, emis, icon, etc) already exist
 - make_prior.py
	creates the prior estimate of the fluxes (and initial conditions if input_defn.inc_icon is True)
	includes modifiable parameters at the start of the file with descriptions.

3: go to obs_preprocess and run one of:
 - sample_point_preprocess.py
	creates a test set of instant, point source observations, with easy to edit values.
 - sample_column_preprocess.py
	creates a test single vertical column observation, with easy to edit values.

4: go to tests and run:
 - test_cost_verbose.py
	runs the cost function logic with a random perturbation in the prior.
 - test_grad_verbose.py
	runs the gradient function logic with a random perturbation in the prior.

5: run the main code via runscript.py
