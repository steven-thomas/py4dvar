"""
application: driver functions that require user definition
handles driver IO and the minimizer function
"""

from __future__ import print_function

import numpy as np
import sys
import os
import shutil
import cPickle as pickle
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
from fourdvar import datadef as d
import fourdvar.util.archive_handle as archive
import fourdvar.libshare.cmaq_handle as cmaq

data_dir = '/home/563/spt563/fourdvar/cmaq_vsn1/fourdvar/data/truth'
observed = None
background = None

def setup():
    """
    application: setup any requirements for minimizer to run (eg: check resources, etc.)
    input: None
    output: None
    """
    archive.setup()
    bg = get_background()
    obs = get_observed()
    bg.archive( 'background' )
    obs.archive( 'observed' )
    return None

def cleanup():
    """
    application: cleanup any unwanted output from minimizer (eg: delete checkpoints, etc.)
    input: None
    output: None
    """
    cmaq.wipeout()
    return None

def get_background():
    """
    application: get the background / prior estimate for the minimizer
    input: None
    output: PhysicalData (prior estimate)
    """
    global background
    global data_dir
    
    #bg_file = 'os.path.join( data_dir, 'prior.ncf' )
    bg_file = os.path.join( data_dir, 'prior_CO2only_4day.ncf' )
    
    if background is None:
        background = d.PhysicalData.from_file( bg_file )
    return background

def get_observed():
    """
    application: get the observed observations for the minimizer
    input: None
    output: ObservationData
    """
    global observed
    global data_dir
    
    obs_file = os.path.join( data_dir, 'obsvals_truth.pickle' )
    
    if observed is None:
        observed = d.ObservationData.from_file( obs_file )
    return observed

def minim( cost_func, grad_func, init_guess ):
    """
    application: the minimizer function
    input: cost function, gradient function, prior estimate / background
    output: list (1st element is numpy.ndarray of solution, the rest are user-defined)
    """
    start_cost = cost_func( init_guess )
    start_grad = grad_func( init_guess )
    start_dict = {'start_cost': start_cost, 'start_grad': start_grad }
    
    answer = minimize( cost_func, init_guess, grad_func )
    #check answer warnflag, etc for success
    answer = list( answer ) + [ start_dict ]
    return answer

def post_process( out_physical, metadata ):
    """
    application: how to handle/save results of minimizer
    input: PhysicalData (solution), list (user-defined output of minim)
    output: None
    """
    out_physical.archive( 'final_solution.ncf' )
    with open( os.path.join( archive.get_archive_path(), 'ans_details.pickle' ), 'w' ) as f:
        pickle.dump( metadata, f )
    return None
