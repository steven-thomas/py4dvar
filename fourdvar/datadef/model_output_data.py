"""
application: stores/references the output of the forward model.
used to construct the simulated observations.
"""

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class ModelOutputData( FourDVarData ):
    """application
    """
    def __init__( self, data ):
        """
        application: create an instance of ModelOutputData
        input: user-defined
        output: None
        
        eg: new_output =  datadef.ModelOutputData( filelist )
        """
        self.value = data
        return None
    
    def archive( self, path=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None
        output: None
        """
        save_path = get_archive_path()
        if path is None:
            path = self.archive_name
        save_path = os.path.join( save_path, path )
        if os.path.isfile( save_path ):
            os.remove( save_path )
        with open(save_path, 'wb') as picklefile:
            pickle.dump(self.value, picklefile)
        return None
    
    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create a ModelOutputData from previous archived files
        input: string (path/to/file)
        output: ModelOutputData
        """
        pathname = os.path.realpath( dirname )
        with open( pathname, 'wb' ) as picklefile:
            data = pickle.load( picklefile )
        
        return cls( data )
        
    def cleanup( self ):
        """
        application: called when model output is no longer required
        input: None
        output: None
        
        eg: old_model_out.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        #function must exist, it doesn't <NEED> to do anything
        return None
