"""
plot_obs_coverage.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
import numpy as np
import datetime
import matplotlib.pyplot as plt

import context
import fourdvar.user_driver as user
import fourdvar.util.date_handle as dt

obs = user.get_observed()

nrow = obs.grid_attr['NROWS']
ncol = obs.grid_attr['NCOLS']
nday = len( dt.get_datelist() )

tstep = obs.grid_attr['TSTEP']
tsec = (tstep//10000)*60*60 + ((tstep//100)%100)*60 + tstep%100
daysec = 24*60*60
nstep = daysec/tsec

coverage = np.zeros((nrow,ncol,),dtype=int)
obs_step = []

skipped_obs = 0
for weight in obs.weight_grid:
    #limit to obs the reach the surface
    if 0 not in [ k[2] for k in weight.keys() ]:
        skipped_obs += 1
        continue
    #assign obs to surface cell with largest weight
    _,obs_coord = max([ (v,k,) for k,v in weight.items() if k[2]==0 ])
    d,t,_,r,c,_ = obs_coord
    coverage[r,c] += 1
    date = datetime.datetime.strptime( str( d ), '%Y%m%d' ).date()
    obs_step.append( (date-dt.start_date).days*nstep + t )
if skipped_obs > 0:
    print( '{:} non-surface obs were omitted.' )

omax = coverage.max()

fig = plt.figure( figsize=(10,5) )
plt.subplot(121)
plt.title( '# of observations for each surface gridcell' )
cov = plt.pcolormesh( coverage, vmin=0, cmap='Blues',
                      edgecolor='k', linestyle=':', linewidth=.1 )
cbar = plt.colorbar()
cbar.set_label('# of observations')
cbar.set_ticks( range(0,omax,max(1,omax//5)) )

plt.subplot(122)
plt.title( '# of observations for each timestep' )
plt.hist( obs_step, bins=[ i+.5 for i in range(nday*nstep+1) ] )
plt.xlim(0,nday*nstep+1)
plt.xticks( [ nstep/2 + nstep*i for i in range(nday) ],
            [ dt.replace_date('<YYYY-MM-DD>',d) for d in dt.get_datelist() ] )
for i in range(1,nday):
    plt.axvline( i*nstep, ls=':', c='k' )
plt.show()
