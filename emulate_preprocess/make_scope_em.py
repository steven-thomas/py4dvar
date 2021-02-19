#!/usr/bin/env python

# Imports
import sys
import numpy as np
import gp_emulator
import copy

from    pyscope.config                        import run_config
from    pyscope.common.structures             import emptyStruct
from    pyscope.io_wrapper.input_controller   import InputController
from    pyscope.pySCOPE                       import run_scope

import context
import fourdvar.params.scope_em_file_defn as em_file_defn
from fourdvar.util.emulate_input_struct import EmulationInput

input_fname = em_file_defn.em_input_struct_fname[0]
emulate_fname = em_file_defn.emulation_fname[0]

training_var = EmulationInput.load( input_fname )

#spectral weighting term for output flourescence
spec_weight = np.zeros((211,))
spec_weight[122] = 1.

#n_train = 500
#n_validate = 500
n_train = 100
n_validate = 100

# Initialize simulation with baseline inputs
param_fname = 'base_config.cfg'
config = run_config.setup_config_input( param_fname )
input_control = InputController( config.param )
input_control.setup_new_run()
param = run_config.process_config( config )

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
    input_list = list(x[0])
    new_run = copy.copy( param )

    #update attributes (or sub-attributes) of new param object
    for var_dict in training_var.var_param:
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
    for s_dict in training_var.setup_func:
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


#unravel arrays and construct single input vector for name, min, max
parameters = [ full_name.split('.')[-1] for full_name in training_var.get_list('name') ]

min_vals = np.array( training_var.get_list('min_val') )
max_vals = np.array( training_var.get_list('max_val') )

#to load previous emulator, use:
#gp = gp_emulator.GaussianProcess( emulator_file=emulate_fname )

x = gp_emulator.create_emulator_validation(vector_scope, parameters, min_vals, max_vals,
                                           n_train, n_validate, do_gradient=True,
                                           n_tries=15 )

gp = x[0]

gp.save_emulator( emulate_fname )

#testing loop
for i in range(5):
    n_in = min_vals.size
    span = max_vals - min_vals
    test_input = span*np.random.random(n_in) + min_vals
    p_out = gp.predict( test_input.reshape((1,-1)), do_deriv=True, do_unc=True )
    guess = p_out[0]
    actual = vector_scope( [test_input] )
    print( '\ntest input = {:}'.format(test_input) )
    print( ' guess = {:}'.format(guess) )
    print( 'target = {:}'.format(actual) )
    print( p_out[1] ) #uncertainty
    print( p_out[2] ) #gradient
