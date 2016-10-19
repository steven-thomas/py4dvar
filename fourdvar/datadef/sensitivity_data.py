"""
application: stores output from adjoint model
should contain data with a similar shape to ModelInputData
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.dim_defn import x_len

class SensitivityData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an AdjointForcingData to be valid.
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        """
        application: create an instance of SensitivityData
        input: user-defined
        output: None
        
        eg: new_sense =  datadef.SensitivityData( filelist )
        """
        #data is an array of x_len x-values
        InterfaceData.__init__( self )
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    def get_value( self, i ):
        """
        application: return a single value from the provided lookup/co-ordinate
        input: user-defined
        output: scalar
        
        eg: sense_value = sensitivity.get_value( day, time, row, col, lay )
        
        notes: only used for accuracy testing.
        """
        return self.data[i]
    
    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: SensitivityData
        
        eg: mock_sensitivity = datadef.SensitivityData.example()
        
        notes: only used for testing.
        """
        arglist = 1.0 + np.zeros( x_len )
        return cls( arglist )
    
    @classmethod
    def clone( cls, source ):
        """
        application: copy a SensitivityData instance.
        input: SensitivityData
        output: SensitivityData
        
        eg: sense_copy = datadef.SensitivityData.clone( current_sense )
        
        notes: only used for testing. ensure that copy is independant (eg: uses copies of files, etc.)
        """
        assert isinstance( cls, source )
        return cls( source.data.copy() )
    
    def cleanup( self ):
        """
        application: called when sensitivity is no longer required
        input: None
        output: None
        
        eg: sensitivity.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        pass
        return None

