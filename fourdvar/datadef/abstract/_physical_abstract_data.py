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
import fourdvar.util.file_handle as fh
import fourdvar.params.model_data as md

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    size = None
    uncertainty = None
    option_input = None
    coord = None
    model_index = None
    
    def __init__( self, val ):
        """
        application: create an instance of PhysicalData
        input: val = <list of value arrays>
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        assert [ v.size for v in val ] == self.size, 'invalid physical data values.'
        self.value = val
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

        phys_list = []
        for i in range( len(self.size) ):
            pdict = { 'value':self.value[i] }
            pdict[ 'uncertainty' ] = self.uncertainty[i]
            pdict[ 'option_input' ] = self.option_input[i]
            pdict[ 'coord' ] = self.coord[i]
            pdict[ 'model_index' ] = self.model_input[i]
            phys_list.append( pdict )
        
        fh.save_list( phys_list, save_path )
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        phys_list = fh.load_list( filename )
        val = [ np.array( pdict.pop('value') ) for pdict in phys_list ]
        unc = [ np.array( pdict.pop('uncertainty') ) for pdict in phys_list ]
        opt = [ np.array( pdict.pop('option_input') ) for pdict in phys_list ]
        coord = [ pdict.pop('coord') for pdict in phys_list ]
        mod = [ pdict.pop('model_index') for pdict in phys_list ]

        if cls.size is not None:
            logger.warn( 'Overwriting PhysicalData meta data' )
        cls.size = [ v.size for v in val ]
        cls.uncertainty = unc
        cls.option_input = opt
        cls.coord = coord
        cls.model_index = mod

        #populate model data
        md.coord_list = [ c for c in coord ]
        md.model_index = [ m for m in mod ]
        
        return cls( val )
    
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
