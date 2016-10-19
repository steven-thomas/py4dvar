# test that the run_adjoint transform matches the run_model transform.
# output a report on the finite difference test
from __future__ import print_function
import numpy as np

import _get_root
from fourdvar import _main_driver as dr
import fourdvar.datadef as d
from fourdvar._transform import transform
from fourdvar.util.dim_defn import x_len

#list of ModelInputData lookups
subset = [ i for i in range( x_len ) ]
#size of perturbation
delta = 0.000001

#convert ModelInput lookup into equivalent Sensitivity lookup
def sense_cast( lookup ):
    return lookup

#how to output the results
def display( results ):
    #user defined output
    print( 'pert_array: ' + ', '.join( '{:>6.3}'.format( val )
          for i,val in enumerate( results['pert_score'] ) ) )
    print( 'grad_array: ' + ', '.join( '{:>6.3}'.format( val )
          for i,val in enumerate( results['grad_score'] ) ) )
    print( 'abs_diff  : ' + ', '.join( '{:>6.3}'.format( val )
          for i,val in enumerate( results['abs_diff'] ) ) )
    print( 'rel_diff  : ' + ', '.join( '{:>6.2%}'.format( val )
          for i,val in enumerate( results['rel_diff'] ) ) )
    return None


base_in = d.ModelInputData.example()
base_out = transform( base_in, d.ModelOutputData )
grad_in = d.AdjointForcingData.from_model( base_out )
grad = transform( grad_in, d.SensitivityData )
base_score = 0.5 * base_out.sum_square()

results = {'pert_score':[], 'grad_score':[], 'abs_diff':[], 'rel_diff':[] }
for i in subset:
    pert_in = d.ModelInputData.clone( base_in )
    val = pert_in.get_value( i )
    pert_in.set_value( i, val + delta )
    pert_out = transform( pert_in, d.ModelOutputData )
    pert_in.cleanup()
    
    pert_score = 0.5 * pert_out.sum_square()
    grad_score = base_score + delta * grad.get_value( sense_cast( i ) )
    abs_diff = abs( pert_score - grad_score )
    rel_diff = abs( 2*abs_diff / ( abs( pert_score ) + abs( grad_score ) ) )
    results['pert_score'].append( pert_score )
    results['grad_score'].append( grad_score )
    results['abs_diff'].append( abs_diff )
    results['rel_diff'].append( rel_diff )
    
    pert_out.cleanup()

display( results )

