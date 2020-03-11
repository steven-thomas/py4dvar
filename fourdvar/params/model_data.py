# container for optic model data

import os

from fourdvar.params.root_path_defn import store_path

# parameters used for rainfall driver
rd_sample = 12000
rd_f0 = 1.
rd_stand_dev = 0.5
rd_timestep = 10.
rd_filename = os.path.join( store_path, 'optic', 'rainfall_driver.pic.gz' )

rainfall_driver = None #container for rainfall driver array

# parameters for optic model
op_timestep = 1.
op_cur_input = None #container for data needed for optic adjoint
