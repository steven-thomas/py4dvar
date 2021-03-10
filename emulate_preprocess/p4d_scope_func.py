
# Imports
#import sys
import numpy as np
import os
import sys
import copy

#special change, add yourself to sys.path to call scope.
mydir = os.path.dirname( os.path.realpath( __file__ ) )
sys.path.append( mydir )

from pyscope.config                        import run_config
from pyscope.io_wrapper.input_controller   import InputController
from pyscope.pySCOPE                       import run_scope

import context
from fourdvar.util.emulate_input_struct import EmulationInput

#spectral weighting term for output flourescence
spec_weight = np.zeros((211,))
spec_weight[122] = 1.

param_fname = os.path.join( mydir, 'base_config.cfg' )
config = run_config.setup_config_input( param_fname )
input_control = InputController( config=config.param, src_path=mydir )
input_control.setup_new_run()
param = run_config.process_config( config )

input_var = None
def set_input( input_fname ):
    global input_var
    input_var = EmulationInput.load( input_fname )
    return None

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

def vector_scope( x ):

    if input_var is None:
        raise ValueError('Must set input_var first.')
    
    input_list = list(x[0])
    new_run = copy.copy( param )

    #update attributes (or sub-attributes) of new param object
    for var_dict in input_var.var_param:
        obj, name = get_leaf( new_run, var_dict['name'] )
        vlen = var_dict['size']
        vshape = var_dict['shape']
        val = input_list[:vlen]
        input_list = input_list[vlen:]
        if vshape is None:
            #set scalar
            setattr( obj, name, val[0] )
        else:
            setattr( obj, name, np.reshape(val,vshape) )

    #set input values that are determined from the var-dict variables
    for s_dict in input_var.setup_func:
        in_val = []
        for in_name in s_dict['input']:
            obj, name = get_leaf( new_run, in_name )
            in_val.append( getattr( obj, name ) )
        if s_dict['func'] == 'sum':
            new_val = sum( in_val )
        else:
            raise ValueError('unknown setup function {:}'.format(s_dict['func']))
        obj, name = get_leaf( new_run, s_dict['name'] )
        setattr( obj, name, new_val )
                
    output_control = run_scope( new_run )
    out_scale = (output_control.rad.LoF_ * spec_weight).sum()
    return out_scale
