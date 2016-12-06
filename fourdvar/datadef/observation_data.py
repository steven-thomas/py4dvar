"""
application: structure for the data from observations, both observed and simulated
"""

import os
import numpy as np
from copy import deepcopy

import _get_root
from fourdvar.datadef.abstract._single_data import SingleData
from fourdvar.datadef.abstract._extractable_data import ExtractableData

from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.file_handle as fh
import fourdvar.util.template_defn as template

class ObservationSingle( SingleData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an ObservationSingle to be valid.
    #require = SingleData.add_require( 'time', 'kind' )
    
    def __init__( self, **kwargs ):
        """
        application: create a record for a single observation
        input: user-defined (must include 'value')
        output: None
        
        notes: any provided keyword argument is stored as an attribute
        """
        # time is in No. of steps (int)
        #kwargs[ 'value' ] = np.float64( kwargs[ 'value'] )
        #kwargs[ 'time' ] = int( kwargs[ 'time' ] )
        #kwargs[ 'kind' ] = int( kwargs[ 'kind' ] )
        
        #this statement must be called.
        SingleData.__init__( self, **kwargs )
        return None

class ObservationData( ExtractableData ):
    """application: vector of observations, observed or simulated"""
    
    archive_name = 'sim_obs.pickle'
    
    def __init__( self, obs_list ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        
        notes: Currently input is a list of dicts, each dict contains the attributes of an observation.
        """
        dataset = [ ObservationSingle( **obs_dict ) for obs_dict in obs_list ]
        
        #this statement must be called.
        ExtractableData.__init__( self, dataset )
        return None
    
    def get_vector( self, attr='value', inc_invalid=False ):
        """
        extension: add option to get_vector to control use of obd 'valid' flag
        input: string, bool
        output: list
        
        notes: this overloads ExtractableData.get_vector()
        """
        output = ExtractableData.get_vector( self, attr )
        if inc_invalid is False:
            valid = ExtractableData.get_vector( self, 'valid' )
            output = [ val for val,flag in zip( output, valid ) if flag is True ]
        return output
    
    def perturb( self ):
        """
        application: change every value randomly based on observation error covariance
        input: None
        output: None
        
        eg: test_obs.perturb()
        
        notes: only used for accuracy testing
        """
        #for obs in self.dataset:
        #    obs.value += np.random.normal(0,1)
        return None
    
    def archive( self, dirname=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None
        output: None

        notes: this will overwrite any clash in namespace.
        if input is None file will write to experiment directory
        else it will create dirname in experiment directory and save there.
        """
        save_path = get_archive_path()
        if dirname is not None:
            save_path = os.path.join( save_path, dirname )
        fh.save_obj( self, os.path.join( save_path, self.archive_name ) )
        return None

    
    @classmethod
    def error_weight( cls, res ):
        """
        application: return residual of observations weighted by the inverse error covariance
        input: ObservationData  (residual)
        output: ObservationData
        
        eg: weighted_residual = datadef.ObservationData.weight( residual )
        """
        weighted = cls.clone( res )
        for obs in weighted.dataset:
            if obs.valid is True:
                obs.value = obs.value / (obs.uncertainty ** 2)
        return weighted
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        """
        application: return the residual of 2 sets of observations
        input: ObservationData, ObservationData
        output: ObservationData
        
        eg: residual = datadef.ObservationData.get_residual( observed_obs, simulated_obs )
        """        
        arglist = []
        for obs, sim in zip( observed.dataset, simulated.dataset ):
            obs = deepcopy( obs.__dict__ )
            sim = deepcopy( sim.__dict__ )
            #handle special attributes:
            valid = (obs.pop( 'valid' ) is True) and (sim.pop( 'valid' ) is True)
            oval, sval = obs.pop( 'value' ), sim.pop( 'value' )
            value = (sval - oval) if valid is True else None
            
            res_dict = { 'valid': valid, 'value': value }
            
            #all_attr = set( obs.keys() ) | set( sim.keys() )
            shared_attr = set( obs.keys() ) & set( sim.keys() )
            for attr in shared_attr:
                msg = 'cannot find residual. Observations incompatible.'
                assert obs[ attr ] == sim[ attr ], msg
                res_dict[ attr ] = obs[ attr ]
            for attr in ( set( obs.keys() ) - shared_attr ):
                res_dict[ attr ] = obs[ attr ]
            for attr in ( set( sim.keys() ) - shared_attr ):
                res_dict[ attr ] = sim[ attr ]
            arglist.append( res_dict )
        return cls( arglist )
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """
        #o_dict = get_dict( filename )
        #lengths = [ len( v ) for v in o_dict.values() ]
        #assert ObservationSingle.require.issubset( set( o_dict.keys() ) ), 'invalid file headings'
        #assert all( [ i == lengths[0] for i in lengths[1:] ] ), 'invalid file content'
        #arglist = []
        #for j in range( lengths[0] ):
        #    arglist.append( { k:o_dict[k][j] for k in o_dict.keys() } )
        #return cls( arglist )
        return None
    
    @classmethod
    def load_blank( cls, obs_list ):
        """
        extension: create an ObservationData with None values
        input: iterable of dicts
        output: ObservationData
        """
        for obs_dict in obs_list:
            obs_dict[ 'value' ] = None
        return cls( obs_list )

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: ObservationData
        
        eg: mock_obs = datadef.ObservationData.example()
        
        notes: only used for testing.
        """
        example_value = 1
        
        obsmeta_path = template.obsmeta
        __ = fh.load_obj( obsmeta_path, close=False )
        obs_list = fh.load_obj( obsmeta_path, close=True )
        obs_set = cls.load_blank( obs_list )
        for obs in obs_set.dataset:
            if obs.valid is True:
                obs.value = example_value
        return obs_set
    
    @classmethod
    def clone( cls, src ):
        """
        application: copy an ObservationData.
        input: ObservationData
        output: ObservationData
        
        eg: obs_copy = datadef.ObservationData.clone( current_obs )
        
        notes: ensure that copy is independant (eg: uses copies of files, etc.)
        """
        msg = 'cannot clone {0}'.format( src.__class__.__name__ )
        assert isinstance( src, cls ), msg
        #obs does not contain any reference to filepaths
        #therefore deepcopy is sufficient
        return deepcopy( src )
