
import numpy as np

import context
import fourdvar.user_driver as user
import fourdvar.datadef as d
from fourdvar._transform import transform
import fourdvar.util.file_handle as fh
from fourdvar.params.input_defn import obs_file

obs_unc_frac = 0.05
obs_unc_floor = 0.01

#single point observations
n_point_obs = 1000

#time averaged observations
n_avg_obs = 100
avg_obs_len = 10

#total carbon observations
n_tot_obs = 500

obs_list = []

phys = user.get_background()
mod_in = transform( phys, d.ModelInputData )
mod_out = transform( mod_in, d.ModelOutputData )
model_arr = mod_out.value
nt,nx = model_arr.shape

#create point observations
point_t = np.random.randint( 0, nt, n_point_obs )
point_x = np.random.randint( 0, nx, n_point_obs )
for t,x in zip(point_t,point_x):
    value = model_arr[t,x]
    uncertainty = max( abs(value*obs_unc_frac), obs_unc_floor )
    odict = { 'type': 'single point',
              'value': value,
              'uncertainty': uncertainty,
              'weight_grid': {(t,x,): 1.} }
    obs_list.append( odict )

#create time averaged observations
avg_t = np.random.randint( 0, nt-avg_obs_len, n_avg_obs )
avg_x = np.random.randint( 0, nx, n_avg_obs )
for t,x in zip(avg_t,avg_x):
    value = model_arr[t:t+avg_obs_len,x].mean()
    uncertainty = max( abs(value*obs_unc_frac), obs_unc_floor )
    w = 1. / float(avg_obs_len)
    odict = { 'type': 'time average',
              'value': value,
              'uncertainty': uncertainty,
              'weight_grid': {(t+i,x,): w for i in range(avg_obs_len)} }
    obs_list.append( odict )

#create total carbon observations
tot_t = np.random.randint( 0, nt, n_tot_obs )
for t in tot_t:
    value = model_arr[t,:].sum()
    uncertainty = max( abs(value*obs_unc_frac), obs_unc_floor )
    odict = { 'type': 'time average',
              'value': value,
              'uncertainty': uncertainty,
              'weight_grid': {(t,i,): 1. for i in range(nx)} }
    obs_list.append( odict )

fh.save_list( obs_list, obs_file )
