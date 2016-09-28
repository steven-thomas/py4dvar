#test that every data class has an example generator

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
import fourdvar.datadef as d
import fourdvar.user_driver as f

def dummy_cost( vector ):
    return 0.5 * np.sum( vector**2 )

def dummy_grad( vector ):
    return vector.copy()

vector = np.array( d.UnknownData.example().get_vector( 'value' ) )
output = f.minim( dummy_cost, dummy_grad, vector )
assert isinstance( output[0], np.ndarray ), 'user_driver.minim()[0] must be a numpy vector'
output = [ d.PhysicalData.example() ] + list( output[1:] )
f.display( output )

