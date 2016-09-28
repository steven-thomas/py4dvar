# output conc field of fwd model, created from ModelInputData, fed into observation operator

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData
from fourdvar.util import dim_label as l

class ModelOutputData( InterfaceData ):
    
    label_x = [ x for x in l.label_x ]
    label_t = [ t for t in l.label_t ]
    
    def __init__( self, conc ):
        InterfaceData.__init__( self )
        if conc.shape != ( len( self.label_x ), len( self.label_t ) ):
            raise ValueError( 'ModelOutputData failed. input of wrong shape.' )
        
        self.conc = np.copy(conc)
        return None
    
    def get_value( self, coord ):
        return self.conc[ coord[ 0 ], coord[ 1 ] ]
    
    def set_value( self, coord, val ):
        self.conc[ coord[ 0 ], coord[ 1 ] ] = val
        return None
    
    def sum_square( self ):
        return np.sum( self.conc**2 )

    @classmethod
    def example( cls ):
        #return an instance with example data
        return cls( np.ones(( len(cls.label_x), len(cls.label_t) )) )
    
    @classmethod
    def clone( cls, source ):
        #produce another instance with same data as source
        return cls( source.conc.copy() )
    
    def cleanup( self ):
        #called when cloned instance is to be removed
        return None

