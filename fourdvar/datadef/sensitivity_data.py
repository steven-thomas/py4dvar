"""
sensitivity_data.py

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

class SensitivityData( FourDVarData ):
    """application
    """
    archive_name = 'model_sensitivity.nc'
    input_name = None
    
    def __init__( self, value, input_name=None ):
        """
        application: create an instance of SensitivityData
        input: user-defined
        output: None
        
        eg: new_sense =  datadef.SensitivityData( filelist )
        """
        self.value = value
        if self.input_name is None:
            self.input_name = input_name
        return None
    
    def archive( self, path=None ):
        """
        extension: save copy of files to archive/experiment directory
        input: string or None
        output: None
        """
        save_path = get_archive_path()
        if path is None:
            path = self.archive_name
        save_path = os.path.join( save_path, path )
        if os.path.isfile( save_path ):
            os.remove( save_path )

        (ninput,nrow,ncol,) = self.value.shape
        attr_dict = { 'INPUT_NAME': self.input_name }
        dim_dict = { 'INPUT':ninput, 'ROW':nrow, 'COL':ncol }
        var_dict = { 'SENSITIVITY': ('f4',('INPUT','ROW','COL',),self.value,) }

        root = ncf.create( path=save_path, attr=attr_dict, dim=dim_dict,
                           var=var_dict, is_root=True )
        root.close()
        return None

    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create a SensitivityData from previous archived files.
        input: string (path/to/file)
        output: SensitivityData
        """
        pathname = os.path.realpath( dirname )
        value = ncf.get_variable( pathname, 'SENSITIVITY' )
        input_name = ncf.get_attr( pathname, 'INPUT_NAME' )
        return cls.create_new( value, input_name )
    
    def cleanup( self ):
        """
        application: called when sensitivity is no longer required
        input: None
        output: None
        
        eg: sensitivity.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        #function needed but can be left blank
        return None
