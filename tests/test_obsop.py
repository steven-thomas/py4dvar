#test that the observation operator transformation runs

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import ModelOutputData, ObservationData
from fourdvar._transform import transform
from fourdvar.util.dim_label import label_x, label_t

conc = np.ones( ( len( label_x ), len( label_t ) ) )
m_out = ModelOutputData( conc )
obs_data = transform( m_out, ObservationData )
obs = np.array( obs_data.get_vector( 'value' ) )

print( obs )
assert np.all( abs( obs - 1.0 ) < 1e-8 )

