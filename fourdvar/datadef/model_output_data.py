"""
application: stores/references the output of the forward model.
used to construct the simulated observations.
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

from fourdvar.util.file_handle import save_array, rm
from fourdvar.util.dim_defn import x_len, nstep

class ModelOutputData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for a ModelOutputData to be valid.
    require = InterfaceData.add_require( 'data', 'fname' )
    #default filenames for examples & clones
    clone_fname = 'model_out.clone'
    example_fname = 'model_out.example'
    
    def __init__( self, data, fname ):
        """
        application: create an instance of ModelOutputData
        input: user-defined
        output: None
        
        eg: new_output =  datadef.ModelOutputData( filelist )
        """
        #data is a numpy array, saved to file 'fname' in fourdvar/data
        data = np.array( data, dtype='float64' )
        assert data.shape == ( x_len, nstep+1 ), 'input data does not match model space'
        self.data = data.copy()
        self.fname = fname
        save_array( self, self.data, self.fname, True )
        return None
    
    def get_value( self, coord ):
        """
        application: return a single value from the provided lookup/co-ordinate
        input: user-defined
        output: scalar
        
        eg: conc_value = model_out.get_value( day, time, row, col, lay )
        
        notes: only used for accuracy testing.
        """
        return self.data[ tuple( coord ) ]
    
    def set_value( self, coord, val ):
        """
        application: change a single value from the provided lookup/co-ordinate
        input: user-defined
        output: None
        
        eg: model_out.set_value( new_conc, day, time, row, col, lay )
        
        notes: only used for accuracy testing. Should use same lookup as get_value
        """
        self.data[ tuple( coord ) ] = val
        save_array( self, self.data, self.fname, True )
        return None
    
    def sum_square( self ):
        """
        application: return sum of squares
        input: None
        output: scalar
        
        eg: total = model_out.sum_square()
        
        notes: only used for accuracy testing.
        """
        return np.sum( self.data**2 )

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: ModelOutputData
        
        eg: mock_model_out = datadef.ModelOutputData.example()
        
        notes: only used for testing.
        """
        arglist = 1.0 + np.zeros(( x_len, nstep+1 ))
        return cls( arglist, cls.example_fname )
    
    @classmethod
    def clone( cls, source, fname=None ):
        """
        application: copy a ModelOutputData.
        input: ModelOutputData
        output: ModelOutputData
        
        eg: model_out_copy = datadef.ModelOutputData.clone( current_model_out )
        
        notes: only used for testing. ensure that copy is independant (eg: uses copies of files, etc.)
        """
        assert isinstance( source, cls )
        if fname is None:
            fname = cls.clone_fname
        return cls( source.data.copy(), fname )
    
    def cleanup( self ):
        """
        application: called when model output is no longer required
        input: None
        output: None
        
        eg: old_model_out.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        rm( self.fname )
        return None

