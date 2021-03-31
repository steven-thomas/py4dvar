"""
_main_driver.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize

from fourdvar import datadef as d
from fourdvar._transform import transform
from fourdvar import user_driver

import setup_logging
logger = setup_logging.get_logger( __file__ )

use_qc = False

def cost_func( vector ):
    """
    framework: cost function used by minimizer
    input: numpy.ndarray
    output: scalar
    """
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
    if use_qc is True:
        #prior probability of gross error in obs
        perr = np.array([ m.get('perr',0) for m in residual.misc_meta ])
        #half width of gross error uniform dist.
        dlen = np.array([ m.get('dlen',1) for m in residual.misc_meta ])
        
        gamma = np.sqrt(2*np.pi) * perr / (2.*dlen*(1-perr))
        g_exp_vec = gamma + np.exp( -0.5*res_vector*wres_vector )
        ob_cost = np.sum( -np.log(g_exp_vec/(gamma+1.)) )
    else:
        ob_cost = 0.5 * np.sum( res_vector * wres_vector )
    cost = bg_cost + ob_cost
    
    unknown.cleanup()
    physical.cleanup()
    model_in.cleanup()
    model_out.cleanup()
    simulated.cleanup()
    residual.cleanup()
    w_residual.cleanup()
    
    logger.info( 'cost = {}'.format( cost ) )
    
    return cost

def gradient_func( vector ):
    """
    framework: gradient function used by minimizer
    input: numpy.ndarray
    output: numpy.ndarray
    """
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

    if use_qc is True:
        res_vector = residual.get_vector()
        wres_vector = w_residual.get_vector()
        #prior probability of gross error in obs
        perr = np.array([ m.get('perr',0) for m in residual.misc_meta ])
        #half width of gross error uniform dist.
        dlen = np.array([ m.get('dlen',1) for m in residual.misc_meta ])
        
        gamma = np.sqrt(2*np.pi) * perr / (2.*dlen*(1-perr))
        g_exp_vec = gamma + np.exp( -0.5*res_vector*wres_vector )
        qc_weight = 1-gamma/g_exp_vec

        # down-weight obs rel. to probability of gross error.
        obs_grad_vec = wres_vector * qc_weight
        obs_grad = d.ObservationData( obs_grad_vec )
    else:
        obs_grad = w_residual
        
    adj_forcing = transform( obs_grad, d.AdjointForcingData )
    model_sensitivity = transform( adj_forcing, d.SensitivityData )
    physical_sensitivity = transform( model_sensitivity, d.PhysicalAdjointData )
    unknown_gradient = transform( physical_sensitivity, d.UnknownData )
    bg_vector = bg_unknown.get_vector()
    un_vector = unknown.get_vector()
    bg_grad = un_vector - bg_vector
    gradient = bg_grad + unknown_gradient.get_vector()
    logger.info( 'gradient norm = {}'.format( np.linalg.norm(gradient) ) )
    unknown.cleanup()
    physical.cleanup()
    model_in.cleanup()
    model_out.cleanup()
    simulated.cleanup()
    residual.cleanup()
    w_residual.cleanup()
    adj_forcing.cleanup()
    model_sensitivity.cleanup()
    physical_sensitivity.cleanup()
    unknown_gradient.cleanup()
    
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

