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
    
    def get_value( self, i ):
        if i[0].strip().lower() == 'icon':
            return self.icon[i[1]]
        elif i[0].strip().lower() == 'emis':
            return self.emis[ i[1], i[2] ]
        else:
            raise ValueError( 'invalid lookup {} for SensitivityData'.format(i) )
    
    @classmethod
    def example( cls ):
        #return an instance with example data
        argicon = np.ones( len(cls.label_x) )
        argemis = np.ones(( len(cls.label_x), len(cls.label_t) ))
        return cls( argicon, argemis )

