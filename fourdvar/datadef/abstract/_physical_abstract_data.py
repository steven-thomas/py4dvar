"""
_physical_abstract_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.netcdf_handle as ncf

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    nvars = None
    nrows = None
    ncols = None
    uncertainty = None
    var_name = None
    
    def __init__( self, val_arr ):
        """
        application: create an instance of PhysicalData
        input: val = <list of value arrays>
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        msg = 'invalid physical data values.'
        assert val_arr.shape == (self.nvars,self.nrows,self.ncols,), msg
        self.value = val_arr
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

        attr_dict = { 'VAR_LIST': self.var_name }
        dim_dict = { 'VAR':self.nvars, 'ROW':self.nrows, 'COL':self.ncols }
        var_dict = { 'VALUE':('f4',('VAR','ROW','COL',),self.value),
                     'UNCERTAINTY':('f4',('VAR','ROW','COL',),self.uncertainty) }
        root = ncf.create( path=save_path, attr=attr_dict, dim=dim_dict, var=var_dict,
                           is_root=True )
        root.close()
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        val_arr = ncf.get_variable( filename, 'VALUE' )
        unc_arr = ncf.get_variable( filename, 'UNCERTAINTY' )
        var_list = ncf.get_attr( filename, 'VAR_LIST' )

        (nvar,nrow,ncol,) = val_arr.shape

        cls_parent = cls.__mro__[1]
        cls_parent.nvars = nvar
        cls_parent.nrows = nrow
        cls_parent.ncols = ncol
        cls_parent.uncertainty = unc_arr
        cls_parent.var_name = var_list
        
        return cls( val_arr )
    
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
