"""
application: Stores the input for the forward model.
Built from the PhysicalData class.
Used to handle any resolution/format changes between the model and backgroud/prior
"""
# input class for the fwd model, generated from PhysicalData

import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.file_handle as fh
import fourdvar.params.model_data as md


class ModelInputData( FourDVarData ):
    """application
    """
    archive_name = 'model_input.pic.gz'
    rainfall_driver = None
    
    def __init__( self, params, x0 ):
        """
        application: create an instance of ModelInputData
        input: user-defined
        output: None
        """
        self.p = params
        self.x = x0
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
        datalist = [ self.p, self.x, md.rd_filename ]
        fh.save_list( datalist, save_path )
        return None
        
    @classmethod
    def create_new( cls, params, x0 ):
        """
        application: create an instance of ModelInputData from template with modified values.
        input: user_defined
        output: ModelInputData
        """
        assert len(params) == 5, 'invalid optic parameters'
        assert len(x0) == 2, 'invalid optic initial conditions'
        if cls.rainfall_driver is None:
            rd_list = fh.load_list( md.rd_filename )
            cls.rainfall_driver = np.array( rd_list )
        return cls( params, x0 )
    
    #OPTIONAL
    @classmethod
    def load_from_archive( cls, dirname ):
        """
        extension: create a ModelInputData from previous archived files
        input: string (path/to/file)
        output: ModelInputData
        """
        pathname = os.path.realpath( dirname )
        params,x0,rain_file = fh.load_list( pathname )
        assert rain_file == md.rd_filename, 'wrong rainfall driver'
        return cls.create_new( params, x0 )
    
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
