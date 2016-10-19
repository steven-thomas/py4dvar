"""
application: Stores the input for the forward model.
Built from the PhysicalData class.
Used to handle any resolution/format changes between the model and backgroud/prior
"""
# input class for the fwd model, generated from PhysicalData

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.dim_defn import x_len

class ModelInputData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an ModelInputData to be valid.
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        """
        application: create an instance of ModelInputData
        input: user-defined
        output: None
        
        eg: new_model_in =  datadef.ModelInputData( filelist )
        """
        #data is an array of x_len x-values
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    def get_value( self, i ):
        """
        application: return a single value from the provided lookup/co-ordinate
        input: user-defined
        output: scalar
        
        eg: conc_value = model_in.get_value( day, time, row, col, lay )
        
        notes: only used for accuracy testing.
        """
        return self.data[i]
    
    def set_value( self, i, val ):
        """
        application: change a single value from the provided lookup/co-ordinate to provided value
        input: user-defined
        output: None
        
        eg: model_in.set_value( new_conc, day, time, row, col, lay )
        
        notes: only used for accuracy testing. Should use same lookup as get_value.
        """
        self.data[i] = val
        return None
    
    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: ModelInputData
        
        eg: mock_model_in = datadef.ModelInputData.example()
        
        notes: only used for testing.
        """
        arglist = 1.0 + np.zeros( x_len )
        return cls( arglist )
    
    @classmethod
    def clone( cls, source ):
        """
        application: copy a ModelInputData.
        input: ModelInputData
        output: ModelInputData
        
        eg: model_in_copy = datadef.ModelInputData.clone( current_model_in )
        
        notes: only used for testing. ensure that copy is independant (eg: uses copies of files, etc.)
        """
        assert isinstance( source, cls )
        return cls( source.data.copy() )
    
    def cleanup( self ):
        """
        application: called when model input is no longer required
        input: None
        output: None
        
        eg: old_model_in.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        return None

