
# Imports
import os
import glob
import numpy as np
import gp_emulator

import context
from fourdvar.params.root_path_defn import store_path
import fourdvar._main_driver as main
import fourdvar.user_driver as user
import fourdvar.datadef as d
from fourdvar._transform import transform
import emulate_preprocess.p4d_scope_func as scope
import fourdvar.params.scope_em_file_defn as em_file_defn
from fourdvar.util.emulate_input_struct import EmulationInput

src_dir = os.path.join( store_path, 'archive', 'pert_pert_test' )
n_iter = len( glob.glob( os.path.join(src_dir,'iter*.phys') ) )
phys_list = [ os.path.join(src_dir,'iter{:04}.phys'.format(i+1)) for i in range(n_iter) ]

obs_path = os.path.join( src_dir, 'obs_pert.pic.gz' )
user.observed = d.ObservationData.from_file( obs_path )

def run_true_model( model_input ):
    """
    application: run the forward model, save result to ModelOutputData
    input: ModelInputData
    output: ModelOutputData
    """
    output = []
    for val, mod_i in zip( model_input.value, model_input.model_index ):
        input_fname = em_file_defn.em_input_struct_fname[mod_i]
        scope.set_input( input_fname )
        p_out = scope.vector_scope( [val] )
        output.append( p_out )

    return d.ModelOutputData( output, model_input.coord, model_input.model_index )

def cost_func_scope( vector ):
    """
    framework: cost function used by minimizer
    input: numpy.ndarray
    output: scalar
    """
    #set up prior/background and observed data
    bg_physical = user.get_background()
    bg_unknown = transform( bg_physical, d.UnknownData )
    observed = user.get_observed()
    
    unknown = d.UnknownData( vector )
    
    physical = transform( unknown, d.PhysicalData )
    model_in = transform( physical, d.ModelInputData )
    #Swapped out emulated model with the real scope.
    model_out = run_true_model( model_in )
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
    
    #logger.info( 'cost = {}'.format( cost ) )
    
    return cost

emulate_cost = []
scope_cost = []
for fname in phys_list:
    phys = d.PhysicalData.from_file( fname )
    vec = transform( phys, d.UnknownData ).get_vector()
    emulate_cost.append( main.cost_func(vec) )
    scope_cost.append( cost_func_scope(vec) )

print( emulate_cost )
print( scope_cost )
