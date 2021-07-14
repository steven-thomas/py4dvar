
# Imports
#import sys
import numpy as np
import os
import sys
import copy
import shutil
import pickle

#special change, add yourself to sys.path to call scope.
mydir = os.path.dirname( os.path.realpath( __file__ ) )
sys.path.append( mydir )

from pyscope.config                        import run_config
from pyscope.io_wrapper.input_controller   import InputController
from pyscope.pySCOPE                       import run_scope

import context
from emulate_preprocess.training_defn import em_training_index
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import scope_setup_fname_list

use_archive = True
vector_input_archive = []
vector_output_archive = []

#spectral weighting term for output flourescence
spec_weight = np.zeros((211,))
spec_weight[122] = 1.

param_fname = os.path.join( mydir, 'base_config.cfg' )

setup_index = em_training_index

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

def move_config( config, dname ):
    orig_dir = config.param.paths.input
    if orig_dir.endswith('/'):
        orig_dir = orig_dir[:-1]
    new_dir = os.path.join( orig_dir, dname )
    if not os.path.isdir( new_dir ):
        os.mkdir( new_dir )
    config.param.paths.input = new_dir
    config.param.atmo.atmofile = config.param.atmo.atmofile.replace(orig_dir,new_dir)
    config.param.directional.anglesfile = config.param.directional.anglesfile.replace(orig_dir,new_dir)
    config.param.optipar.optifile = config.param.optipar.optifile.replace(orig_dir,new_dir)
    config.param.soil.soil_file = config.param.soil.soil_file.replace(orig_dir,new_dir)
    return config

def vector_scope( x, dname=None ):

    if input_var is None:
        raise ValueError('Must set input_var first.')

    if use_archive is True:
        global vector_input_archive
        global vector_output_archive
        vector_input_archive.append( np.array(x[0]) )
    
    input_list = list(x[0])
    #new_run = copy.copy( base_param )
    config = run_config.setup_config_input( param_fname )
    if dname is not None:
        config = move_config( config, dname )
    input_control = InputController( config=config.param, src_path=mydir )
    input_control.setup_new_run()
    new_run = config.param

    #update attributes of param object with specific emulation setup values.
    setup_fname = scope_setup_fname_list[setup_index]
    with open( setup_fname, 'rb' ) as f:
        setup_dict = pickle.load(f)
    for full_name, value in setup_dict.items():
        obj, name = get_leaf( new_run, full_name )
        setattr( obj, name, value )

    #update attributes of new param object with input values
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
            if type( in_name ) == str:
                obj, name = get_leaf( new_run, in_name )
                in_val.append( getattr( obj, name ) )
            else:
                in_val.append( in_name )
        if s_dict['func'] == 'sum':
            new_val = sum( in_val )
        elif s_dict['func'] == 'prod':
            new_val = np.prod( in_val )
        else:
            raise ValueError('unknown setup function {:}'.format(s_dict['func']))
        obj, name = get_leaf( new_run, s_dict['name'] )
        setattr( obj, name, new_val )

    config.param = new_run
    param = run_config.process_config( config )

    param = run_config.process_config( config )
    output_control = run_scope( param )
    out_scale = (output_control.rad.LoF_ * spec_weight).sum()

    if use_archive is True:
        vector_output_archive.append( out_scale )
    if dname is not None:
        shutil.rmtree( config.param.paths.input )
    return out_scale
