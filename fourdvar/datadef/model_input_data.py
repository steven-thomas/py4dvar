# input class for the fwd model, generated from PhysicalData

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData
from fourdvar.util import dim_label as l

class ModelInputData( InterfaceData ):
    """stores 2 objects, icon (array of shape[x]) and emis (array of shape[x,t])"""
    label_x = [ x for x in l.label_x ]
    label_t = [ t for t in l.label_t ]
    
    def __init__( self, data ):
        #data is a dict => (icon, emis) tuple for every point in space (x)
        InterfaceData.__init__( self )
        
        if sorted( data.keys() ) != self.label_x:
            raise ValueError( 'ModelInputData failed. label_x did not match' )
        if np.any( [ len( data[ x ] ) != 2 for x in self.label_x ] ):
            raise ValueError( 'ModelInputData failed. data was not {x:(icon, emis)}' )
        
        self.icon = np.array( [ data[ x ][ 0 ] for x in self.label_x ] )
        
        self.emis = np.zeros( ( len( self.label_x ), len( self.label_t ) ) )
        e_in = np.array( [ data[ x ][ 1 ] for x in self.label_x ] )
        self.emis += e_in.reshape(( len(self.label_x), 1 ))
        
        return None

    @classmethod
    def example( cls ):
        #return an instance with example data
        argdict = {}
        for x in cls.label_x:
            argdict[x] = (1,1)
        return cls( argdict )

