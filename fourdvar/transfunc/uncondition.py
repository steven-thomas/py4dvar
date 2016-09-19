
import numpy as np

import _get_root
from fourdvar.datadef import UnknownData, PhysicalData
from fourdvar.util.dim_label import label_x

def uncondition( unknown ):
    #undo pre-conditioning and add lost meta-data

    #ensure data formats are compatible with this function
    if label_x != PhysicalData.label_x:
        raise ValueError( 'Physical data does not match this transformation function' )
    val = unknown.get_vector( 'value' )
    
    arg_dict = {}
    for x in label_x:
        icon = val.pop( 0 )
        emis = val.pop( 0 )
        arg_dict[ x ] = [ icon, emis ]
    
    return PhysicalData( arg_dict )

