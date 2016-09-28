#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import AdjointForcingData, SensitivityData
from fourdvar.transfunc.run_adjoint import run_adjoint

msg = 'transfunc {0} must output an instance of {1}'
out = run_adjoint( AdjointForcingData.example() )
assert isinstance( out, SensitivityData ), msg.format( 'run_adjoint', 'SensitivityData' )

