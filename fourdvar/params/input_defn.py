
import os

from fourdvar.params.root_path_defn import store_path

#full path to the prior file used by user_driver.get_background
prior_file = os.path.join( store_path, 'input/prior.nc' )

#full path to the obs file used by user_driver.get_observed
obs_file = os.path.join( store_path, 'input/test_obs.pic.gz' )
