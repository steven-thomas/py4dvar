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

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.netcdf_handle as ncf

class ModelInputData( FourDVarData ):
    """application
    """
    archive_name = 'model_input.nc'
    input_name = None
    
    def __init__( self, value ):
        """
        application: create an instance of ModelInputData
        input: user-defined
        output: None
        """
        self.value = value
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

        (ninput,nrow,ncol,) = self.value.shape
        attr_dict = { 'INPUT_NAME': self.input_name }
        dim_dict = { 'INPUT':ninput, 'ROW':nrow, 'COL':ncol }
        var_dict = { 'INPUT': ('f4',('INPUT','ROW','COL',),self.value,) }

        root = ncf.create( path=save_path, attr=attr_dict, dim=dim_dict,
                           var=var_dict, is_root=True )
        root.close()
        return None
        
    @classmethod
    def create_new( cls, value, input_name=None ):
        """
        application: create an instance of ModelInputData from template with modified values.
        input: user_defined
        output: ModelInputData
        """
        if cls.input_name is None:
            assert input_name is not None, 'model_input.input_name must be defined.'
            cls.input_name = input_name
        elif input_name is not None:
            assert cls.input_name == input_name, "Can't replace model input_name."
        return cls( value )
    
    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create a ModelInputData from previous archived files
        input: string (path/to/file)
        output: ModelInputData
        """
        pathname = os.path.realpath( dirname )
        value = ncf.get_variable( pathname, 'INPUT' )
        input_name = ncf.get_attr( pathname, 'INPUT_NAME' )
        return cls.create_new( value, input_name )
    
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
