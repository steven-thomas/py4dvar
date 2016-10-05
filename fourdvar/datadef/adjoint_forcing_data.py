# the adjoint forcing serves as input for the adjoint model run, made from the weighted residual of observations

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.dim_defn import x_len, nstep

class AdjointForcingData( InterfaceData ):
    """docstring
    """
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        #data is a 2d array of x_len, nstep+1 x-values
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, nstep+1 ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    def get_value( self, coord ):
        return self.data[ tuple( coord ) ]

    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = 1.0 + np.zeros(( x_len, nstep+1 ))
        return cls( arglist )
    
    @classmethod
    def from_model( cls, m_out ):
        #generate forcing directly from model_output
        return cls( m_out.data.copy() )

