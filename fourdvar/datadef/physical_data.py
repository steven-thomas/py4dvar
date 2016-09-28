# physical data is read in from file or produced from UnknownData.
# it turns into UnknownData and ModelInputData
# it describes the background and minimized estimate as described from files.
# unlike UnknownData it doesn't need to be vectorable

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util import data_read
from fourdvar.util import dim_label as l


class PhysicalData( InterfaceData ):
    """Starting point of background, link between model and unknowns
    data structure is a dictionary, keys are space co-ord (x)
    values are pairs (icon, emis), emission is constant over all time
    data structure: dict[ x 'space' ] = [ icon 'conc', emis 'conc/s' ]
    """
    label_x = [ x for x in l.label_x ]
    
    def __init__( self, data ):
        #data is a dict of (icon, emis) tuples for each point in space (x)
        if self.label_x != sorted( data.keys() ):
            raise ValueError( 'input data does not match model space' )
        self.data = data.copy()
        return None
    
    @classmethod
    def from_file( cls, filename ):
        #create PhysicalData from a file
        p_dict = data_read.get_dict( filename )
        arg_dict = {}
        for i in range( len( p_dict['x'] ) ):
            arg_dict[ int( p_dict['x'][i] ) ] = [ p_dict['icon'][i], p_dict['emis'][i] ]
        return cls( arg_dict )

    @classmethod
    def example( cls ):
        #return an instance with example data
        argdict = {}
        for x in cls.label_x:
            argdict[ x ] = (1,1)
        return cls( argdict )

