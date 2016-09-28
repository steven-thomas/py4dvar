#test that every data class has an example generator

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
import fourdvar.datadef as d

msg = '{0}.example() must return instance of {0}'
trace_text = ''
try:
    p0 = d.PhysicalData.example()
    assert isinstance( p0, d.PhysicalData ), msg.format('PhysicalData')
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p1 = d.UnknownData.example()
    assert isinstance( p1, d.UnknownData ), msg.format('UnknownData')
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p2 = d.ModelInputData.example()
    assert isinstance( p2, d.ModelInputData ), msg.format('ModelInputData')
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p3 = d.ModelOutputData.example()
    assert isinstance( p3, d.ModelOutputData ), msg.format('ModelOutputData')
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p4 = d.ObservationData.example()
    assert isinstance( p4, d.ObservationData ), msg.format('ObservationData')
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p5 = d.AdjointForcingData.example()
    assert isinstance( p5, d.AdjointForcingData ), msg.format('AdjointForcingData')
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p6 = d.SensitivityData.example()
    assert isinstance( p6, d.SensitivityData ), msg.format('SensitivityData')
except Exception:
    trace_text += traceback.format_exc() + '\n'

if trace_text != '':
    sys.stderr.write( trace_text )
    sys.exit( 1 )

