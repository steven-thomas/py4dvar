"""
uncondition.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

import fourdvar.util.netcdf_handle as ncf
from fourdvar.datadef import UnknownData, PhysicalData
from fourdvar.params.input_defn import inc_icon
import fourdvar.params.template_defn as template

def uncondition( unknown ):
    """
    application: undo pre-conditioning of PhysicalData, add back any lost metadata
    input: UnknownData
    output: PhysicalData
    
    notes: this function must apply the prior error covariance
    """
    PhysicalData.assert_params()
    p = PhysicalData
    ncat = len( p.cat )
    emis_len = ncat * p.nstep * p.nlays_emis * p.nrows * p.ncols
    emis_shape = ( ncat, p.nstep, p.nlays_emis, p.nrows, p.ncols, )
    if inc_icon is True:
        icon_len = p.nlays_icon * p.nrows * p.ncols
        icon_shape = ( p.nlays_icon, p.nrows, p.ncols, )
    del p
    
    diurnal = ncf.get_variable( template.diurnal, PhysicalData.spcs )
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    emis_dict = {}
    i = 0
    for spc in PhysicalData.spcs:
        if inc_icon is True:
            icon = vals[ i:i+icon_len ]
            icon = icon.reshape( icon_shape )
            icon_dict[ spc ] = icon * PhysicalData.icon_unc[ spc ]
            i += icon_len
        
        emis_arr = np.zeros( emis_shape )
        cat_arr = diurnal[ spc ][ :-1, :PhysicalData.nlays_emis, :, : ]
        for c in range( ncat ):
            nan_arr = (cat_arr == c).sum( axis=0, keepdims=True )
            nan_arr = np.where( (nan_arr==0), np.nan, 0. )
            emis_arr[ c, :, :, :, : ] = nan_arr
        
        emis_len = np.count_nonzero( ~np.isnan(emis_arr) )
        emis_vector = vals[ i:i+emis_len ]
        emis_arr[ ~np.isnan(emis_arr) ] = emis_vector
        emis_dict[ spc ] = emis_arr * PhysicalData.emis_unc[ spc ]
        i += emis_len
        
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict )

