# handles the input and output for the main driver
# also includes the minimizer

from __future__ import print_function

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
from fourdvar import datadef as d
from fourdvar._transform import transform

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
    
    #convert init_guess to array if in other format (PhysicalData/UnknownData)
    if isinstance( init_guess, d.PhysicalData ):
        init_guess = transform( init_guess, d.UnknownData )
    if isinstance( init_guess, d.UnknownData ):
        init_guess = np.array( init_guess.get_vector( 'value' ) )
    if type( init_guess ) != np.ndarray:
        raise TypeError( 'invalid inital guess, must be np.array, PhysicalData or UnknownData' )
    
    answer = minimize( cost_func, init_guess, grad_func )
    #check answer warnflag, etc for success
    return answer

def display( min_output ):
    #first element has been converted into a PhysicalData object, other elements untouched
    phys_out = min_output[0]
    metadata = min_output[1:]
    print( '\n\nRESULTS!\n' )
    print( phys_out.data )
    for m in metadata:
        print( m )
    return None

