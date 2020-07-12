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

import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.cmaq_io_files import get_filedict
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
        
        notes: assumes all files already exist,
        to create files see create_new or load_from_archive
        """
        self.file_data = get_filedict( self.__class__.__name__ )
        
        #check that required files exist
        for record in self.file_data.values():
            exists = os.path.isfile( record[ 'actual' ] )
            assert exists, 'missing file {}'.format( record[ 'actual' ] )
        return None
    
    def get_variable( self, file_label, varname ):
        """
        extension: return an array of a single variable
        input: string, string
        output: numpy.ndarray
        """
        err_msg = 'file_label {} not in file_data'.format( file_label )
        assert file_label in self.file_data.keys(), err_msg
        return ncf.get_variable( self.file_data[file_label]['actual'], varname )
    
    def archive( self, dirname=None ):
        """
        extension: save copy of files to archive/experiment directory
        input: string or None
        output: None
        
        notes: this will overwrite any clash of namespace.
        if input is None file will write to experiment directory
        else it will create dirname in experiment directory and save there.
        """
        save_path = get_archive_path()
        if dirname is not None:
            save_path = os.path.join( save_path, dirname )
        ensure_path( save_path, inc_file=False )
        for record in self.file_data.values():
            source = record['actual']
            dest = os.path.join( save_path, record['archive'] )
            ncf.copy_compress( source, dest )
        return None
    
    @classmethod
    def create_new( cls, **kwargs ):
        """
        application: create an instance of ModelInputData from template with modified values.
        input: user_defined
        output: ModelInputData
        """
        #each input arg is a dictionary, matching to a record in file_details[class_name]
        #arg name matches the record key
        #arg value is a dictionary, keys are variable in file, values are numpy arrays
        fdata = get_filedict( cls.__name__ )
        msg = 'input args incompatible with file list'
        assert set( fdata.keys() ) == set( kwargs.keys() ), msg
        for label, data in kwargs.items():
            err_msg = "{} data doesn't match template.".format( label )
            assert ncf.validate( fdata[ label ][ 'template' ], data ), err_msg
        
        for label, record in fdata.items():
            ncf.create_from_template( record[ 'template' ],
                                      record[ 'actual' ],
                                      var_change=kwargs[ label ],
                                      date=record[ 'date' ],
                                      overwrite=True )
        return cls()
    
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create a ModelInputData from previous archived files
        input: string (path/to/file)
        output: ModelInputData
        
        notes: this function assumes the filenames match current archive default names
        """
        pathname = os.path.realpath( dirname )
        assert os.path.isdir( pathname ), 'dirname must be an existing directory'
        filedict = get_filedict( cls.__name__ )
        for record in filedict.values():
            source = os.path.join( pathname, record['archive'] )
            dest = record['actual']
            ncf.copy_compress( source, dest )
        return cls()
    
    @classmethod
    def load_from_template( cls ):
        """
        extension: create a ModelInputData from the template files
        input: None
        output: ModelInputData
        """
        filedict = get_filedict( cls.__name__ )
        for record in filedict.values():
            source = record['template']
            dest = record['actual']
            ncf.copy_compress( source, dest )
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
        for record in self.file_data.values():
            os.remove( record['actual'] )
        return None
