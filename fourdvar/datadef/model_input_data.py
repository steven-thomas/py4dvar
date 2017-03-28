"""
application: Stores the input for the forward model.
Built from the PhysicalData class.
Used to handle any resolution/format changes between the model and backgroud/prior
"""
# input class for the fwd model, generated from PhysicalData

import numpy as np
import os

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.cmaq_io_files import get_filedict
from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import ensure_path

class ModelInputData( InterfaceData ):
    """application
    """
    
    #add to the require set all the attributes that must be defined for an ModelInputData to be valid.
    require = InterfaceData.add_require( 'file_data' )
    
    def __init__( self, **kwargs ):
        """
        application: create an instance of ModelInputData
        input: user-defined
        output: None
        
        eg: new_model_in =  datadef.ModelInputData( filelist )
        """
        #each input arg is a dictionary, matching to a record in file_details[class_name]
        #arg name matches the record key
        #arg value is a dictionary, keys are variable in file, values are numpy arrays
        self.file_data = get_filedict( self.__class__.__name__ )
        msg = 'input args incompatible with file list'
        assert set( self.file_data.keys() ) == set( kwargs.keys() ), msg
        need_time = set()
        for label, data in kwargs.items():
            err_msg = "{} data doesn't match template.".format( label )
            assert ncf.validate( self.file_data[ label ][ 'template' ], data ), err_msg
            for array in data.values():
                if len( array.shape ) == 4 and array.shape[0] > 1:
                    #data has a timestep (ie: not icon)
                    need_time.add( (label, array.shape[0]) )
        
        #if file in need_time, check file TSTEP is compatible 
        for label, nstep in need_time:
            step_file = self.file_data[ label ][ 'template' ]
            tstep = int( ncf.get_attr( step_file, 'TSTEP' ) )
            tsec = 3600*(tstep//10000) + 60*((tstep//100)%100) + (tstep%100)
            daysec = 24*60*60
            assert daysec % tsec == 0, 'timestep must cleanly divide a day.'
            msg = '{0} must have {1} timesteps.'.format( label, daysec//tsec + 1 )
            assert (nstep-1) % (daysec//tsec) == 0, msg
        
        for label, record in self.file_data.items():
            ncf.create_from_template( record[ 'template' ],
                                      record[ 'actual' ],
                                      var_change=kwargs[ label ],
                                      date=record[ 'date' ] )
        return None
    
    def get_variable( self, file_label, varname ):
        """
        extension: return an array of a single variable
        input: string, string
        output: numpy.ndarray
        """
        err_msg = 'file_label {} not in file_data'.format( file_label )
        assert file_label in self.file_data.keys(), err_msg
        return ncf.get_variable( self.file_data[file_label]['actual'], varname )
    
    def archive( self, dirname=None ):
        """
        extension: save copy of files to archive/experiment directory
        input: string or None
        output: None
        
        notes: this will overwrite any clash of namespace.
        if input is None file will write to experiment directory
        else it will create dirname in experiment directory and save there.
        """
        save_path = get_archive_path()
        if dirname is not None:
            save_path = os.path.join( save_path, dirname )
        ensure_path( save_path, inc_file=False )
        for record in self.file_data.values():
            source = record['actual']
            dest = os.path.join( save_path, record['archive'] )
            ncf.copy_compress( source, dest )
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
        filedict = get_filedict( cls.__name__ )
        argdict = { label: {} for label in filedict.keys() }
        return cls( **argdict )    
    
    def cleanup( self ):
        """
        application: called when model input is no longer required
        input: None
        output: None
        
        eg: old_model_in.cleanup()
        
        notes: called after test instance is no longer needed,
               used to delete files etc.
        """
        for record in self.file_data.values():
            os.remove( record['actual'] )
        return None
