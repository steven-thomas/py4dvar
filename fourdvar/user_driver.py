# handles the input and output for the main driver
# also includes the minimizer

from __future__ import print_function

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
from fourdvar import datadef as d
from fourdvar.util.file_handle import rmall

def setup():
    # run at start of get_answer
    return None

def teardown():
    # run at end of get_answer
    rmall()
    return None

def get_background():
    # return the background as a PhysicalData object
    bg_physical = d.PhysicalData.from_file( 'background.csv' )
    return bg_physical

def get_observed():
    #return the observation set as an ObservationData object
    observed = d.ObservationData.from_file( 'observed.csv' )
    return observed

def minim( cost_func, grad_func, init_guess ):
    #the minimizer function
    #return a list, 1st element is minimized vector, all other elements contain metadata passed to display
    
    answer = minimize( cost_func, init_guess, grad_func )
    #check answer warnflag, etc for success
    return answer

def display( out_physical, metadata ):
    #first element has been converted into a PhysicalData object, other elements untouched
    print( '\n\nRESULTS!\n' )
    print( out_physical.data )
    for m in metadata:
        print( m )
    return None

