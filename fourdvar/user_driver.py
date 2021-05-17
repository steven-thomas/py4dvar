"""
user_driver.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from __future__ import print_function

import numpy as np
import os
import pickle
from scipy.optimize import fmin_l_bfgs_b as minimize

import fourdvar.datadef as d
import fourdvar.util.archive_handle as archive
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import em_input_struct_fname
import fourdvar.params.input_defn as input_defn
import fourdvar.params.model_data as md
from fourdvar._transform import transform
import setup_logging
logger = setup_logging.get_logger( __file__ )

observed = None
background = None
iter_num = 0

def setup():
    """
    application: setup any requirements for minimizer to run (eg: check resources, etc.)
    input: None
    output: None
    """
    archive.setup()
    bg = get_background()
    obs = get_observed()
    bg.archive( 'prior.pic' )
    obs.archive( 'observed.pic' )

    em_struct = EmulationInput.load( em_input_struct_fname )
    full_input_name = em_struct.get_list('name')
    input_name = [ name.split('.')[-1] for name in full_input_name ]
    min_list = em_struct.get_list('min_val')
    max_list = em_struct.get_list('max_val')

    min_arr = np.zeros( bg.value.shape )
    max_arr = np.zeros( bg.value.shape )
    for i,name in enumerate(bg.var_name):
        loc = input_name.index(name)
        min_arr[i,:,:] = min_list[loc]
        max_arr[i,:,:] = max_list[loc]
    
    min_phys = d.PhysicalData( min_arr )
    max_phys = d.PhysicalData( max_arr )
    min_vals = transform( min_phys, d.UnknownData ).get_vector()
    max_vals = transform( max_phys, d.UnknownData ).get_vector()
    bounds = [ (min_v,max_v,) for min_v,max_v in zip(min_vals,max_vals) ]
    md.minim_bounds = bounds
    print( bounds )
    return None

def cleanup():
    """
    application: cleanup any unwanted output from minimizer (eg: delete checkpoints, etc.)
    input: None
    output: None
    """
    return None

def get_background():
    """
    application: get the background / prior estimate for the minimizer
    input: None
    output: PhysicalData (prior estimate)
    """
    global background
    
    if background is None:
        background = d.PhysicalData.from_file( input_defn.prior_file )
    return background

def get_observed():
    """
    application: get the observed observations for the minimizer
    input: None
    output: ObservationData
    """
    global observed
    
    if observed is None:
        observed = d.ObservationData.from_file( input_defn.obs_file )
    return observed

def callback_func( current_vector ):
    """
    extension: called once for every iteration of minimizer
    input: np.array
    output: None
    """
    global iter_num
    iter_num += 1
    current_unknown = d.UnknownData( current_vector )
    current_physical = transform( current_unknown, d.PhysicalData )
    current_physical.archive( 'iter{:04}.phys'.format( iter_num ) )
    
    logger.info( 'iter_num = {}'.format( iter_num ) )
    
    return None

def minim( cost_func, grad_func, init_guess ):
    """
    application: the minimizer function
    input: cost function, gradient function, prior estimate / background
    output: list (1st element is numpy.ndarray of solution, the rest are user-defined)
    """
    start_cost = cost_func( init_guess )
    start_grad = grad_func( init_guess )
    start_dict = {'start_cost': start_cost, 'start_grad': start_grad }

    min_arr = np.array([ x[0] for x in md.minim_bounds ])
    max_arr = np.array([ x[1] for x in md.minim_bounds ])
    if (init_guess < min_arr).any() or (init_guess > max_arr).any():
        logger.warn( 'Inital input outside of bounds.' )
    
    answer = minimize( cost_func, init_guess, bounds=md.minim_bounds,
                       fprime=grad_func, callback=callback_func )
    #check answer warnflag, etc for success
    answer = list( answer ) + [ start_dict ]
    return answer

def post_process( out_physical, metadata ):
    """
    application: how to handle/save results of minimizer
    input: PhysicalData (solution), list (user-defined output of minim)
    output: None
    """
    out_physical.archive( 'final_solution.pic' )
    with open( os.path.join( archive.get_archive_path(), 'ans_details.pic' ), 'wb' ) as f:
        pickle.dump( metadata, f )
    return None
