#test user_driver's get_background and get_observed work

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
import fourdvar.datadef as d
import fourdvar.user_driver as f

trace_text = ''
msg = 'user_driver.{0}() must return an instance of {1}'
try:
    p0 = f.get_background()
    assert isinstance( p0, d.PhysicalData ), msg.format( 'get_background', 'PhysicalData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p1 = f.get_observed()
    assert isinstance( p1, d.ObservationData ), msg.format( 'get_observed', 'ObservationData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'

if trace_text != '':
    sys.stderr.write( trace_text )
    sys.exit( 1 )

