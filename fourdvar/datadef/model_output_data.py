"""
application: stores/references the output of the forward model.
used to construct the simulated observations.
"""

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.cmaq_datadef_files import get_filedict
from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class ModelOutputData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for a ModelOutputData to be valid.
    require = InterfaceData.add_require( 'file_data' )

    def __init__( self ):
        """
        application: create an instance of ModelOutputData
        input: user-defined
        output: None
        
        eg: new_output =  datadef.ModelOutputData( filelist )
        """
        #just check all required files exist
        self.file_data = get_filedict( self.__class__.__name__ )
        for record in self.file_data.values():
            assert os.path.isfile( record['actual'] ), 'missing {}'.format( record['actual'] )
        #OPTIONAL: convert daily files into single arrays?
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
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: ModelOutputData
        
        eg: mock_model_out = datadef.ModelOutputData.example()
        
        notes: only used for testing.
        """
        filedict = get_filedict( cls.__name__ )
        for record in filedict.values():
            ncf.create_from_template( record['template'], record['actual'], {} )
        return cls()
    
    def cleanup( self ):
        """
        application: called when model output is no longer required
        input: None
        output: None
        
        eg: old_model_out.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        for record in self.file_data.values():
            os.remove( record['actual'] )
        return None

