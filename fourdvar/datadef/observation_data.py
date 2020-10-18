"""
observation_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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
    """application: vector of observations, observed or simulated
    Can be either 'full' or 'lite' file.
    'lite' file has no weight_grid attribute and cannot be used in transforms
        (for achiving and analysis only)"""
    
    #Parameters
    length = None
    uncertainty = None
    weight_grid = None
    alpha_scale = None
    ref_profile = None
    misc_meta = None
    grid_attr = None
    ind_by_date = None
    spcs = None
    lite_coord = None
    
    archive_name = 'obsset.pickle.zip'
    
    def __init__( self, val_list, is_lite=False ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        
        notes: Currently input is a list of floats.
               Metadata created by from_file()
        """
        #params must all be set and not None
        self.is_lite = is_lite
        self.assert_params( need_weight=False )
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
        
    def archive( self, name=None, force_lite=False ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None, boolean
        output: None

        notes: this will overwrite any clash in namespace.
        if input is None file will use default name.
        output file is in acceptable format for from_file method.
        force_lite will archive obs-lite file (no weight_grid).
        """
        save_path = get_archive_path()
        if name is None:
            name = self.archive_name
        save_path = os.path.join( save_path, name )
        
        domain = deepcopy( self.grid_attr )
        domain['SDATE'] = np.int32(dt.replace_date('<YYYYMMDD>',dt.start_date))
        domain['EDATE'] = np.int32(dt.replace_date('<YYYYMMDD>',dt.end_date))
        if force_lite is True:
            domain['is_lite'] = True
        else:
            domain['is_lite'] = self.is_lite
        
        obs_list = []
        for i in range( self.length ):
            odict = deepcopy( self.misc_meta[i] )
            odict[ 'value' ] = self.value[i]
            odict[ 'uncertainty' ] = self.uncertainty[i]
            odict[ 'alpha_scale' ] = self.alpha_scale[i]
            odict[ 'ref_profile' ] = self.ref_profile[i]
            odict[ 'lite_coord' ] = self.lite_coord[i]
            if domain['is_lite'] is False:
                odict[ 'weight_grid' ] = self.weight_grid[i]
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
        if 'is_lite' in domain.keys():
            is_lite = domain.pop('is_lite')
        else:
            is_lite = False
        if cls.grid_attr is not None:
            logger.warn( 'Overwriting ObservationData.grid_attr' )
        cls.grid_attr = domain
        cls.check_grid()
        msg = 'obs data does not match params date'
        assert sdate == np.int32( dt.replace_date('<YYYYMMDD>',dt.start_date) ), msg
        assert edate == np.int32( dt.replace_date('<YYYYMMDD>',dt.end_date) ), msg
        
        obs_list = datalist[1:]
        unc = [ odict.pop('uncertainty') for odict in obs_list ]
        val = [ odict.pop('value') for odict in obs_list ]
        alp = [ odict.pop('alpha_scale') for odict in obs_list ]
        ref = [ odict.pop('ref_profile') for odict in obs_list ]
        if is_lite is False:
            weight = [ odict.pop('weight_grid') for odict in obs_list ]
        #create default 'lite_coord' if not available
        coord = [ odict.pop('lite_coord',None) for odict in obs_list ]
        if None in coord:
            assert is_lite is False, 'Missing coordinate data.'
            logger.warn( "Missing lite_coord data. Setting to coord with largest weight in weight_grid" )
            for i,_ in enumerate( obs_list ):
                if coord[i] is None:
                    max_weight = max( [ (v,k,) for k,v in weight[i].items() ] )
                    coord[i] = max_weight[1]
        
        if cls.length is not None:
            logger.warn( 'Overwriting ObservationData.length' )
        cls.length = len( obs_list )
        if cls.uncertainty is not None:
            logger.warn( 'Overwriting ObservationData.uncertainty' )
        cls.uncertainty = unc
        if cls.alpha_scale is not None:
            logger.warn( 'Overwriting ObservationData.alpha_scale' )
        cls.alpha_scale = alp
        if cls.ref_profile is not None:
            logger.warn( 'Overwriting ObservationData.ref_profile' )
        cls.ref_profile = ref
        if cls.lite_coord is not None:
            logger.warn( 'Overwriting ObservationData.lite_coord' )
        cls.lite_coord = coord
        if cls.misc_meta is not None:
            logger.warn( 'Overwriting ObservationData.misc_meta' )
        cls.misc_meta = obs_list
        if is_lite is False:
            if cls.weight_grid is not None:
                logger.warn( 'Overwriting ObservationData.weight_grid' )
            cls.weight_grid = weight
        
        if is_lite is True:
            all_spcs = set( str( coord[-1] ) for coord in cls.lite_coord )
        else:
            all_spcs = set()
            for w in cls.weight_grid:
                spcs = set( str( coord[-1] ) for coord in w.keys() )
                all_spcs = all_spcs.union( spcs )
        if cls.spcs is not None:
            logger.warn( 'Overwriting ObservationData.spcs' )
        cls.spcs = sorted( list( all_spcs ) )
        
        if is_lite is False:
            dlist = [ dt.replace_date('<YYYYMMDD>',d) for d in dt.get_datelist() ]
            ind_by_date = { d: [] for d in dlist }
            for i, weight in enumerate( cls.weight_grid ):
                dates = set( str( coord[0] ) for coord in weight.keys() )
                for d in dates:
                    ind_by_date[ d ].append( i )
            if cls.ind_by_date is not None:
                logger.warn( 'Overwriting ObservationData.ind_by_date' )
            cls.ind_by_date = ind_by_date
        
        return cls( val, is_lite=is_lite )
    
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
    def assert_params( cls, need_weight=True ):
        """
        extension: assert that all needed observation parameters are valid
        input: boolean (True == must have weight_grid (eg: not a obs-lite file))
        output: None
        """
        assert cls.length is not None, 'length is not set'
        assert cls.uncertainty is not None, 'uncertainty is not set'
        assert cls.alpha_scale is not None, 'alpha_scale is not set'
        assert cls.ref_profile is not None, 'ref_profile is not set'
        assert cls.lite_coord is not None, 'lite_coord is not set'
        assert cls.misc_meta is not None, 'misc_meta is not set'
        assert cls.grid_attr is not None, 'grid_attr is not set'
        assert cls.spcs is not None, 'spcs is not set'
        assert len(cls.uncertainty) == cls.length, 'invalid uncertainty length'
        assert len(cls.lite_coord) == cls.length, 'invalid lite_coord length'
        assert len(cls.misc_meta) == cls.length, 'invalid misc_meta length'
        if need_weight is True:
            assert cls.weight_grid is not None, 'weight_grid is not set'
            assert cls.ind_by_date is not None, 'ind_by_date is not set'
            assert len(cls.weight_grid)==cls.length, 'invalid weight_grid length'
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
        return cls( src.value, is_lite=src.is_lite )
