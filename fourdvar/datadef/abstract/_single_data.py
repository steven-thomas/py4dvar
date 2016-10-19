"""
framework: abstract class for single records of an ExtractableData
must contain at least a 'value' attribute
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

class SingleData( FourDVarData ):
    """
    framework:
    This abstract class is for the single instances of the 'extractable' array-like class
    """
    
    #add 'value' to the list of required attributes
    require = FourDVarData.add_require( 'value' )
    
    def __init__( self, value, **kwargs ):
        """
        framework: create an instance of a record
        input: scalar, keyword-values for metadata (arbitrary number of)
        output: None
        
        eg: new_record = datadef.SingleData( value=1.0, category=2, description='whatever you want' )
        """
        
        self.value = value
        [ setattr( self, attr, kwargs[ attr ] ) for attr in kwargs.keys() ]
        
        return None

