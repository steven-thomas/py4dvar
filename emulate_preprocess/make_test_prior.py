
import numpy as np

from    pyscope.config                        import run_config
from    pyscope.common.structures             import emptyStruct
from    pyscope.io_wrapper.input_controller   import InputController

import context
import fourdvar.util.file_handle as fh
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import em_input_struct_fname
import fourdvar.params.input_defn as input_defn

coord_list = [(0,0,),(0,1,),(1,0,),(1,1,)]
index_list = [0,0,0,0]
assert len(coord_list) == len(index_list), 'lists must have same length.'

def get_leaf( obj, full_name ):
    nlist = full_name.split('.')
    nlen = len( nlist )
    new_obj = obj
    for ni, name in enumerate( nlist ):
        if ni == nlen-1:
            leaf_name = name
        else:
            new_obj = getattr( new_obj, name )
    return new_obj, leaf_name

param_fname = 'base_config.cfg'
config = run_config.setup_config_input( param_fname )
input_control = InputController( config.param )
input_control.setup_new_run()
param = run_config.process_config( config )

em_struct = [ EmulationInput.load( fname ) for fname in em_input_struct_fname ]

phys_list = []
for mod_i, coord in zip( index_list, coord_list ):
    val_list = []
    unc_list = []
    opt_list = []
    var_meta = em_struct[ mod_i ]
    for var_dict in var_meta.var_param:
        obj, name = get_leaf( param, var_dict['name'] )
        #ensure val is always a 1-D array.
        val = np.array( getattr( obj, name ) ).reshape(-1)
        if var_dict['is_target']:
            val_list.extend( val )
            #set unc to max of 10% of val or 1.0 if val == 0
            unc = .1*abs(val)
            unc[ unc<=0. ] = 1.0
            unc_list.extend( unc )
        else:
            opt_list.extend( val )

    p_dict = { 'value':np.array(val_list) }
    p_dict[ 'uncertainty' ] = np.array(unc_list)
    p_dict[ 'option_input' ] = np.array(opt_list)
    p_dict[ 'coord' ] = coord
    p_dict[ 'model_index' ] = mod_i
    phys_list.append( p_dict )
fh.save_list( phys_list, input_defn.prior_file )
