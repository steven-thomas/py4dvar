# UnknownData stores the vector that the minimizer works with
# it is the pre-conditioned form PhysicalData and exists only really as a vector

import numpy as np

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

class UnknownSingle( SingleData ):
    """single point in the unknown vector space"""
    def __init__( self, val ):
        SingleData.__init__( self, value=val )
        return None


class UnknownData( ExtractableData ):
    """vector of unknowns"""
    def __init__( self, val_array ):
        val_list = list( val_array )
        dataset = [ UnknownSingle( val ) for val in val_list ]
        ExtractableData.__init__( self, dataset )
        return None

