
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, UnknownData

def condition( physical ):
    #apply pre-conditioning and vectorize input
    return UnknownData( physical.data.copy() )

