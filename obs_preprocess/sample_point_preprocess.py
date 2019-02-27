
import os

import context
from obs_preprocess.obs_defn import ObsSimple
from obs_preprocess.model_space import ModelSpace
import fourdvar.util.file_handle as fh
import fourdvar.params.input_defn as input_defn

# save new obs file as fourdvar input file
save_file = input_defn.obs_file
fh.ensure_path( os.path.dirname( save_file ) )

# define the parameters of the test observations (2 obs in this example)
#             coordinate format for observations is
#             (    date, timestep, layer, row, column, species, )
obs_coord = [ (20070610,        6,     0,  12,     12,   'CO2', ),
              (20070610,       12,     0,  12,     12,   'CO2', ) ]
# concentration of observation (ppm)
obs_val = [ 400.,
            400. ]
# uncertainty of observation (ppm)
obs_unc = [ 1.,
            1. ]

# make obs file using above parameters & fourdvar-CMAQ model
model_grid = ModelSpace.create_from_fourdvar()
obslist = [ model_grid.get_domain() ]
for coord, val, unc in zip( obs_coord, obs_val, obs_unc ):
    obs = ObsSimple.create( coord, val, unc )
    obs.model_process( model_grid )
    obslist.append( obs.get_obsdict() )
fh.save_list( obslist, save_file )
print 'observations saved to {:}'.format( save_file )
