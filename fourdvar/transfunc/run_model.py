
import numpy as np

import _get_root
from fourdvar.datadef import ModelInputData, ModelOutputData
from fourdvar.util.dim_label import label_x, label_t, deltat

def run_model( model_input ):
    #run the forward model
    
    #ensure data formats are compatible with this function
    if model_input.label_x != label_x:
        raise TypeError( 'invalid ModelInputData for run_model transformation' )
    if ModelOutputData.label_x != label_x or ModelOutputData.label_t != label_t:
        raise TypeError( 'invalid ModelOutputData for run_model transformation' )
    
    icon = model_input.icon
    emis = model_input.emis
    
    conc = deltat * emis.cumsum( axis=1 ) + icon.reshape( ( len(label_x), 1 ) )
    
    return ModelOutputData( conc )

