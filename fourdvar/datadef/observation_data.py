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

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.file_handle as fh

import setup_logging
logger = setup_logging.get_logger( __file__ )

class ObservationData( FourDVarData ):
    """application: vector of observations, observed or simulated"""
    # parameters
    archive_name = 'obs_set.pic.gz'
    length = None
    uncertainty = None
    weight_grid = None
    misc_meta = None

    def __init__( self, val_list ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        notes: Input is a list of observed values (floats).
               Metadata created by from_file() method.
        """
        assert len( val_list ) == self.length, 'invalid list of values'
        self.value = np.array( val_list )
        return None
    
    def get_vector( self ):
        """
        framework: return the values of ObservationData as a 1D numpy array
        input: None
        output: np.ndarray
        """
        return np.array(self.value)

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

        obs_list = []
        for i in range( self.length ):
            odict = { k:v for k,v in self.misc_meta[i].items() }
            odict[ 'value' ] = self.value[i]
            odict[ 'uncertainty' ] = self.uncertainty[i]
            odict[ 'weight_grid' ] = self.weight_grid[i]
            obs_list.append( odict )
        fh.save_list( obs_list, save_path )
        return None
    
    @classmethod
    def error_weight( cls, res ):
        """
        application: return residual of observations weighted by the inverse error covariance
        input: ObservationData  (residual)
        output: ObservationData
        
        eg: weighted_residual = datadef.ObservationData.weight( residual )
        """
        weighted = res.value/((res.uncertainty)**2)
        return cls( weighted )
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        """
        application: return the residual of 2 sets of observations
        input: ObservationData, ObservationData
        output: ObservationData
        
        eg: residual = datadef.ObservationData.get_residual( observed_obs, simulated_obs )
        """
        res = simulated.value - observed.value
        return cls( res )
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """
        obs_list = fh.load_list( filename )
        unc = [ odict.pop('uncertainty') for odict in obs_list ]
        val = [ odict.pop('value') for odict in obs_list ]
        weight = [ odict.pop('weight_grid') for odict in obs_list ]

        if cls.length is not None:
            logger.warn( 'Overwriting ObservationData.length' )
        cls.length = len( obs_list )
        if cls.uncertainty is not None:
            logger.warn( 'Overwriting ObservationData.uncertainty' )
        cls.uncertainty = np.array( unc )
        if cls.misc_meta is not None:
            logger.warn( 'Overwriting ObservationData.misc_meta' )
        cls.misc_meta = obs_list
        if cls.weight_grid is not None:
            logger.warn( 'Overwriting ObservationData.weight_grid' )
        cls.weight_grid = weight

        return cls( val )
