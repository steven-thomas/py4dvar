# test that the calc_forcing transform matches the obs_operator transform.
# output a report on the finite difference test
from __future__ import print_function
import numpy as np

import _get_root
from fourdvar import _main_driver as dr
import fourdvar.datadef as d
from fourdvar._transform import transform
from fourdvar.util.dim_defn import x_len, nstep

#list of ModelOutputData lookups
subset = [ ( x, t ) for t in range( 2, nstep, 2 ) for x in range( x_len ) ]
#size of perturbation
delta = 1.0

#convert ModelOutput lookup into equivalent AdjointForcing lookup
def adj_cast( lookup ):
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


base_in = d.ModelOutputData.example()
base_obs = transform( base_in, d.ObservationData )
grad = transform( base_obs, d.AdjointForcingData )
base_score = 0.5 * base_obs.sum_square()

results = {'pert_score':[], 'grad_score':[], 'abs_diff':[], 'rel_diff':[], }
for i in subset:
    pert_in = d.ModelOutputData.clone( base_in )
    val = pert_in.get_value( i )
    pert_in.set_value( i, val + delta )
    pert_obs = transform( pert_in, d.ObservationData )
    pert_in.cleanup()
    
    pert_score = 0.5 * pert_obs.sum_square()
    grad_score = base_score + delta * grad.get_value( adj_cast( i ) )
    abs_diff = abs( pert_score - grad_score )
    rel_diff = abs( 2*abs_diff / ( abs( pert_score ) +  abs( grad_score ) ) )
    results['pert_score'].append( pert_score )
    results['grad_score'].append( grad_score )
    results['abs_diff'].append( abs_diff )
    results['rel_diff'].append( rel_diff )

base_in.cleanup()
display( results )

