# input class for the fwd model, generated from PhysicalData

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.dim_defn import x_len

class ModelInputData( InterfaceData ):
    """docstring
    """
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        #data is an array of x_len x-values
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    def get_value( self, i ):
        return self.data[i]
    
    def set_value( self, i, val ):
        self.data[i] = val
        return None
    
    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = 1.0 + np.zeros( x_len )
        return cls( arglist )
    
    @classmethod
    def clone( cls, source ):
        #return a new copy of source, with its own data
        return cls( source.data.copy() )
    
    def cleanup( self ):
        #cleanup any tmp files from a clone
        return None

