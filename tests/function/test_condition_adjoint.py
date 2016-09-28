#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import SensitivityData, UnknownData
from fourdvar.transfunc.condition_adjoint import condition_adjoint

msg = 'transfunc {0} must output an instance of {1}'
out = condition_adjoint( SensitivityData.example() )
assert isinstance( out, UnknownData ), msg.format( 'condition_adjoint', 'UnknownData' )

