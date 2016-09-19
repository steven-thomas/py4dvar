#test that a physical data set can load in from a file and be output as a values vector

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData

filename = 'background.csv'

p = PhysicalData.from_file( filename )

data = p.data
print( data )
assert type( data ) == dict
assert len( data.keys() ) > 0
for k in data.keys():
    assert len( data[ k ] ) == 2

