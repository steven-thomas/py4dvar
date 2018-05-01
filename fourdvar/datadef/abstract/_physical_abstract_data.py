"""
application: format used to store data on physical space of interest
parent of PhysicalData & PhysicalAdjointData classes,
the two child classes share almost all attributes
therefore most of their code is here.
"""

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

from fourdvar.util.archive_handle import get_archive_path

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """    
    def __init__( self, ... ):
        """
        application: create an instance of PhysicalData
        input: user-defined
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
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
        #save data to save_path
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        return cls( ... )
    
    def cleanup( self ):
        """
        application: called when physical data instance is no longer required
        input: None
        output: None
        
        eg: old_phys.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        #function must exist but can be left blank
        pass
        return None
