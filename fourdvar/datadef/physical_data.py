# physical data is read in from file or produced from UnknownData.
# it turns into UnknownData and ModelInputData
# it describes the background and minimized estimate as described from files.
# unlike UnknownData it doesn't need to be vectorable

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.file_handle import get_dict
from fourdvar.util.dim_defn import x_len


class PhysicalData( InterfaceData ):
    """Starting point of background, link between model and unknowns
    """
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        #data is an array of x_len x-values
        InterfaceData.__init__( self )
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    @classmethod
    def from_file( cls, filename ):
        #create PhysicalData from a file
        read_dict = get_dict( filename )
        return cls( read_dict['x'] )

    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = 1.0 + np.zeros( x_len )
        return cls( arglist )

