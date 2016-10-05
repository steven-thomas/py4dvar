# NOT FOR USER MODIFICATION
# extractable data abstract class for data which must be accessable in a vector form

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.datadef.abstract._single_data import SingleData

class ExtractableData( FourDVarData ):
    """This is the abstract class for data stuctures that are examined afterwards.
    This must contain of a list of DataSingle objects to be returned as a vector.
    """
    require = FourDVarData.add_require( 'dataset' )
    
    def __init__( self, dataset ):
        """dataset is a list of instances that subclass SingleData"""
        
        if not np.all( [ isinstance( i, SingleData ) for i in dataset ] ):
            #this is not a valid dataset
            raise Exception( "dataset of extractable must be subclassed from SingleData" )
        
        self.dataset = [ i for i in dataset ]
        
        return None
    
    def get_vector( self, attr='value' ):
        """get requested attribute from DataSingle as a list.
        will return None in place of value if attribute does not exist.
        """
        return [ getattr( single, attr, None ) for single in self.dataset ]

