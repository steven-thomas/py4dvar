# output conc field of fwd model, created from ModelInputData, fed into observation operator

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.file_handle import save_array, rm
from fourdvar.util.dim_defn import x_len, nstep

class ModelOutputData( InterfaceData ):
    """docstring
    """
    require = InterfaceData.add_require( 'data', 'fname' )
    clone_fname = 'model_out.clone'
    example_fname = 'model_out.example'
    
    def __init__( self, data, fname ):
        #data is a 2d array of x_len, nstep+1 x-values
        InterfaceData.__init__( self )
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, nstep+1 ), 'input data does not match model space'
        self.data = data.copy()
        self.fname = fname
        save_array( self, self.data, self.fname, True )
        return None
    
    def get_value( self, coord ):
        return self.data[ tuple( coord ) ]
    
    def set_value( self, coord, val ):
        self.data[ tuple( coord ) ] = val
        save_array( self, self.data, self.fname, True )
        return None
    
    def sum_square( self ):
        return np.sum( self.data**2 )

    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = 1.0 + np.zeros(( x_len, nstep+1 ))
        return cls( arglist, cls.example_fname )
    
    @classmethod
    def clone( cls, source ):
        #produce another instance with same data as source
        return cls( source.data.copy(), cls.clone_fname )
    
    def cleanup( self ):
        #called when cloned instance is to be removed
        rm( self.fname )
        return None

