"""
application: undo pre-conditioning to UnknownData, get back PhysicalData (format of prior/background)
like all transform in transfunc this is referenced from the transform function
eg: transform( unknown_instance, datadef.PhysicalData ) == uncondition( unknown_instance )
"""
from __future__ import absolute_import

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
    ncells = p.nall_cells
    nstep = p.nstep
    spcs_list = p.spcs
    nunknowns = p.nunknowns
    eigen_vectors = p.eigen_vectors
    eigen_values = p.eigen_values
    e_slice_shape = ( p.nlays_emis, p.nrows, p.ncols )
    emis_shape = ( p.nstep, p.nlays_emis, p.nrows, p.ncols )
    bcon_shape = ( p.nstep_bcon, p.bcon_region, )
    bcon_len = np.prod( bcon_shape )
    del p
    
    vals = unknown.get_vector()
    if inc_icon is True:
        icon_dict = {}
    i = 0
    for spc in spcs_list:
        if inc_icon is True:
            icon = vals[ i ]
            i += 1
            icon = icon * PhysicalData.icon_unc[ spc ]
            icon_dict[ spc ] = icon

    emis_dict = { spc: np.zeros( emis_shape ) for spc in spcs_list }    
    for t in range( nstep ):
        emis_vector = vals[ i : i+nunknowns[t] ]
        i += nunknowns[t]
        
        emis_vector = emis_vector * eigen_values[t]
        emis_vector = np.dot( eigen_vectors[t], emis_vector )
        for ns,spc in enumerate( spcs_list ):
            e_len = np.prod( e_slice_shape )
            e_slice = emis_vector[ ns*e_len : (ns+1)*e_len ]
            emis = e_slice.reshape( e_slice_shape )
            emis_dict[ spc ][t,...] = emis[:]
    
    for spc in spcs_list:
        bcon = vals[ i:i+bcon_len ]
        bcon = bcon.reshape( bcon_shape )
        bcon_dict[ spc ] = bcon * PhysicalData.bcon_unc[ spc ]
        i += bcon_len
    
    if inc_icon is False:
        icon_dict = None
    assert i == vals.size, 'did not map expected number of unknowns.'
    return PhysicalData( icon_dict, emis_dict, bcon_dict )
