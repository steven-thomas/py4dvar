#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import PhysicalData, UnknownData
from fourdvar.transfunc.condition import condition

msg = 'transfunc {0} must output an instance of {1}'
out = condition( PhysicalData.example() )
assert isinstance( out, UnknownData ), msg.format( 'condition', 'UnknownData' )

