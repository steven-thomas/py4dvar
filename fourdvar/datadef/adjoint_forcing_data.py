# the adjoint forcing serves as input for the adjoint model run, made from the weighted residual of observations

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData
from fourdvar.util import dim_label as l

class AdjointForcingData( InterfaceData ):
    
    label_x = [ x for x in l.label_x ]
    label_t = [ t for t in l.label_t ]
    
    def __init__( self, frc ):
        #frc is a 2D numpy array, forcing for space (x) and time (t)
        InterfaceData.__init__( self )
        if frc.shape != ( len( self.label_x ), len( self.label_t ) ):
            raise ValueError( 'AdjointForcingData failed. input of wrong shape.' )
        
        self.frc = np.copy(frc)
        return None
    
    def get_value( self, coord ):
        return self.frc[ coord[ 0 ], coord[ 1 ] ]

    @classmethod
    def example( cls ):
        #return an instance with example data
        return cls( np.ones(( len(cls.label_x), len(cls.label_t) )) )

