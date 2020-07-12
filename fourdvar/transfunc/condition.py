"""
condition.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
from __future__ import absolute_import

import numpy as np

from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.datadef import UnknownData
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
    ncells = p.nall_cells
    nstep = p.nstep
    spcs_list = p.spcs
    nunknowns = p.nunknowns
    eigen_vectors = p.eigen_vectors
    eigen_values = p.eigen_values
    bcon_len = p.nstep_bcon * p.bcon_region
    del p

    if inc_icon is True:
        total_len = len( spcs_list )*(1+bcon_len) + sum( nunknowns )
    else:
        total_len = len( spcs_list )*bcon_len + sum( nunknowns )
    
    #weighting function changes if is_adjoint
    if is_adjoint is True:
        weight = lambda val, sd: val * sd
    else:
        weight = lambda val, sd: val / sd
    
    arg = np.zeros( total_len )
    i = 0
    for spc in spcs_list:
        if inc_icon is True:
            icon = weight( physical.icon[ spc ], physical.icon_unc[ spc ] )
            arg[ i ] = icon
            i += 1

    for t in range( nstep ):
        emis_vector = np.zeros( ncells )
        for ns,spc in enumerate( spcs_list ):
            emis = physical.emis[ spc ][t,...].flatten()
            emis_vector[ ns*emis.size : (ns+1)*emis.size ] = emis[:]
        emis_vector = np.dot( emis_vector, eigen_vectors[t] )
        emis_vector = weight( emis_vector, eigen_values[t] )
        arg[ i : i+nunknowns[t] ] = emis_vector[:]
        i += nunknowns[t]
    
    for spc in spcs_list:
        bcon = weight( physical.bcon[ spc ], physical.bcon_unc[ spc ] )
        arg[ i:i+bcon_len ] = bcon.flatten()
        i += bcon_len

    assert i == total_len, 'did not map expected number of unknowns.'
    return UnknownData( arg )
