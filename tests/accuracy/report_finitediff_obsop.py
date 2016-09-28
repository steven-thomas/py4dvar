# test that the gradient and cost functions of the driver produce accurate results.
# output a report on the finite difference test
from __future__ import print_function
import numpy as np

import _get_root
from fourdvar import _main_driver as dr
import fourdvar.datadef as d
from fourdvar._transform import transform
from fourdvar.util import dim_label as l

#list of ModelOutputData lookups
subset = [ ( 0, i ) for i in l.label_t ]
delta = 1.0

def adj_cast( lookup ):
    #convert ModelOutput lookup into equivalent AdjointForcing lookup
    return lookup

def make_base():
    #return a ModelOutputData holding the baseline value for this test
    return d.ModelOutputData( np.ones(( len( l.label_x ), len( l.label_t ) )) )

def display( pert_array, grad_array ):
    #user defined output
    abs_diff = np.abs( pert_array - grad_array )
    rel_diff = 2*abs_diff / np.abs( pert_array + grad_array )
    print( 'pert_array: ' + ', '.join( '{:>6.3}'.format( val ) for i,val in enumerate( pert_array ) ) )
    print( 'grad_array: ' + ', '.join( '{:>6.3}'.format( val ) for i,val in enumerate( grad_array ) ) )
    print( 'abs_diff  : ' + ', '.join( '{:>6.3}'.format( val ) for i,val in enumerate( abs_diff ) ) )
    print( 'rel_diff  : ' + ', '.join( '{:>6.2%}'.format( val ) for i,val in enumerate( rel_diff ) ) )
    return None

base_in = make_base()
base_obs = transform( base_in, d.ObservationData )
grad = transform( base_obs, d.AdjointForcingData )

base_score = 0.5 * base_obs.sum_square()

pert_list = []
grad_list = []
for i in subset:
    pert_in = make_base()
    val = pert_in.get_value( i )
    pert_in.set_value( i, val + delta )
    pert_obs = transform( pert_in, d.ObservationData )
    pert_score = 0.5 * pert_obs.sum_square()
    grad_score = base_score + delta * grad.get_value( adj_cast( i ) )
    pert_list.append( pert_score )
    grad_list.append( grad_score )

display( np.array( pert_list ), np.array( grad_list ) )

