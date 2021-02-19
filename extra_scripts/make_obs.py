
import numpy as np

import context
import fourdvar.util.file_handle as fh
import fourdvar.params.input_defn as input_defn

main_val = 1.0
main_unc = 0.02

nobs = 1000

"""[{'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(0, 0): 1.0}}, {'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(0, 1): 1.0}}, {'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(1, 0): 1.0}}, {'value': 1.0, 'uncertainty': 0.1, 'weight_grid': {(1, 1): 1.0}}]"""


prior = fh.load_list( input_defn.prior_file )
coord_list = [ x['coord'] for x in prior ]

obs_list = []
for coord in coord_list:
    for i in range(nobs):
        obs = { 'value':main_val, 'uncertainty':main_unc, 'weight_grid':{coord:1.0} }
        obs_list.append( obs )
fh.save_list( obs_list, input_defn.obs_file )
