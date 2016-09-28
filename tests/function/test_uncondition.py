#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import UnknownData, PhysicalData
from fourdvar.transfunc.uncondition import uncondition

msg = 'transfunc {0} must output an instance of {1}'
out = uncondition( UnknownData.example() )
assert isinstance( out, PhysicalData ), msg.format( 'uncondition', 'PhysicalData' )

