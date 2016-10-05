
import numpy as np

import _get_root
from fourdvar.datadef import SensitivityData, UnknownData

def condition_adjoint( sensitivity ):
    #convert output of adjoint model into gradient in pre-conditioned unknown space
    return UnknownData( sensitivity.data )

