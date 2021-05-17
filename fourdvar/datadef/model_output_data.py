"""
model_output_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.netcdf_handle as ncf

class ModelOutputData( FourDVarData ):
    """application
    """
    archive_name = 'model_output.nc'

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

        (nrow,ncol,) = self.value.shape
        dim_dict = {'ROW':nrow,'COL':ncol}
        var_dict = { 'VALUE': ('f4', ('ROW','COL',), self.value[:]) }
        root = ncf.create( save_path, dim=dim_dict, var=var_dict, is_root=True )
        root.close()
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
        value = ncf.get_variable( pathname, 'VALUE' )
        return cls( value )
        
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
