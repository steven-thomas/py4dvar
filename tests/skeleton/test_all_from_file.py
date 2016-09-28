#test that every data class has an example generator

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
from fourdvar.datadef import ObservationData, PhysicalData

obs_file = 'observed.csv'
phys_file = 'background.csv'

trace_text = ''
try:
    p0 = PhysicalData.from_file( phys_file )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p1 = ObservationData.from_file( obs_file )
except Exception:
    trace_text += traceback.format_exc() + '\n'

if trace_text != '':
    sys.stderr.write( trace_text )
    sys.exit( 1 )

