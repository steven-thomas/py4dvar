
import numpy as np

import context
import fourdvar.datadef as d
from fourdvar._transform import transform
import fourdvar.util.file_handle as fh
import fourdvar.params.input_defn as input_defn

main_val = 1.0
main_unc = 0.02

nobs = 1000

"""[{'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(0, 0): 1.0}}, {'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(0, 1): 1.0}}, {'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(1, 0): 1.0}}, {'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(1, 1): 1.0}}]"""


prior = d.PhysicalData.from_file( input_defn.prior_file )
mod_in = transform( prior, d.ModelInputData )
mod_out = transform( mod_in, d.ModelOutputData )
(nrow,ncol,) = mod_out.value.shape

obs_list = []
unc = .1 * mod_out.value.max()
for r in range(nrow):
    for c in range(ncol):
        obs = { 'value': mod_out.value[r,c], 'uncertainty': unc,
                'weight_grid': {(r,c,):1.0} }
        obs_list.append( obs )

fh.save_list( obs_list, input_defn.obs_file )
