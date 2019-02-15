"""
application: structure for the data from observations, both observed and simulated
"""

import os
import numpy as np
from copy import deepcopy

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.file_handle as fh
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf

import setup_logging
logger = setup_logging.get_logger( __file__ )

class ObservationData( FourDVarData ):
    """application: vector of observations, observed or simulated"""
    
    #Parameters
    length = None
    uncertainty = None
    weight_grid = None
    offset_term = None
    misc_meta = None
    grid_attr = None
    ind_by_date = None
    spcs = None
    
    archive_name = 'obsset.pickle.zip'
    
    def __init__( self, val_list ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        
        notes: Currently input is a list of floats.
               Metadata created by from_file()
        """
        #params must all be set and not None
        self.assert_params()
        assert len( val_list ) == self.length, 'invalid list of values'
        self.value = [ float( v ) for v in val_list ]
        return None
    
    def get_vector( self ):
        """
        framework: return the values of ObservationData as a 1D numpy array
        input: None
        output: np.ndarray
        """
        return np.array( self.value )
        
    def archive( self, name=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None
        output: None

        notes: this will overwrite any clash in namespace.
        if input is None file will use default name.
        output file is in acceptable format for from_file method.
        """
        save_path = get_archive_path()
        if name is None:
            name = self.archive_name
        save_path = os.path.join( save_path, name )
        
        domain = deepcopy( self.grid_attr )
        domain['SDATE'] = np.int32(dt.replace_date('<YYYYMMDD>',dt.start_date))
        domain['EDATE'] = np.int32(dt.replace_date('<YYYYMMDD>',dt.end_date))
        
        obs_list = []
        iter_obj = zip( self.value, self.uncertainty,
                        self.weight_grid, self.offset_term,
                        self.misc_meta )
        for val,unc,weight,off,misc in iter_obj:
            odict = deepcopy( misc )
            odict[ 'value' ] = val
            odict[ 'uncertainty' ] = unc
            odict[ 'weight_grid' ] = weight
            odict[ 'offset_term' ] = off
            obs_list.append( odict )
        
        archive_list = [ domain ] + obs_list
        fh.save_list( archive_list, save_path )
        return None
    
    @classmethod
    def check_grid( cls, other_grid=template.conc ):
        """
        extension: check that griddata matches other
        input: string(path/to/conc.ncf) <OR> dict
        output: Boolean
        """
        attr_list = cls.grid_attr.keys()
        return ncf.match_attr( cls.grid_attr, other_grid, attr_list )
    
    @classmethod
    def error_weight( cls, res ):
        """
        application: return residual of observations weighted by the inverse error covariance
        input: ObservationData  (residual)
        output: ObservationData
        
        eg: weighted_residual = datadef.ObservationData.weight( residual )
        """
        weighted = [ v/(u**2) for v,u in zip( res.value, res.uncertainty ) ]
        return cls( weighted )
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        """
        application: return the residual of 2 sets of observations
        input: ObservationData, ObservationData
        output: ObservationData
        
        eg: residual = datadef.ObservationData.get_residual( observed_obs, simulated_obs )
        """
        res = [ s - o for o,s in zip( observed.value, simulated.value ) ]
        return cls( res )
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """
        datalist = fh.load_list( filename )
        
        domain = datalist[0]
        sdate = domain.pop('SDATE')
        edate = domain.pop('EDATE')
        if cls.grid_attr is not None:
            logger.warn( 'Overwriting ObservationData.grid_attr' )
        cls.grid_attr = domain
        cls.check_grid()
        msg = 'obs data does not match params date'
        assert sdate == np.int32( dt.replace_date('<YYYYMMDD>',dt.start_date) ), msg
        assert edate == np.int32( dt.replace_date('<YYYYMMDD>',dt.end_date) ), msg
        
        obs_list = datalist[1:]
        unc = [ odict.pop('uncertainty') for odict in obs_list ]
        weight = [ odict.pop('weight_grid') for odict in obs_list ]
        val = [ odict.pop('value') for odict in obs_list ]
        off = [ odict.pop('offset_term') for odict in obs_list ]
        
        if cls.length is not None:
            logger.warn( 'Overwriting ObservationData.length' )
        cls.length = len( obs_list )
        if cls.uncertainty is not None:
            logger.warn( 'Overwriting ObservationData.uncertainty' )
        cls.uncertainty = unc
        if cls.weight_grid is not None:
            logger.warn( 'Overwriting ObservationData.weight_grid' )
        cls.weight_grid = weight
        if cls.offset_term is not None:
            logger.warn( 'Overwriting ObservationData.offset_term' )
        cls.offset_term = off
        if cls.misc_meta is not None:
            logger.warn( 'Overwriting ObservationData.misc_meta' )
        cls.misc_meta = obs_list
        
        all_spcs = set()
        for w in cls.weight_grid:
            spcs = set( str( coord[-1] ) for coord in w.keys() )
            all_spcs = all_spcs.union( spcs )
        if cls.spcs is not None:
            logger.warn( 'Overwriting ObservationData.spcs' )
        cls.spcs = sorted( list( all_spcs ) )
        
        dlist = [ dt.replace_date( '<YYYYMMDD>', d ) for d in dt.get_datelist() ]
        ind_by_date = { d: [] for d in dlist }
        for i, weight in enumerate( cls.weight_grid ):
            dates = set( str( coord[0] ) for coord in weight.keys() )
            for d in dates:
                ind_by_date[ d ].append( i )
        if cls.ind_by_date is not None:
            logger.warn( 'Overwriting ObservationData.ind_by_date' )
        cls.ind_by_date = ind_by_date
        
        return cls( val )
    
    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: ObservationData
        
        notes: only used for testing.
        """
        example_value = 1
        obsval = np.zeros( cls.length ) + example_value
        return cls( obsval )
    
    @classmethod
    def assert_params( cls ):
        """
        extension: assert that all needed observation parameters are valid
        input: None
        output: None
        """
        assert cls.length is not None, 'length is not set'
        assert cls.uncertainty is not None, 'uncertainty is not set'
        assert cls.weight_grid is not None, 'weight_grid is not set'
        assert cls.offset_term is not None, 'offset_term is not set'
        assert cls.misc_meta is not None, 'misc_meta is not set'
        assert cls.grid_attr is not None, 'grid_attr is not set'
        assert cls.ind_by_date is not None, 'ind_by_date is not set'
        assert cls.spcs is not None, 'spcs is not set'
        assert len(cls.uncertainty) == cls.length, 'invalid uncertainty length'
        assert len(cls.weight_grid) == cls.length, 'invalid weight_grid length'
        assert len(cls.misc_meta) == cls.length, 'invalid misc_meta length'
        return None
    
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
        return cls( src.value )
