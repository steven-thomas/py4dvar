#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData
from fourdvar.transfunc.calc_forcing import calc_forcing

msg = 'transfunc {0} must output an instance of {1}'
out = calc_forcing( ObservationData.example() )
assert isinstance( out, AdjointForcingData ), msg.format( 'calc_forcing', 'AdjointForcingData' )

