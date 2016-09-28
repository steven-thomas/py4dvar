#test that ObservationData's weight and get_residual methods work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import ObservationData as Obs

trace_text = ''
msg = '{0}.{{}}() must return instance of {0}'.format( 'ObservationData' )
try:
    p0 = Obs.weight( Obs.example() )
    assert isinstance( p0, Obs ), msg.format( 'weight' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p1 = Obs.get_residual( Obs.example(), Obs.example() )
    assert isinstance( p1, Obs ), msg.format( 'get_residual' )
except Exception:
    trace_text += traceback.format_exc() + '\n'

if trace_text != '':
    sys.stderr.write( trace_text )
    sys.exit( 1 )

