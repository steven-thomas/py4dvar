
import numpy as np

import _get_root
from fourdvar.datadef import ModelOutputData, ObservationData
from fourdvar.libshare.obs_handle import obsop_map, obs_param

def obs_operator( model_output ):
    #simulate the observation set from model output
    arglist = []
    for param in obs_param:
        val = obsop_map[ param['kind'] ]( model_output.data[ :, param['time'] ] )
        d = param.copy()
        d['value'] = val
        arglist.append( d )
    return ObservationData( arglist )

