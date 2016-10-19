"""
application: structure for the data from observations, both observed and simulated
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

from fourdvar.util.file_handle import get_dict
from fourdvar.util.dim_defn import nstep, obs_kinds

class ObservationSingle( SingleData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an ObservationSingle to be valid.
    require = SingleData.add_require( 'time', 'kind' )
    
    def __init__( self, **kwargs ):
        """
        application: create a record for a single observation
        input: user-defined (must include 'value')
        output: None
        
        notes: any provided keyword argument is stored as an attribute
        """
        # time is in No. of steps (int)
        kwargs[ 'value' ] = np.float64( kwargs[ 'value'] )
        kwargs[ 'time' ] = int( kwargs[ 'time' ] )
        kwargs[ 'kind' ] = int( kwargs[ 'kind' ] )
        
        #this statement must be called.
        SingleData.__init__( self, **kwargs )
        return None

obs_param = []
for i in range( 1, nstep-1 ):
    obs_param.append( {'time':i, 'kind':( i % obs_kinds )} )
    obs_param.append( {'time':i, 'kind':( (i + 2) % obs_kinds )} )

class ObservationData( ExtractableData ):
    """application: vector of observations, observed or simulated"""
    
    #metadata used when constructing a new set of observations
    param = obs_param
    
    def __init__( self, obs_list ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        
        notes: Currently input is a list of dicts, each dict contains the attributes of an observation.
        """
        #list of dicts, keys are 'value', 'time', & 'kind'
        keyset = ObservationSingle.require
        msg = 'input data does not match observation space.'
        assert all( [ keyset.issubset( o.keys() ) for o in obs_list ] ), msg
        dataset = [ ObservationSingle( **obs_dict ) for obs_dict in obs_list ]
        
        #this statement must be called.
        ExtractableData.__init__( self, dataset )
        return None
    
    def sum_square( self ):
        """
        application: return sum of squares
        input: None
        output: scalar
        
        eg: total = obs.sum_square()
        
        notes: only used for accuracy testing.
        """
        vector = np.array( self.get_vector( 'value' ) )
        return np.sum( vector**2 )
    
    def perturb( self ):
        """
        application: change every value randomly base on observation error covariance
        input: None
        output: None
        
        eg: test_obs.perturb()
        
        notes: only used for accuracy testing
        """
        for obs in self.dataset:
            obs.value += np.random.normal(0,1)
        return None
    
    @classmethod
    def weight( cls, res ):
        """
        application: return residual of observations weighted by the inverse error covariance
        input: ObservationData  (residual)
        output: ObservationData
        
        eg: weighted_residual = datadef.ObservationData.weight( residual )
        """
        keyset = list( ObservationSingle.require )
        obslen = len( res.dataset )
        attrlist = [ res.get_vector( key ) for key in keyset ]
        arglist = []
        for j in range( obslen ):
            arglist.append( { name: attrlist[i][j] for i,name in enumerate( keyset ) } )
        return cls( arglist )
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        """
        application: return the residual of 2 sets of observations
        input: ObservationData, ObservationData
        output: ObservationData
        
        eg: residual = datadef.ObservationData.get_residual( observed_obs, simulated_obs )
        """
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
        """
        application: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """
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
        """
        application: return a valid example with arbitrary values.
        input: None
        output: ObservationData
        
        eg: mock_obs = datadef.ObservationData.example()
        
        notes: only used for testing.
        """
        arglist = []
        for i in range( 10 ):
            arglist.append( { 'value':1, 'time':i, 'kind':0 } )
        return cls( arglist )
    
    @classmethod
    def clone( cls, source ):
        """
        application: copy an ObservationData.
        input: ObservationData
        output: ObservationData
        
        eg: obs_copy = datadef.ObservationData.clone( current_obs )
        
        notes: only used for testing. ensure that copy is independant (eg: uses copies of files, etc.)
        """
        assert isinstance( source, cls )
        arglist = []
        for obs in source.dataset:
            arglist.append( obs.__dict__.copy() )
        return cls( arglist )

