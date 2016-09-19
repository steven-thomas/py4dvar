#test that an observation set can load in from a file and be output as a values vector

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import ObservationData

filename = 'observed.csv'

o = ObservationData.from_file( filename )

vals = o.get_vector( 'value' )
print( vals )
assert type(vals) == list
assert len(vals) > 0
assert ( None not in vals )

