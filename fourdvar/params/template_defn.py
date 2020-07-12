"""
template_defn.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
from fourdvar.params.root_path_defn import store_path

template_path = os.path.join( store_path, 'template' )

#filepaths to template netCDF files used by CMAQ & fourdvar
conc = os.path.join( template_path, 'conc_template.ncf' )
force = os.path.join( template_path, 'force_template.ncf' )
sense_emis = os.path.join( template_path, 'sense_emis_template.ncf' )
sense_conc = os.path.join( template_path, 'sense_conc_template.ncf' )

#fwd model inputs are "records" instead of templates.
emis = os.path.join( template_path, 'record', 'emis_record_<YYYYMMDD>.ncf' )
icon = os.path.join( template_path, 'record', 'icon_record.ncf' )

diurnal = os.path.join( template_path, 'diurnal.ncf' )
