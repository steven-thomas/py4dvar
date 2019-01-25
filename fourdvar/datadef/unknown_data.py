"""
application: structure for the vector handled by the minimizer.
is the pre-conditioned form of physical data, can be converted back and forth via transform function
"""
from __future__ import absolute_import

import numpy as np

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

class UnknownData( FourDVarData ):
    """
    application: vector of unknowns/optimization values
    note: all methods except 'clone' are already framework
    """
    def __init__( self, values ):
        """
        framework: create an instance of UnknownData
        input: iterable of scalars (eg: list of floats)
        output: None
        
        eg: new_unknown =  datadef.UnknownData( [ val1, val2, ... ] )
        """
        self.value_arr = np.array( values, dtype='float64' )
        return None
    
    def get_vector( self ):
        """
        framework: return the values in UnknownData as a 1D numpy array
        input: None
        output: np.ndarray
        """
        return np.array( self.value_arr )
    
    @classmethod
    def clone( cls, source ):
        """
        framework: copy an UnknownData instance
        input: UnknownData
        output: UnknownData
        
        eg: unknown_copy = datadef.UnknownData.clone( current_unknown )
        
        notes: only used for testing.
        """
        assert isinstance( source, cls )
        return cls( source.get_vector() )

