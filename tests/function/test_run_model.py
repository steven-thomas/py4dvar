#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import ModelInputData, ModelOutputData
from fourdvar.transfunc.run_model import run_model

msg = 'transfunc {0} must output an instance of {1}'
out = run_model( ModelInputData.example() )
assert isinstance( out, ModelOutputData ), msg.format( 'run_model', 'ModelOutputData' )

