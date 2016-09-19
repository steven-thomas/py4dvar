# SensitivityData is the output of the adjoint model, it becomes a gradient in Unknown space

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData
from fourdvar.util import dim_label as l


class SensitivityData( InterfaceData ):
    """stores 2 objects, icon (array of shape[x]) and emis (array of shape[x,t])
    values stored in here are sensitivities!
    """
    label_x = [ x for x in l.label_x ]
    label_t = [ t for t in l.label_t ]
    
    def __init__( self, d_icon, d_emis ):
        #d_icon and d_emis are numpy arrays
        InterfaceData.__init__( self )
        
        if d_icon.size != len( self.label_x ):
            raise ValueError( 'SensitivityData failed. input d_icon was not valid.' )
        if d_emis.shape != ( len( self.label_x ), len( self.label_t ) ):
            raise ValueError( 'SensitivityData failed. input d_emis was not valid.' )
        
        self.icon = np.copy( d_icon )
        self.emis = np.copy( d_emis )
        
        return None

