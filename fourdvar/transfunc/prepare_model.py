
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, ModelInputData

def prepare_model( physical_data ):
    #produce model input from inital physical definitions
    return ModelInputData( physical_data.data.copy() )

