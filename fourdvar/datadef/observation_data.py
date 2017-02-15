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
from fourdvar.util.date_handle import replace_date
import fourdvar.util.file_handle as fh
import fourdvar.util.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import setup_logging

logger = setup_logging.get_logger( __file__ )

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
        
        #this statement must be called.
        SingleData.__init__( self, **kwargs )
        return None

class ObservationData( ExtractableData ):
    """application: vector of observations, observed or simulated"""
    
    archive_name = 'obsset.pickle'
    
    def __init__( self, griddata, obs_list ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        
        notes: Currently input is a list of dicts, each dict contains the attributes of an observation.
        """
        #a 'valid'==False obs might not have a value, it needs one.
        for obs in obs_list:
            if obs['valid'] is False and 'value' not in obs.keys():
                obs[ 'value' ] == None
        dataset = [ ObservationSingle( **obs_dict ) for obs_dict in obs_list ]
        
        #this statement must be called.
        ExtractableData.__init__( self, dataset )
        #include data on the netCDF grid used for weighting index
        self.griddata = deepcopy( griddata )
        #date range last used for self.make_valid()
        self.valid_dates = None
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
        
    def archive( self, pathname=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None(path/to/save.pickle)
        output: None

        notes: this will overwrite any clash in namespace.
        if input is None file will use default name.
        output file is in acceptable format for from_file method.
        """
        save_path = get_archive_path()
        if pathname is None:
            pathname = self.archive_name
        save_path = os.path.join( save_path, pathname )
        
        obs_list = [ deepcopy( obs.__dict__ ) for obs in self.dataset ]
        fh.save_obj( self.griddata, save_path, overwrite=True )
        fh.save_obj( obs_list, save_path, overwrite=False )
        return None
    
    def check_grid( self, other_grid=template.conc ):
        """
        extension: check that griddata matches other
        input: string(path/to/conc.ncf) <OR> dict
        output: Boolean
        """
        attr_list = self.griddata.keys()
        return ncf.match_attr( self.griddata, other_grid, attr_list )
    
    def make_valid( self, datelist ):
        """
        extension: ensure that every valid obs in within domain.
                   make obs invalid otherwise.
        input: list  ( from global_config.get_datelist() )
        output: None (changes in place)
        """
        #check make_valid has not already been run for these dates
        if self.valid_dates == datelist:
            return None
        
        nlays = self.griddata['NLAYS']
        nrows = self.griddata['NROWS']
        ncols = self.griddata['NCOLS']
        spc_list = self.griddata['VAR-LIST'].split()
        t = int( self.griddata['TSTEP'] )
        tsec = 60*60*(t//10000) + 60*((t%10000)//100) + (t%100)
        nstep = (60*60*24 // tsec) + 1
        dates = [ int( replace_date('<YYYYMMDD>',d) ) for d in datelist ]
        
        max_ind_list = [nstep,nlays,nrows,ncols]
        valid_obs = [ o for o in self.dataset if o.valid is True ]
        for obs in valid_obs:
            keep = True
            for coord in obs.weight_grid.keys():
                day,step,lay,row,col,spc = coord
                ind_list = [step,lay,row,col]
                if (day == dates[0]) and (step == 0):
                    #special case: forcing offset will shift data off grid
                    keep = False
                if (day not in dates) or (spc not in spc_list):
                    keep = False
                for val,max_val in zip( ind_list, max_ind_list ):
                    if not (0 <= val < max_val):
                        keep = False
                if keep is False:
                    break
            if keep is False:
                obs.valid = False
        self.valid_dates = datelist
        return None
    
    def check_meta( self, other=None ):
        """
        extension: check that 2 ObservationData have compatible metadata
        input: ObservationData
        output: Boolean
        """
        if other is None:
            other = ObservationData.load_blank( template.obsmeta )
        #must have the same griddata
        if self.check_grid( other.griddata ) is False:
            return False
        
        for s_obs, o_obs in zip( self.dataset, other.dataset ):
            s_obs = deepcopy( s_obs.__dict__ )
            o_obs = deepcopy( o_obs.__dict__ )
            #handle special attributes: valid & value are allowed to be different.
            s_obs.pop( 'valid' )
            o_obs.pop( 'valid' )
            s_obs.pop( 'value' )
            o_obs.pop( 'value' )
            
            shared_attr = list( set( s_obs.keys() ) & set( o_obs.keys() ) )
            if ncf.match_attr( s_obs, o_obs, shared_attr ) is False:
                return False
        return True
    
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
        
        observed.check_meta( simulated )
        
        arglist = []
        for obs, sim in zip( observed.dataset, simulated.dataset ):
            obs = deepcopy( obs.__dict__ )
            sim = deepcopy( sim.__dict__ )
            #handle special attributes:
            valid = (obs.pop( 'valid' ) is True) and (sim.pop( 'valid' ) is True)
            oval, sval = obs.pop( 'value' ), sim.pop( 'value' )
            value = (sval - oval) if valid is True else None
            
            res_dict = { 'valid': valid, 'value': value }
            res_dict.update( obs )
            res_dict.update( sim )
            arglist.append( res_dict )
        griddata = deepcopy( observed.griddata )
        residual = cls( griddata, arglist )
        if observed.valid_dates is None:
            residual.valid_dates = simulated.valid_dates
        elif simulated.valid_dates is None:
            residual.valid_dates = observed.valid_dates
        elif observed.valid_dates == simulated.valid_dates:
            residual.valid_dates = observed.valid_dates
        return residual
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """
        griddata = fh.load_obj( filename, close=False )
        obs_list = fh.load_obj( filename, close=True )
        return cls( griddata, obs_list )
    
    @classmethod
    def load_blank( cls, filename ):
        """
        extension: create an ObservationData with None values
        input: iterable of dicts
        output: ObservationData
        """
        griddata = fh.load_obj( filename, close=False )
        obs_list = fh.load_obj( filename, close=True )
        for obs_dict in obs_list:
            obs_dict[ 'value' ] = None
        return cls( griddata, obs_list )
    
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
        
        obs_set = cls.load_blank( template.obsmeta )
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
