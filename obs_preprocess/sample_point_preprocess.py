
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
obs_coord = [ (20180801,        6,     0,  12,     12,   'CO', ),
              (20180801,       12,     0,  12,     12,   'CO', ) ]
# concentration of observation (ppm)
obs_val = [ 4.,
            4. ]
# uncertainty of observation (ppm)
obs_unc = [ .01,
            .01 ]

# make obs file using above parameters & fourdvar-CMAQ model
model_grid = ModelSpace.create_from_fourdvar()
domain = model_grid.get_domain()
domain['is_lite'] = False
obslist = [ domain ]
for coord, val, unc in zip( obs_coord, obs_val, obs_unc ):
    obs = ObsSimple.create( coord, val, unc )
    obs.model_process( model_grid )
    obsdict = obs.get_obsdict()
    obsdict['lite_coord'] = coord
    obslist.append( obsdict )
fh.save_list( obslist, save_file )
print 'observations saved to {:}'.format( save_file )
