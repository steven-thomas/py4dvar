"""
application: stores data on physical space of interest
used to store prior/background, construct model input and minimizer input
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

#from fourdvar.util.file_handle import get_dict
#from fourdvar.util.dim_defn import x_len


class PhysicalData( InterfaceData ):
    """Starting point of background, link between model and unknowns
    """
    
    #add to the require set all the attributes that must be defined for an AdjointForcingData to be valid.
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        """
        application: create an instance of PhysicalData
        input: user-defined
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        #data is an array of x_len x-values
        InterfaceData.__init__( self )
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        read_dict = get_dict( filename )
        return cls( read_dict['x'] )

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: PhysicalData
        
        eg: mock_phys = datadef.PhysicalData.example()
        
        notes: only used for testing.
        """
        arglist = 1.0 + np.zeros( x_len )
        return cls( arglist )
    
    @classmethod
    def clone( cls, source ):
        """
        application: copy a PhysicalData instance.
        input: PhysicalData
        output: PhysicalData
        
        eg: phys_copy = datadef.PhysicalData.clone( current_phys )
        
        notes: only used for testing. ensure that copy is independant (eg: uses copies of files, etc.)
        """
        assert isinstance( source, cls )
        return cls( source.data.copy() )
    
    def cleanup( self ):
        """
        application: called when physical data instance is no longer required
        input: None
        output: None
        
        eg: old_phys.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        pass
        return None

