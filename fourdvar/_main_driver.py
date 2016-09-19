# NOT FOR USER MODIFICATION
# main driver for 4dvar system, to use from import call the get_answer() function

from __future__ import print_function

import numpy as np
from scipy.optimize import fmin_l_bfgs_b as minimize

import _get_root
from fourdvar import datadef as d
from fourdvar._transform import transform
from fourdvar import user_driver

#set up saved data
bg_physical = user_driver.get_background()
bg_unknown = transform( bg_physical, d.UnknownData )
observed = user_driver.get_observed()

def cost_func( vector ):
    #cost function of minimizer, input must be a numpy array, output a scalar
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
    start_vector = np.array( bg_unknown.get_vector( 'value' ) )
    min_output = user_driver.minim( cost_func, gradient_func, start_vector )
    out_vector = min_output[0]
    out_unknown = d.UnknownData( out_vector )
    out_physical = transform( out_unknown, d.PhysicalData )
    answer = [ out_physical ] + list( min_output[1:] )
    user_driver.display( answer )
    return None

if __name__ == '__main__':
    get_answer()

