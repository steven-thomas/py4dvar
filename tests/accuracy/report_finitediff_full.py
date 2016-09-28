# test that the gradient and cost functions of the driver produce accurate results.
# output a report on the finite difference test
from __future__ import print_function
import numpy as np

import _get_root
from fourdvar import _main_driver as dr
from fourdvar.datadef import UnknownData

base_input = np.array( UnknownData.example().get_vector() )

base_cost = dr.cost_func( base_input )
grad = dr.gradient_func( base_input )

subset = [0,1]
subset = range(len(base_input))
for i in subset:
    pert_input = base_input.copy()
    pert_input[i] += 1
    pert_cost = dr.cost_func( pert_input )
    grad_cost = base_cost + grad[i]
    abs_diff = abs( pert_cost - grad_cost )
    rel_diff = abs_diff / (0.5 * ( pert_cost + grad_cost ) )
    print( 'pert: {}'.format( pert_cost ) )
    print( 'grad: {}'.format( grad_cost ) )
    print( 'abs_diff: {:}'.format( abs_diff ) )
    print( 'rel_diff: {:.0%}\n'.format( rel_diff ) )

