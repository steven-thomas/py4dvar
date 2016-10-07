# test that the gradient and cost functions of the driver produce accurate results.
# output a report on the finite difference test
from __future__ import print_function
import numpy as np

import _get_root
from fourdvar import _main_driver as dr
from fourdvar.datadef import UnknownData

subset = [0,1,2]
delta = 0.0001


#base_input = np.array( UnknownData.example().get_vector() )

#DO NOT KEEP THIS, IT IS WRONG!
from fourdvar.user_driver import get_background
base_input = np.array( get_background().data ) + np.random.normal( 0, 1.0, 3 )


base_cost = dr.cost_func( base_input )
grad = dr.gradient_func( base_input )
for i in subset:
    pert_input = base_input.copy()
    pert_input[i] += delta
    pert_cost = dr.cost_func( pert_input )
    grad_cost = base_cost + delta*grad[i]
    abs_diff = abs( pert_cost - grad_cost )
    rel_diff = 2.0 * abs_diff / ( abs( pert_cost ) + abs( grad_cost ) )
    print( 'pert: {}'.format( pert_cost ) )
    print( 'grad: {}'.format( grad_cost ) )
    print( 'abs_diff: {:}'.format( abs_diff ) )
    print( 'rel_diff: {:.0%}\n'.format( rel_diff ) )

