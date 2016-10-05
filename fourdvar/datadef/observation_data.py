#observation_data.py
#this contains definitions for both single and extractable observations.

import numpy as np

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

from fourdvar.util.file_handle import get_dict

class ObservationSingle( SingleData ):
    """single observation"""
    require = SingleData.add_require( 'time', 'kind' )
    def __init__( self, **kwargs ):
        # time is in No. of steps (int)
        kwargs[ 'value' ] = np.float64( kwargs[ 'value'] )
        kwargs[ 'time' ] = int( kwargs[ 'time' ] )
        kwargs[ 'kind' ] = int( kwargs[ 'kind' ] )
        SingleData.__init__( self, **kwargs )
        return None


class ObservationData( ExtractableData ):
    """vector of observations, observed or simulated"""
    
    def __init__( self, obs_list ):
        #list of dicts, keys are 'value', 'time', & 'kind'
        keyset = ObservationSingle.require
        msg = 'input data does not match observation space.'
        assert all( [ keyset.issubset( o.keys() ) for o in obs_list ] ), msg
        dataset = [ ObservationSingle( **obs_dict ) for obs_dict in obs_list ]
        ExtractableData.__init__( self, dataset )
        return None
    
    def sum_square( self ):
        vector = np.array( self.get_vector( 'value' ) )
        return np.sum( vector**2 )
    
    @classmethod
    def weight( cls, res ):
        # weight residual relative to inverse observation error covariance
        #at present no error weighting is applied.
        keyset = list( ObservationSingle.require )
        obslen = len( res.dataset )
        attrlist = [ res.get_vector( key ) for key in keyset ]
        arglist = []
        for j in range( obslen ):
            arglist.append( { name: attrlist[i][j] for i,name in enumerate( keyset ) } )
        return cls( arglist )
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        # return a new ObservationData containing the residual of observed and simulated
        obsval = observed.get_vector( 'value' )
        simval = simulated.get_vector( 'value' )
        keyset = [ k for k in ObservationSingle.require if k != 'value' ]
        attrlist = [ observed.get_vector( key ) for key in keyset ]
        
        errmsg = 'Observed and Simulated observations are incompatible'
        assert attrlist == [ simulated.get_vector( key ) for key in keyset ], errmsg
        
        arglist = []
        for j in range( len( obsval ) ):
            d = { name: attrlist[i][j] for i,name in enumerate( keyset ) }
            d[ 'value' ] = simval[ j ] - obsval[ j ]
            arglist.append( d )

        return cls( arglist )
    
    @classmethod
    def from_file( cls, filename ):
        #create an ObservationData from a file
        o_dict = get_dict( filename )
        lengths = [ len( v ) for v in o_dict.values() ]
        assert ObservationSingle.require.issubset( set( o_dict.keys() ) ), 'invalid file headings'
        assert all( [ i == lengths[0] for i in lengths[1:] ] ), 'invalid file content'
        arglist = []
        for j in range( lengths[0] ):
            arglist.append( { k:o_dict[k][j] for k in o_dict.keys() } )
        return cls( arglist )

    @classmethod
    def example( cls ):
        #return an instance with example data
        arglist = []
        for i in range( 10 ):
            arglist.append( { 'value':1, 'time':i, 'kind':0 } )
        return cls( arglist )

