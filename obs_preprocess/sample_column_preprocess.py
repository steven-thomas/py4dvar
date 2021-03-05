"""
sample_column_preprocess.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os

import context
from obs_preprocess.obs_defn import ObsInstantRay
from obs_preprocess.model_space import ModelSpace
import fourdvar.util.file_handle as fh
import fourdvar.params.input_defn as input_defn

# save new obs file as fourdvar input file
save_file = input_defn.obs_file
fh.ensure_path( os.path.dirname( save_file ) )

# define the parameters of the test observations (1 obs in this example)
obs_param = { 'date': 20070610, # YYYYMMSS
              'time': 60000,    # HHMMSS
              'lat': 34.2,      # latitude
              'lon': -84.0,     # longitude
              'spc': 'CO2',     # species
              'val': 400.,      # concentration (ppm)
              'unc': 1.,        # uncertainty (ppm)
              'interp': False } # interpolate between 2 nearest timesteps

# convert obs_param into needed input units
model_grid = ModelSpace.create_from_fourdvar()
otime = (obs_param['date'],obs_param['time'],)
ox,oy = model_grid.get_xy( obs_param['lat'], obs_param['lon'] )
oloc = ( (ox,oy,0), (ox,oy,model_grid.max_height) )
ospc = obs_param['spc']
oval = obs_param['val']
ounc = obs_param['unc']
ointerp = obs_param['interp']

# make obs file using above parameters & fourdvar-CMAQ model
obslist = [ model_grid.get_domain() ]
obs = ObsInstantRay.create( otime, oloc, ospc, oval, ounc, )
obs.interp_time = ointerp
obs.model_process( model_grid )
obslist = [ model_grid.get_domain(), obs.get_obsdict() ]
fh.save_list( obslist, save_file )
print( 'observations saved to {:}'.format( save_file ) )
