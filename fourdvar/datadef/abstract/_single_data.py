# NOT FOR USER MODIFICATION
# the single elements of the extractable data set, must have a 'value' provided.

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

class SingleData( FourDVarData ):
    """This abstract class is for the single instances of the 'extractable' array-like class"""
    
    def __init__( self, value, **kwargs ):
        """adds every provided kwarg as an atribute"""
        
        FourDVarData.__init__( self )
        
        self.value = value
        self.required.add( 'value' )
        
        [ setattr( self, attr, kwargs[ attr ] ) for attr in kwargs.keys() ]
        
        return None

