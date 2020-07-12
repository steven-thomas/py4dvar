"""
uncondition.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import UnknownData, PhysicalData
from fourdvar.params.input_defn import inc_icon

def uncondition( unknown ):
    """
    application: undo pre-conditioning of PhysicalData, add back any lost metadata
    input: UnknownData
    output: PhysicalData
    
    notes: this function must apply the prior error covariance
    """
    PhysicalData.assert_params()
    p = PhysicalData
    emis_len = p.nstep * p.nlays_emis * p.nrows * p.ncols
    emis_shape = (p.nstep, p.nlays_emis, p.nrows, p.ncols,)
    if inc_icon is True:
        total_len = len( p.spcs ) * ( 1 + emis_len )
    else:
        total_len = len( p.spcs ) * emis_len
    del p
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    emis_dict = {}
    i = 0
    for spc in PhysicalData.spcs:
        if inc_icon is True:
            icon = vals[ i ]
            i += 1
            icon = icon * PhysicalData.icon_unc[ spc ]
            icon_dict[ spc ] = icon
        
        emis = vals[ i:i+emis_len ]
        i += emis_len
        emis = emis.reshape( emis_shape)
        emis = emis * PhysicalData.emis_unc[ spc ]
        emis_dict[ spc ] = emis
    
    assert i == total_len, 'Some physical data left unassigned!'
    
    if inc_icon is False:
        icon_dict = None
    return PhysicalData( icon_dict, emis_dict )

