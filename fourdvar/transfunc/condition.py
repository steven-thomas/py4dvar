"""
condition.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import UnknownData
from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.params.input_defn import inc_icon

def condition_adjoint( physical_adjoint ):
    """
    application: apply pre-conditioning to PhysicalAdjointData, get vector gradient
    input: PhysicalAdjointData
    output: UnknownData
    
    notes: this function must apply the prior error covariance
    """
    return phys_to_unk( physical_adjoint, True )

def condition( physical ):
    """
    application: apply pre-conditioning to PhysicalData, get vector to optimize
    input: PhysicalData
    output: UnknownData
    
    notes: this function must apply the inverse prior error covariance
    """
    return phys_to_unk( physical, False )

def phys_to_unk( physical, is_adjoint ):
    """
    application: apply pre-conditioning to PhysicalData, get vector to optimize
    input: PhysicalData
    output: UnknownData
    
    notes: this function must apply the inverse prior error covariance
    """
    p = PhysicalAbstractData
    emis_len = p.nstep_emis * p.nlays_emis * p.nrows * p.ncols
    bcon_len = p.nstep_bcon * p.bcon_region
    if inc_icon is True:
        total_len = len(p.spcs) * (1 + emis_len + bcon_len)
    else:
        total_len = len(p.spcs) * (emis_len + bcon_len)
    del p
    
    #weighting function changes if is_adjoint
    if is_adjoint is True:
        weight = lambda val, sd: val * sd
    else:
        weight = lambda val, sd: val / sd
    
    arg = np.zeros( total_len )
    i = 0
    for spc in PhysicalAbstractData.spcs:
        if inc_icon is True:
            icon = weight( physical.icon[ spc ], physical.icon_unc[ spc ] )
            arg[ i ] = icon
            i += 1

        emis = weight( physical.emis[ spc ], physical.emis_unc[ spc ] )
        arg[ i:i+emis_len ] = emis.flatten()
        i += emis_len

        bcon = weight( physical.bcon[ spc ], physical.bcon_unc[ spc ] )
        arg[ i:i+bcon_len ] = bcon.flatten()
        i += bcon_len
    assert i == total_len, 'Some unknowns left unassigned!'
    return UnknownData( arg )
