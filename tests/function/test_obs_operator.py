#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import ModelOutputData, ObservationData
from fourdvar.transfunc.obs_operator import obs_operator

msg = 'transfunc {0} must output an instance of {1}'
out = obs_operator( ModelOutputData.example() )
assert isinstance( out, ObservationData ), msg.format( 'obs_operator', 'ObservationData' )

