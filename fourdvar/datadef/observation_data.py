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

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

from fourdvar.util.archive_handle import get_archive_path

import setup_logging
logger = setup_logging.get_logger( __file__ )

class ObservationData( FourDVarData ):
    """application: vector of observations, observed or simulated"""
    
    archive_name = 'obsset.pickle.zip'
    
    def __init__( self, val_list ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        """
        return None
    
    def get_vector( self ):
        """
        framework: return the values of ObservationData as a 1D numpy array
        input: None
        output: np.ndarray
        """
        return np.array()
        
    def archive( self, name=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None
        output: None
        """
        save_path = get_archive_path()
        if name is None:
            name = self.archive_name
        save_path = os.path.join( save_path, name )
        #save data to save_path
        return None
        
    @classmethod
    def error_weight( cls, res ):
        """
        application: return residual of observations weighted by the inverse error covariance
        input: ObservationData  (residual)
        output: ObservationData
        
        eg: weighted_residual = datadef.ObservationData.weight( residual )
        """
        return cls()
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        """
        application: return the residual of 2 sets of observations
        input: ObservationData, ObservationData
        output: ObservationData
        
        eg: residual = datadef.ObservationData.get_residual( observed_obs, simulated_obs )
        """
        #eg:
        #res = [ s - o for o,s in zip( observed.value, simulated.value ) ]
        return cls()
    
    @classmethod
    def from_file( cls, ... ):
        """
        extension: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """        
        return cls()
