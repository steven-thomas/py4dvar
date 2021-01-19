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
import fourdvar.util.file_handle as fh

class ModelInputData( FourDVarData ):
    """application
    """
    archive_name = 'model_input.pic.gz'
    coord = None
    model_index = None
    
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

        mod_list = []
        for i in range( len( self.value ) ):
            mdict = { 'value': self.value[i] }
            mdict[ 'coord' ] = self.coord[i]
            mdict[ 'model_index' ] = self.model_index[i]
            mod_list.append( mdict )
        
        fh.save_list( mod_list, save_path )
        return None
        
    @classmethod
    def create_new( cls, value, coord=None, model_index=None ):
        """
        application: create an instance of ModelInputData from template with modified values.
        input: user_defined
        output: ModelInputData
        """
        if cls.coord is None:
            assert coord is not None, 'model_input.coord must be defined.'
            cls.coord = coord
        elif coord is not None:
            assert cls.coord == coord, "Can't replace model input coord"
        if cls.model_index is None:
            assert model_index is not None, 'model_input.model_index must be defined.'
            cls.model_index = model_index
        elif model_index is not None:
            assert cls.model_index == model_index, "Can't replace model input model_index."
        assert len(value) == len(cls.coord), 'input values invalid.'
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
        mod_list = fh.load_list( pathname )
        val = [ np.array( md['value'] ) for md in mod_list ]
        coord = [ md['coord'] for md in mod_list ]
        model_index = [ md['model_index'] for md in mod_list ]
        return cls.create_new( value, coord, model_index )
    
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
