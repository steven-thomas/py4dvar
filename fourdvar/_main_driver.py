"""
framework: driver of 4dvar system
"""

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
from fourdvar import datadef as d
from fourdvar._transform import transform
from fourdvar import user_driver

#set up prior/background and observed data
bg_physical = user_driver.get_background()
bg_unknown = transform( bg_physical, d.UnknownData )
observed = user_driver.get_observed()

def cost_func( vector ):
    """
    framework: cost function used by minimizer
    input: numpy.ndarray
    output: scalar
    """
    
    unknown = d.UnknownData( vector )
    
    physical = transform( unknown, d.PhysicalData )
    model_in = transform( physical, d.ModelInputData )
    model_out = transform( model_in, d.ModelOutputData )
    simulated = transform( model_out, d.ObservationData )
    
    residual = d.ObservationData.get_residual( observed, simulated )
    w_residual = d.ObservationData.weight( residual )
    
    bg_vector = np.array( bg_unknown.get_vector( 'value' ) )
    un_vector = np.array( unknown.get_vector( 'value' ) )
    bg_cost = np.sum( ( un_vector - bg_vector )**2 )
    
    res_vector = np.array( residual.get_vector( 'value' ) )
    wres_vector = np.array( w_residual.get_vector( 'value' ) )
    ob_cost = np.sum( res_vector * wres_vector )

    cost = bg_cost + ob_cost
    return cost

def gradient_func( vector ):
    """
    framework: gradient function used by minimizer
    input: numpy.ndarray
    output: numpy.ndarray
    """
    #gradient function of minimizer, input and output must be numpy arrays
    unknown = d.UnknownData( vector )
    
    physical = transform( unknown, d.PhysicalData )
    model_in = transform( physical, d.ModelInputData )
    model_out = transform( model_in, d.ModelOutputData )
    simulated = transform( model_out, d.ObservationData )
    
    residual = d.ObservationData.get_residual( observed, simulated )
    w_residual = d.ObservationData.weight( residual )
    
    adj_forcing = transform( w_residual, d.AdjointForcingData )
    sensitivity = transform( adj_forcing, d.SensitivityData )
    un_gradient = transform( sensitivity, d.UnknownData )
    
    bg_vector = np.array( bg_unknown.get_vector( 'value' ) )
    un_vector = np.array( unknown.get_vector( 'value' ) )
    bg_grad = un_vector - bg_vector
    
    gradient = bg_grad + np.array( un_gradient.get_vector( 'value' ) )
    return np.array( gradient )

def get_answer():
    """
    framework: run the minimizer & display results from user_driver module
    input: None
    output: None (user_driver.display should print/save output as desired)
    """
    user_driver.setup()
    start_vector = np.array( bg_unknown.get_vector( 'value' ) )
    min_output = user_driver.minim( cost_func, gradient_func, start_vector )
    out_vector = min_output[0]
    out_unknown = d.UnknownData( out_vector )
    out_physical = transform( out_unknown, d.PhysicalData )
    user_driver.display( out_physical, min_output[1:] )
    user_driver.cleanup()
    return None

