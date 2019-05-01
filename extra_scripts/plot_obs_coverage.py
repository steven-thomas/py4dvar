
import os
import numpy as np
import matplotlib.pyplot as plt

import context
import fourdvar.datadef as d
import fourdvar.user_driver as user
import fourdvar.params.input_defn as input_defn
from fourdvar.params.root_path_defn import store_path

obs = user.get_observed()

nrow = obs.grid_attr['NROWS']
ncol = obs.grid_attr['NCOLS']

coverage = np.zeros((nrow,ncol,),dtype=int)

skipped_obs = 0
for weight in obs.weight_grid:
    #limit to obs the reach the surface
    if 0 not in [ k[2] for k in weight.keys() ]:
        skipped_obs += 1
        continue
    #assign obs to surface cell with largest weight
    _,obs_coord = max([ (v,k,) for k,v in weight.items() if k[2]==0 ])
    #only need the row & col of the obs
    r,c = (obs_coord[3],obs_coord[4],)
    coverage[r,c] += 1
if skipped_obs > 0:
    print '{:} non-surface obs were omitted.'

omax = coverage.max()

plt.title( '# of observations for each surface gridcell' )
cov = plt.pcolormesh( coverage, vmin=0, cmap='Blues' )
cbar = plt.colorbar()
cbar.set_label('# of observations')
cbar.set_ticks( range(0,omax,max(1,omax//5)) )
plt.show()
