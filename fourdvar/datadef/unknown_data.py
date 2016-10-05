# UnknownData stores the vector that the minimizer works with
# it is the pre-conditioned form PhysicalData and exists only really as a vector

import numpy as np

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

from fourdvar.util.dim_defn import x_len

class UnknownSingle( SingleData ):
    """single point in the unknown vector space"""
    def __init__( self, val ):
        SingleData.__init__( self, value=val )
        return None


class UnknownData( ExtractableData ):
    """vector of unknowns"""
    def __init__( self, vals ):
        val_arr = np.array( vals, dtype='float64' )
        assert val_arr.shape == ( x_len, ), 'input data does not match model space'
        dataset = [ UnknownSingle( val ) for val in val_arr ]
        ExtractableData.__init__( self, dataset )
        return None
    
    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = [ 1 for x in range( x_len ) ]
        return cls( arglist )

