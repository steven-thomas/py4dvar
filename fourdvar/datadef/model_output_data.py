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

