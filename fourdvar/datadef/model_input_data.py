"""
application: Stores the input for the forward model.
Built from the PhysicalData class.
Used to handle any resolution/format changes between the model and backgroud/prior
"""
# input class for the fwd model, generated from PhysicalData

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class ModelInputData( FourDVarData ):
    """application
    """
    
    def __init__( self ):
        """
        application: create an instance of ModelInputData
        input: user-defined
        output: None
        """
        #Mostly handled by the 'create_new' classmethod
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
        
    @classmethod
    def create_new( cls, data, **kwargs ):
        """
        application: create an instance of ModelInputData from template with modified values.
        input: user_defined
        output: ModelInputData
        """
        cls.value = data
        return cls()
    
    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create a ModelInputData from previous archived files
        input: string (path/to/file)
        output: ModelInputData
        """
        pathname = os.path.realpath( dirname )
        with open( pathname, 'wb' ) as picklefile:
            data = pickle.load( picklefile )
        
        return cls.create_new( data )
    
    def cleanup( self ):
        """
        application: called when model input is no longer required
        input: None
        output: None
        
        eg: old_model_in.cleanup()
        
        notes: called after test instance is no longer needed,
               used to delete files etc.
        """
        #function must exist, it doesn't <NEED> to do anything.
        return None
