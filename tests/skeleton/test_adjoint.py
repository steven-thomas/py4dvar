#test that the adjoint transformation runs

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import AdjointForcingData, SensitivityData
from fourdvar._transform import transform
from fourdvar.util.dim_label import label_x, label_t

len_x = len( label_x )
len_t = len( label_t )

frc = np.ones( ( len_x, len_t ) )
frc_data = AdjointForcingData( frc )
sense = transform( frc_data, SensitivityData )

d_icon = sense.icon
d_emis = sense.emis
print( d_icon )
print( d_emis )

assert abs( np.sum( frc ) - np.sum( d_icon ) ) < 1e-8

emis_sum = len_t * (len_t + 1) * 1.0/2.0 * len_x
assert abs( np.sum( d_emis ) - emis_sum ) < 1e-8

