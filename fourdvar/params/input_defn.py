
import os

from fourdvar.params.root_path_defn import store_path

#full path to the prior file used by user_driver.get_background
#prior_file = os.path.join( store_path, 'input/prior.ncf' )
prior_file = os.path.join( store_path, 'input/prior_month.nc' )

#full path to the obs file used by user_driver.get_observed
#obs_file = os.path.join( store_path, 'input/obs_oco2.pickle.zip' )
#obs_file = os.path.join( store_path, 'input/test_methane_obs.pic.gz' )
obs_file = os.path.join( store_path, 'input/tropomi_month_obs.pic.gz' )

#include model initial conditions in solution
inc_icon = True
