#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import PhysicalData, ModelInputData
from fourdvar.transfunc.prepare_model import prepare_model

msg = 'transfunc {0} must output an instance of {1}'
out = prepare_model( PhysicalData.example() )
assert isinstance( out, ModelInputData ), msg.format( 'prepare_model', 'ModelInputData' )

