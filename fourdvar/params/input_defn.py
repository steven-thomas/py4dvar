
import os

import _get_root
from fourdvar.params.root_path_defn import short_path

#full path to the prior file used by user_driver.get_background
prior_file = os.path.join( short_path, 'input/prior.ncf' )

#full path to the obs file used by user_driver.get_observed
obs_file = os.path.join( short_path, 'input/obs_oco2.pickle.zip' )

#include model initial conditions in solution
inc_icon = False
