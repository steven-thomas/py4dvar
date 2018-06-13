"""
application: driver functions that require user definition
handles driver IO and the minimizer function
"""

from __future__ import print_function

import numpy as np
import os
import cPickle as pickle
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
import fourdvar.datadef as d
import fourdvar.util.archive_handle as archive
import fourdvar.params.input_defn as input_defn
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
    bg.archive( 'prior.pickle' )
    obs.archive( 'observed.pickle' )
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
        background = d.PhysicalData( [-1., -1., -1.] )
        d.PhysicalData.set_unc( np.array( [2.,2.,2.] ) )
    return background

def get_observed():
    """
    application: get the observed observations for the minimizer
    input: None
    output: ObservationData
    """
    global observed
    
    if observed is None:
        observed = d.ObservationData([3.])
        d.ObservationData.unc = np.array([1.]) # setting class variable directly
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
    
    answer = minimize( cost_func, init_guess,
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
    out_physical.archive( 'final_solution.pickle' )
    with open( os.path.join( archive.get_archive_path(), 'ans_details.pickle' ), 'w' ) as f:
        pickle.dump( metadata, f )
    return None
