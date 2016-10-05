# SensitivityData is the output of the adjoint model, it becomes a gradient in Unknown space

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.dim_defn import x_len

class SensitivityData( InterfaceData ):
    """docstring
    """
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        #data is an array of x_len x-values
        InterfaceData.__init__( self )
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    def get_value( self, i ):
        return self.data[i]
    
    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = 1.0 + np.zeros( x_len )
        return cls( arglist )

