
import numpy as np

import _get_root
from fourdvar.datadef import UnknownData, PhysicalData

def uncondition( unknown ):
    #undo pre-conditioning and add lost meta-data
    return PhysicalData( unknown.get_vector( 'value' ) )

