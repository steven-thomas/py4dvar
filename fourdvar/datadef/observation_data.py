"""
application: structure for the data from observations, both observed and simulated
"""

import os
import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
import cPickle as pickle
from fourdvar.util.archive_handle import get_archive_path

import setup_logging
logger = setup_logging.get_logger( __file__ )

class ObservationData( FourDVarData ):
    """application: vector of observations, observed or simulated"""
    
    archive_name = 'obsset.pickle.zip'
    unc = None # place holder class variable
    def __init__( self, data ):
        """
        application: create an instance of ObservationData
        input: user-defined.
        output: None
        
        eg: new_obs =  datadef.ObservationData( [{...}, {...}, ...] )
        """
        self.value = np.array( data )
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
        """
        save_path = get_archive_path()
        if name is None:
            name = self.archive_name
        save_path = os.path.join( save_path, name )
        with open(save_path, 'wb') as picklefile:
            pickle.dump(self.value, picklefile)
            pickle.dump(self.unc, picklefile)
        return None
        
    @classmethod
    def error_weight( cls, res ):
        """
        application: return residual of observations weighted by the inverse error covariance
        input: ObservationData  (residual)
        output: ObservationData
        
        eg: weighted_residual = datadef.ObservationData.weight( residual )
        """
        return cls(res.value/ObservationData.unc)
    
    @classmethod
    def get_residual( cls, observed, simulated ):
        """
        application: return the residual of 2 sets of observations
        input: ObservationData, ObservationData
        output: ObservationData
        
        eg: residual = datadef.ObservationData.get_residual( observed_obs, simulated_obs )
        """
        #eg:
        res = [ s - o for o,s in zip( observed.value, simulated.value ) ]
        return cls( res)
                                                                                                                                                           
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create an ObservationData from a file
        input: user-defined
        output: ObservationData
        
        eg: observed = datadef.ObservationData.from_file( "saved_obs.data" )
        """
        with open(filename, 'rb') as picklefile:
            val = pickle.dump( picklefile )
            unc = pickle.dump( picklefile )
        cls.unc = unc
        return cls(val)
