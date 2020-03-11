"""
application: format used to store data on physical space of interest
parent of PhysicalData & PhysicalAdjointData classes,
the two child classes share almost all attributes
therefore most of their code is here.
"""

#import cPickle as pickle
import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.file_handle as fh

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    uncertainty = None
    s0 = None
    x0 = None
    def __init__( self, params):
        """
        application: create an instance of PhysicalData
        input: params = [p1,p2,k1,k2]
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        assert len(params) == 4, 'invalid parameter set'
        assert self.uncertainty is not None, 'uncertainty not set'
        assert self.s0 is not None, 's0 not set'
        assert self.x0 is not None, 'x0 not set'
        self.params = np.array( params )
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
        datalist = [ self.params, self.s0, self.x0, self.uncertainty ]
        fh.save_list( datalist, save_path )
        return None
    
    @classmethod
    def _set_unc( cls, uncertainty ):
        """define uncertainty for the 4 parameters we want to solve for:
        p1, p2, k1, k2"""
        #define parent class explicitly so calling from child will set parents variable
        unc = np.array( uncertainty )
        assert unc.size == 4, 'invalid set of uncertainties'
        assert (unc>0).all(), 'uncertainties must be > 0.'
        if cls.uncertainty is not None and (cls.uncertainty!=unc).all():
            logger.warn( 'Overwriting PhysicalData.uncertainty globally!' )
        PhysicalAbstractData.uncertainty = unc
        return None

    @classmethod
    def _set_s0( cls, s0 ):
        """define s0 (seed term) parameter (not solved for)"""
        #define parent class explicitly so calling from child will set parents variable
        if cls.s0 is not None and (cls.s0!=s0):
            logger.warn( 'Overwriting PhysicalData.s0 globally!' )
        PhysicalAbstractData.s0 = s0
        return None

    @classmethod
    def _set_x0( cls, x0 ):
        """define x0 (inital state) parameters x0_1, x0_2 (not solved for)"""
        #define parent class explicitly so calling from child will set parents variable
        x0 = np.array( x0 )
        assert x0.size == 2, 'invalid x0, must be a pair.'
        if cls.x0 is not None and (cls.x0!=x0).all():
            logger.warn( 'Overwriting PhysicalData.x0 globally!' )
        PhysicalAbstractData.x0 = x0
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        datalist = fh.load_list( filename )
        params,s0,x0,uncertainty = datalist
        cls._set_unc( uncertainty )
        cls._set_s0( s0 )
        cls._set_x0( x0 )
        return cls( np.array(params) )
    
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
