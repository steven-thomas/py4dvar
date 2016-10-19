"""
application: the adjoint forcing serves as input for the adjoint model run.
expresses influence of weighted residual of observations on model adjoint run.
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData
from fourdvar.datadef.model_output_data import ModelOutputData

from fourdvar.util.dim_defn import x_len, nstep

class AdjointForcingData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an AdjointForcingData to be valid.
    require = InterfaceData.add_require( 'data' )
    
    def __init__( self, data ):
        """
        application: create an instance of AdjointForcingData
        input: user-defined
        output: None
        
        eg: new_forcing =  datadef.AdjointForcingData( filelist )
        """
        #data is a 2d array of x_len, nstep+1 values
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, nstep+1 ), 'input data does not match model space'
        self.data = data.copy()
        return None
    
    def get_value( self, coord ):
        """
        application: return a single value from the provided lookup/co-ordinate
        input: user-defined
        output: scalar
        
        eg: forcing_value = forcing.get_value( day, time, row, col, lay )
        
        notes: only used for accuracy testing.
        """
        return self.data[ tuple( coord ) ]

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: AdjointForcingData
        
        eg: mock_forcing = datadef.AdjointForcingData.example()
        
        notes: only used for testing.
        """
        arglist = 1.0 + np.zeros(( x_len, nstep+1 ))
        return cls( arglist )
    
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
        assert isinstance( m_out, ModelOutputData )
        return cls( m_out.data.copy() )
    
    @classmethod
    def clone( cls, source ):
        """
        application: copy an AdjointForcingData.
        input: AdjointForcingData
        output: AdjointForcingData
        
        eg: forcing_copy = datadef.AdjointForcingData.clone( current_forcing )
        
        notes: only used for testing. ensure that copy is independant (eg: uses copies of files, etc.)
        """
        assert isinstance( source, cls )
        return cls( source.data.copy() )
    
    def cleanup( self ):
        """
        application: called when forcing is no longer required
        input: None
        output: None
        
        eg: old_forcing.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        pass
        return None

