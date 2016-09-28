#test that the calc_forcing transformation runs

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData
from fourdvar._transform import transform
from fourdvar.util.dim_label import label_i

obs = ObservationData( [ ( i, 1 ) for i in label_i ] )
frc_data = transform( obs, AdjointForcingData )

frc = frc_data.frc

print( frc )
#total of forcing == total of weighted residual of observation
assert abs( np.sum( frc ) - len( label_i ) ) < 1e-8

