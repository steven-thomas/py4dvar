"""
model_input_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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
        
    def archive( self, dirname=None ):
        """
        extension: save copy of files to archive/experiment directory
        input: string or None
        output: None
        """
        save_path = get_archive_path()
        if dirname is not None:
            save_path = os.path.join( save_path, dirname )
        ensure_path( save_path, inc_file=False )
        #save data to save_path, somehow
        return None
    
    @classmethod
    def create_new( cls, **kwargs ):
        """
        application: create an instance of ModelInputData from template with modified values.
        input: user_defined
        output: ModelInputData
        """
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
        assert os.path.isdir( pathname ), 'dirname must be an existing directory'
        #Load data from archive format into use
        return cls()
    
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
