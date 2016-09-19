#observation_data.py
#this contains definitions for both single and extractable observations.

import numpy as np

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

from fourdvar.util import data_read
from fourdvar.util import dim_label as l


class ObservationSingle( SingleData ):
    """single observation"""
    def __init__( self, value, location ):
        SingleData.__init__( self, value=value, location=int( location ) )
        self.required.add( 'location' )
        return None


class ObservationData( ExtractableData ):
    """vector of observations, observed or simulated"""
    label_i = [ i for i in l.label_i ]
    
    def __init__( self, attr_list ):
        #attr_list is list of (location (i), value (val)) tuples
        obs_set = [ { 'location': d[0], 'value': d[1] } for d in attr_list ]
        dataset = [ ObservationSingle( **obs_dict ) for obs_dict in obs_set ]
        ExtractableData.__init__( self, dataset )
        if self.label_i != self.get_vector( 'location' ):
            raise ValueError( 'input data does not match observation space.' )
        return None
    
    @classmethod
    def weight( cls, res ):
        # weight residual relative to inverse observation error covariance
        #at present no error weighting is applied.
        val_list = res.get_vector( 'value' )
        loc_list = res.get_vector( 'location' )
        attr_list = [ (loc_list[i], val_list[i]) for i in range( len( val_list ) ) ]
        return cls( attr_list )
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        # return a new ObservationData containing the residual of observed and simulated
        o_val = observed.get_vector( 'value' )
        s_val = simulated.get_vector( 'value' )
        val_list = [ s_val[i] - o_val[i] for i in range( len( o_val ) ) ]
        loc_list = observed.get_vector( 'location' )
        attr_list = [ (loc_list[i], val_list[i]) for i in range( len( val_list ) ) ]
        return cls( attr_list )
    
    @classmethod
    def from_file( cls, filename ):
        #create an ObservationData from a file
        o_dict = data_read.get_dict( filename )
        attr_list = [ (o_dict['i'][n-1], o_dict['value'][n-1]) for n in cls.label_i ]
        return cls( attr_list )

