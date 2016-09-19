#test that the entire cost function in the driver runs without error
from __future__ import print_function
import numpy as np

import _get_root
from fourdvar import _main_driver as dr
from fourdvar.datadef import PhysicalData, UnknownData
from fourdvar.util.dim_label import label_x

test_case = {}
for x in label_x:
    test_case[ x ] = (1, 1)

phys = PhysicalData( test_case )
unk = dr.transform( phys, UnknownData )
start = np.array( unk.get_vector() )

cost = float( dr.cost_func( start ) )
print( cost )

