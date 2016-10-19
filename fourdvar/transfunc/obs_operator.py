"""
application: simulate set of observations from output of the forward model
like all transform in transfunc this is referenced from the transform function
eg: transform( model_output_instance, datadef.ObservationData ) == obs_operator( model_output_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import ModelOutputData, ObservationData
from fourdvar.libshare.obs_handle import obsop_map

def obs_operator( model_output ):
    """
    application: simulate set of observations from output of the forward model
    input: ModelOutputData
    output: ObservationData
    """
    arglist = []
    for param in ObservationData.param:
        val = obsop_map[ param['kind'] ]( model_output.data[ :, param['time'] ] )
        d = param.copy()
        d['value'] = val
        arglist.append( d )
    return ObservationData( arglist )

