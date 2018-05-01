"""
application: the adjoint forcing serves as input for the adjoint model run.
expresses influence of weighted residual of observations on model adjoint run.
"""

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class AdjointForcingData( FourDVarData ):
    """application
    """
    
    def __init__( self ):
        """
        application: create an instance of AdjointForcingData
        input: None
        output: None
        """
        # most work handled by the create_new classmethod.
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
        #save data to save_path
        return None
        
    @classmethod
    def create_new( cls, **kwargs ):
        """
        application: create an instance of AdjointForcingData from template with new data
        input: user-defined
        output: AdjointForcingData
        
        eg: new_forcing =  datadef.AdjointForcingData( filelist )
        """
        return cls()

    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create an AdjointForcingData from previous archived files.
        input: string (path/to/file)
        output: AdjointForcingData
        """
        pathname = os.path.realpath( dirname )
        assert os.path.isdir( pathname ), 'dirname must be an existing directory'
        #load data from archive format
        return cls()
    
    def cleanup( self ):
        """
        application: called when forcing is no longer required
        input: None
        output: None
        
        eg: old_forcing.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        # function needed but can be left blank
        return None

