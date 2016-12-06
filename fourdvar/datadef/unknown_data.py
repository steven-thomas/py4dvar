"""
application: structure for the vector handled by the minimizer.
is the pre-conditioned form of physical data, can be converted back and forth via transform function
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

class UnknownSingle( SingleData ):
    """framework: single point in the unknown vector space"""
    def __init__( self, val ):
        """
        framework: create a record for a single unknown
        input: scaler
        output: None
        """
        SingleData.__init__( self, value=val )
        return None


class UnknownData( ExtractableData ):
    """
    application: vector of unknowns/optimization values
    note: all methods except 'clone' are already framework"""
    def __init__( self, vals ):
        """
        framework: create an instance of UnknownData
        input: iterable of scalars (eg: list of floats)
        output: None
        
        eg: new_unknown =  datadef.UnknownData( [ val1, val2, ... ] )
        """
        val_arr = np.array( vals, dtype='float64' )
        dataset = [ UnknownSingle( val ) for val in val_arr ]
        ExtractableData.__init__( self, dataset )
        return None
    
    def perturb( self ):
        """
        framework: change every value by a random amount normally distributed with a standard deviation of 1.
        input: None
        output: None
        
        eg: test_unknown.perturb()
        
        notes: only used for accuracy testing.
               unknowns generated from pre-conditioning will have a covariance error of 1 by construction.
        """
        for item in self.dataset:
            item.value += np.random.normal( 0, 1 )
        return None
    
    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: UnknownData
        
        eg: mock_unknown = datadef.UnknownData.example()
        
        notes: only used for testing.
        """
        #return cls( arglist )
        return None
    
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
        return cls( source.get_vector( 'value' ) )

