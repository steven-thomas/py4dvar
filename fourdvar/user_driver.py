"""
application: driver functions that require user definition
handles driver IO and the minimizer function
"""

from __future__ import print_function

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
from fourdvar import datadef as d
from fourdvar.util.file_handle import rmall

def setup():
    """
    application: setup any requirements for minimizer to run (eg: check resources, etc.)
    input: None
    output: None
    """
    return None

def cleanup():
    """
    application: cleanup any unwanted output from minimizer (eg: delete checkpoints, etc.)
    input: None
    output: None
    """
    rmall()
    return None

def get_background():
    """
    application: get the background / prior estimate for the minimizer
    input: None
    output: PhysicalData (prior estimate)
    """
    bg_physical = d.PhysicalData.from_file( 'background.csv' )
    return bg_physical

def get_observed():
    """
    application: get the observed observations for the minimizer
    input: None
    output: ObservationData
    """
    observed = d.ObservationData.from_file( 'observed.csv' )
    return observed

def minim( cost_func, grad_func, init_guess ):
    """
    application: the minimizer function
    input: cost function, gradient function, prior estimate / background
    output: list (1st element is numpy.ndarray of solution, the rest are user-defined)
    """
    
    answer = minimize( cost_func, init_guess, grad_func )
    #check answer warnflag, etc for success
    return answer

def display( out_physical, metadata ):
    """
    application: how to display/save results of minimizer
    input: PhysicalData (solution), list (user-defined output of minim)
    output: None
    """
    
    print( '\n\nRESULTS!\n' )
    print( out_physical.data )
    for m in metadata:
        print( m )
    return None

