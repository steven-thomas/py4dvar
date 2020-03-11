"""
application: the adjoint forcing serves as input for the adjoint model run.
expresses influence of weighted residual of observations on model adjoint run.
"""

import cPickle as pickle
import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class AdjointForcingData( FourDVarData ):
    """application
    """
    archive_name = 'adjoint_forcing.pic'
    def __init__( self, data ):
        """
        application: create an instance of AdjointForcingData
        input: None
        output: None
        """
        # most work handled by the create_new classmethod.
        self.value = np.array( data)
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
        with open(save_path, 'wb') as picklefile:
            pickle.dump(self.value, picklefile)
        return None
        
    @classmethod
    def create_new( cls, data, **kwargs ):
        """
        application: create an instance of AdjointForcingData from template with new data
        input: user-defined
        output: AdjointForcingData
        
        eg: new_forcing =  datadef.AdjointForcingData( filelist )
        """
        return cls( data)

    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create an AdjointForcingData from previous archived files.
        input: string (path/to/file)
        output: AdjointForcingData
        """
        pathname = os.path.realpath( dirname )
        with open( pathname, 'wb' ) as picklefile:
            data = pickle.load( picklefile )
        
        return cls( data )
    
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

