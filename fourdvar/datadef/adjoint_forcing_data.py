"""
application: the adjoint forcing serves as input for the adjoint model run.
expresses influence of weighted residual of observations on model adjoint run.
"""

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData
#from fourdvar.datadef.model_output_data import ModelOutputData

import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.cmaq_datadef_files import adjoint_forcing_files as file_data
from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class AdjointForcingData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an AdjointForcingData to be valid.
    #require = InterfaceData.add_require( 'data' )
    file_data = file_data

    def __init__( self, **kwargs ):
        """
        application: create an instance of AdjointForcingData
        input: user-defined
        output: None
        
        eg: new_forcing =  datadef.AdjointForcingData( filelist )
        """
        #each input arg is a dictionary, matching to a record in file_details[class_name]
        #arg name matches the record key
        #arg value is a dictionary, keys are variable in file, values are numpy arrays
        assert len(file_data) == len(kwargs), 'input args do not match file_details'
        for label, data in kwargs.items():
            assert label in file_data.keys(), '{} not in file_details'.format( label )
            err_msg = "{} data doesn't match template.".format( label )
            assert ncf.validate( file_data[ label ][ 'template' ], data ), err_msg
        
        for label, record in file_data.items():
            ncf.create_from_template( record[ 'template' ],
                                      record[ 'actual' ],
                                      kwargs[ label ] )
        return None
    
    def get_variable( self, file_label, varname ):
        """
        extension: return an array of a single variable
        input: string, string
        output: numpy.ndarray
        """
        err_msg = 'file_label {} not in file_details'.format( file_label )
        assert file_label in file_data.keys(), err_msg
        return ncf.get_variable( file_data[file_label]['actual'], varname )
    
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
        for record in file_data.values():
            source = record['actual']
            dest = os.path.join( save_path, record['archive'] )
            ncf.copy_compress( source, dest )
        return None

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: AdjointForcingData
        
        eg: mock_forcing = datadef.AdjointForcingData.example()
        
        notes: only used for testing.
        """
        argdict = { label: {} for label in file_data.keys() }
        return cls( **argdict )
    
    @classmethod
    def from_model( cls, m_out ):
        """
        application: return valid forcing copied from model output.
        input: ModelOutputData
        output: AdjointForcingData
        
        eg: new_forcing = datadef.AdjointForcingData.from_model( modelout )
        
        notes: only used for accuracy testing.
        """
        #generate forcing directly from model_output
        #assert isinstance( m_out, ModelOutputData )
        #return cls( m_out.data.copy() )
        pass
    
    def cleanup( self ):
        """
        application: called when forcing is no longer required
        input: None
        output: None
        
        eg: old_forcing.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        for record in file_data.values():
            os.remove( record['actual'] )
        return None

