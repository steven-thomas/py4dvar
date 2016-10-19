"""
framework: abstract class for data structures that must be accessable in a vector form
Used my UnknownData and ObservationData
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.datadef.abstract._single_data import SingleData

class ExtractableData( FourDVarData ):
    """
    framework: abstract class inherited by data structures that are expressable as vectors
    """
    
    #add 'dataset' to list of required attributes
    require = FourDVarData.add_require( 'dataset' )
    
    def __init__( self, dataset ):
        """
        framework: create an instance of ExtractableData
        input: list of SingleData instances
        output: None
        
        notes: the ExtractableData.__init__ method must be called by the __init__ of any child class
        """
        
        if not np.all( [ isinstance( i, SingleData ) for i in dataset ] ):
            #this is not a valid dataset
            raise Exception( "dataset of extractable must be subclassed from SingleData" )
        
        # ensure dataset is a copy, not a reference
        self.dataset = [ i for i in dataset ]
        
        return None
    
    def get_vector( self, attr='value' ):
        """
        framework: get a list of attribute values from SingleData's in dataset
        input: string  (name of desired attribute)
        output: list
        
        eg: simulated_observations.get_vector( 'time' )
        
        notes: will return None in place of value if attribute does not exist.
        """
        return [ getattr( single, attr, None ) for single in self.dataset ]

