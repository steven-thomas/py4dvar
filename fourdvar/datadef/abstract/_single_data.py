# NOT FOR USER MODIFICATION
# the single elements of the extractable data set, must have a 'value' provided.

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

class SingleData( FourDVarData ):
    """This abstract class is for the single instances of the 'extractable' array-like class"""
    
    require = FourDVarData.add_require( 'value' )
    
    def __init__( self, value, **kwargs ):
        """adds every provided kwarg as an atribute"""
        
        self.value = value
        [ setattr( self, attr, kwargs[ attr ] ) for attr in kwargs.keys() ]
        
        return None

