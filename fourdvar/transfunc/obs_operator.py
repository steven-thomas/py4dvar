
import numpy as np

import _get_root
from fourdvar.datadef import ModelOutputData, ObservationData
from fourdvar.util.dim_label import label_x, label_t, label_i

def obs_operator( model_output ):
    #simulate the observation set from model output
    
    #ensure data formats are compatible with this function
    if model_output.label_x != label_x or model_output.label_t != label_t:
        raise TypeError( 'invalid ModelOutputData for obs_operator transform.' )
    if ObservationData.label_i != label_i:
        raise TypeError( 'invalid ObservationData for obs_operator transform.' )
    
    conc = model_output.conc
    attr_list = []
    for i in label_i:
        attr_list.append( [ i, conc[:, i-1:i+2].mean() ] )
    
    return ObservationData( attr_list )

