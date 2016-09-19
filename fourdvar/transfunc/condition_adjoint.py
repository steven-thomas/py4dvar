
import numpy as np

import _get_root
from fourdvar.datadef import SensitivityData, UnknownData
from fourdvar.util.dim_label import label_x, label_t

def condition_adjoint( sensitivity ):
    #convert output of adjoint model into gradient in pre-conditioned unknown space
    
    #ensure data formats are compatible with this function
    if sensitivity.label_x != label_x or sensitivity.label_t != label_t:
        raise TypeError( 'invalid SensitivityData for condition_adjoint transformation' )
    
    d_icon = sensitivity.icon
    d_emis = sensitivity.emis.sum( axis=1 )
    
    val_list = []
    for x in label_x:
        val_list.append( d_icon[ x ] )
        val_list.append( d_emis[ x ] )
    
    return UnknownData( val_list )

