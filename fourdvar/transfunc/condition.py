
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, UnknownData
from fourdvar.util.dim_label import label_x

def condition( physical ):
    #apply pre-conditioning and vectorize input
    
    #ensure data formats are compatible with this function
    if label_x != physical.label_x:
        raise ValueError( 'physical data does not match this transform function' )
    val_list = []
    for x in label_x:
        #add icon
        val_list.append( physical.data[ x ][0] )
        #add emis
        val_list.append( physical.data[ x ][1] )
    return UnknownData( val_list )

