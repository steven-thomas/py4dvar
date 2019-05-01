"""
framework: driver of 4dvar system
"""

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize
import time

from fourdvar import datadef as d
from fourdvar._transform import transform
from fourdvar import user_driver

import setup_logging
logger = setup_logging.get_logger( __file__ )

def cost_func( vector ):
    """
    framework: cost function used by minimizer
    input: numpy.ndarray
    output: scalar
    """
    start_time = time.time()
    #set up prior/background and observed data
    bg_physical = user_driver.get_background()
    bg_unknown = transform( bg_physical, d.UnknownData )
    observed = user_driver.get_observed()
    
    unknown = d.UnknownData( vector )
    
    physical = transform( unknown, d.PhysicalData )
    model_in = transform( physical, d.ModelInputData )
    model_out = transform( model_in, d.ModelOutputData )
    simulated = transform( model_out, d.ObservationData )
    
    residual = d.ObservationData.get_residual( observed, simulated )
    w_residual = d.ObservationData.error_weight( residual )
    
    bg_vector = bg_unknown.get_vector()
    un_vector = unknown.get_vector()
    
    bg_cost = 0.5 * np.sum( ( un_vector - bg_vector )**2 )
    
    res_vector = residual.get_vector()
    wres_vector = w_residual.get_vector()
    ob_cost = 0.5 * np.sum( res_vector * wres_vector )
    cost = bg_cost + ob_cost
    
    unknown.cleanup()
    physical.cleanup()
    model_in.cleanup()
    model_out.cleanup()
    simulated.cleanup()
    residual.cleanup()
    w_residual.cleanup()
    
    end_time = time.time()
    logger.info( 'cost = {:} in {:}s'.format( cost, int(end_time-start_time) ) )
    
    return cost

def gradient_func( vector ):
    """
    framework: gradient function used by minimizer
    input: numpy.ndarray
    output: numpy.ndarray
    """
    start_time = time.time()
    #set up prior/background and observed data
    bg_physical = user_driver.get_background()
    bg_unknown = transform( bg_physical, d.UnknownData )
    observed = user_driver.get_observed()
    
    unknown = d.UnknownData( vector )
    
    physical = transform( unknown, d.PhysicalData )
    model_in = transform( physical, d.ModelInputData )
    model_out = transform( model_in, d.ModelOutputData )
    simulated = transform( model_out, d.ObservationData )
    
    residual = d.ObservationData.get_residual( observed, simulated )
    w_residual = d.ObservationData.error_weight( residual )
    
    adj_forcing = transform( w_residual, d.AdjointForcingData )
    sensitivity = transform( adj_forcing, d.SensitivityData )
    phys_sense = transform( sensitivity, d.PhysicalAdjointData )
    un_gradient = transform( phys_sense, d.UnknownData )
    
    bg_vector = bg_unknown.get_vector()
    un_vector = unknown.get_vector()
    bg_grad = un_vector - bg_vector
    gradient = bg_grad + un_gradient.get_vector()
    
    unknown.cleanup()
    physical.cleanup()
    model_in.cleanup()
    model_out.cleanup()
    simulated.cleanup()
    residual.cleanup()
    w_residual.cleanup()
    adj_forcing.cleanup()
    sensitivity.cleanup()
    phys_sense.cleanup()
    un_gradient.cleanup()

    end_time = time.time()
    logger.info( 'gradient norm = {:} in {:}s'.format( np.linalg.norm(gradient),
                                                       int(end_time-start_time) ) )
    
    return np.array( gradient )

def get_answer():
    """
    framework: run the minimizer & display results from user_driver module
    input: None
    output: None (user_driver.display should print/save output as desired)
    """
    #set up background unknowns
    bg_physical = user_driver.get_background()
    bg_unknown = transform( bg_physical, d.UnknownData )
    
    user_driver.setup()
    start_vector = bg_unknown.get_vector()
    min_output = user_driver.minim( cost_func, gradient_func, start_vector )
    out_vector = min_output[0]
    out_unknown = d.UnknownData( out_vector )
    out_physical = transform( out_unknown, d.PhysicalData )
    user_driver.post_process( out_physical, min_output[1:] )
    out_unknown.cleanup()
    out_physical.cleanup()
    user_driver.cleanup()
    return None

