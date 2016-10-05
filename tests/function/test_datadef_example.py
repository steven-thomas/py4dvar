#test that every data class has an example generator

from __future__ import print_function
import numpy as np
import traceback
import sys

import _get_root
import fourdvar.datadef as d

instance_msg = '{0}.example() must return instance of {0}'
require_msg = '{}.has_require() failed'
trace_text = ''
try:
    p0 = d.PhysicalData.example()
    assert isinstance( p0, d.PhysicalData ), instance_msg.format( 'PhysicalData' )
    assert p0.has_require( False ), require_msg.format( 'PhysicalData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p1 = d.UnknownData.example()
    assert isinstance( p1, d.UnknownData ), instance_msg.format( 'UnknownData' )
    assert p1.has_require( True ), require_msg.format( 'UnknownData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p2 = d.ModelInputData.example()
    assert isinstance( p2, d.ModelInputData ), instance_msg.format( 'ModelInputData' )
    assert p2.has_require( False ), require_msg.format( 'ModelInputData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p3 = d.ModelOutputData.example()
    assert isinstance( p3, d.ModelOutputData ), instance_msg.format( 'ModelOutputData' )
    assert p3.has_require( False ), require_msg.format( 'ModelOutputData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p4 = d.ObservationData.example()
    assert isinstance( p4, d.ObservationData ), instance_msg.format( 'ObservationData' )
    assert p4.has_require( True ), require_msg.format( 'ObservationData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p5 = d.AdjointForcingData.example()
    assert isinstance( p5, d.AdjointForcingData ), instance_msg.format( 'AdjointForcingData' )
    assert p5.has_require( False ), require_msg.format( 'AdjointForcingData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'
try:
    p6 = d.SensitivityData.example()
    assert isinstance( p6, d.SensitivityData ), instance_msg.format( 'SensitivityData' )
    assert p6.has_require( False ), require_msg.format( 'SensitivityData' )
except Exception:
    trace_text += traceback.format_exc() + '\n'

if trace_text != '':
    sys.stderr.write( trace_text )
    sys.exit( 1 )

