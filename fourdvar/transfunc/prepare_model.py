
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, ModelInputData
from fourdvar.util.dim_label import label_x, label_t

def prepare_model( physical_data ):
    #produce model input from inital physical definitions
    
    #ensure data formats are compatible with this function
    if physical_data.label_x != label_x:
        raise TypeError( 'PhysicalData invalid for prepare_model transform.' )
    if ModelInputData.label_x != label_x or ModelInputData.label_t != label_t:
        raise TypeError( 'ModelInputData invalid for prepare_model transform.' )
    
    return ModelInputData( physical_data.data )

