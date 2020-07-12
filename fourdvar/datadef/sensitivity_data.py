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

import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.cmaq_io_files import get_filedict
from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class SensitivityData( FourDVarData ):
    """application
    """
    
    #list of attributes that must match between actual and template
    checklist = [ 'STIME', 'TSTEP', 'NCOLS', 'NROWS', 'NLAYS', 'NVARS',
                  'GDTYP', 'P_ALP', 'P_BET', 'P_GAM', 'XCENT', 'YCENT',
                  'XORIG', 'YORIG', 'XCELL', 'YCELL',
                  'VGTYP', 'VGTOP', 'VGLVLS', 'VAR-LIST' ]
        
    def __init__( self ):
        """
        application: create an instance of SensitivityData
        input: user-defined
        output: None
        
        eg: new_sense =  datadef.SensitivityData( filelist )
        """        
        #check all required files exist and match attributes with templates
        self.file_data = get_filedict( self.__class__.__name__ )
        for record in self.file_data.values():
            actual = record[ 'actual' ]
            template = record[ 'template' ]
            msg = 'missing {}'.format( actual )
            assert os.path.isfile( actual ), msg
            msg = '{} is incompatible with template {}.'.format( actual, template )
            assert ncf.match_attr( actual, template, self.checklist ) is True, msg
        return None
    
    def get_variable( self, file_label, varname ):
        """
        extension: return an array of a single variable
        input: string, string
        output: numpy.ndarray
        """
        err_msg = 'file_label {} not in file_details'.format( file_label )
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
    def load_from_archive( cls, dirname ):
        """
        extension: create a SensitivityData from previous archived files.
        input: string (path/to/file)
        output: SensitivityData
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
        application: return a valid example with template values.
        input: None
        output: SensitivityData
        
        notes: only used for testing.
        """
        filedict = get_filedict( cls.__name__ )
        for record in filedict.values():
            ncf.create_from_template( record['template'], record['actual'],
                                      var_change={}, date=record['date'] )
        return cls()
    
    def cleanup( self ):
        """
        application: called when sensitivity is no longer required
        input: None
        output: None
        
        eg: sensitivity.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        for record in self.file_data.values():
            os.remove( record['actual'] )
        return None
