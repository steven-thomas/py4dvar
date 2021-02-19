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

emulator_save_name = 'emulated_scope.npz'

training_var = emptyStruct()
training_var.name_list = []
training_var.min_list = []
training_var.max_list = []
training_var.shape_list = []
training_var.size_list = []


def add_var( t, name, min_val, max_val, shape ):
    t.name_list.append(name)
    t.min_list.append(min_val)
    t.max_list.append(max_val)
    t.shape_list.append(shape)
    if shape == None:
        t.size_list.append(1)
    else:
        t.size_list.append( np.prod(shape) )
    return None

#add/change inputs to train here (full name in param obj, min val, max val, shape(None==scalar))
add_var( training_var, 'angles.psi', 88., 90., None )
add_var( training_var, 'angles.tto', 0., 2., None )
add_var( training_var, 'angles.tts', 29., 31., None )
add_var( training_var, 'leafbio.stressfactor', 0.5, 2., None )

#spectral weighting term for output flourescence
spec_weight = np.zeros((211,))
spec_weight[100] = 1.

n_train = 500
n_validate = 500

# Initialize simulation with baseline inputs
param_fname = 'base_config.cfg'
config = run_config.setup_config_input( param_fname )
input_control = InputController( config.param )
input_control.setup_new_run()
param = run_config.process_config( config )

def vector_scope( x ):
    input_list = list(x[0])
    new_run = copy.copy( param )

    #update attributes (or sub-attributes) of new param object
    for var_i,full_name in enumerate( training_var.name_list ):
        nlist = full_name.split('.')
        nlen = len( nlist )
        obj = new_run
        for ni, name in enumerate( nlist ):
            if ni == nlen-1:
                #name is the leaf attribute.
                vlen = training_var.size_list[var_i]
                vshape = training_var.shape_list[var_i]
                val = input_list[:vlen]
                input_list = input_list[vlen:]
                if vshape is None:
                    #set scalar
                    setattr( obj, name, val[0] )
                else:
                    setattr( obj, name, np.reshape(val,vshape) )
            else:
                #name is another object.
                obj = getattr( obj, name )
                
    output_control = run_scope( new_run )
    out_scale = (output_control.rad.LoF_ * spec_weight).sum()
    return out_scale


#unravel arrays and construct single input vector for name, min, max
short_name = [ n.split('.')[-1] for n in training_var.name_list ]
parameters = []
for sn, size in zip( short_name, training_var.size_list ):
    parameters.extend( [sn]*size )

min_vals = []
for val,shape in zip( training_var.min_list, training_var.shape_list ):
    if shape is None:
        min_vals.append(val)
    else:
        min_vals.extend( list(val.flatten()) )
min_vals = np.array( min_vals )

max_vals = []
for val,shape in zip( training_var.max_list, training_var.shape_list ):
    if shape is None:
        max_vals.append(val)
    else:
        max_vals.extend( list(val.flatten()) )
max_vals = np.array( max_vals )

#to load previous emulator, use:
#gp = gp_emulator.GaussianProcess( emulator_file=emulator_save_name )

x = gp_emulator.create_emulator_validation(vector_scope, parameters, min_vals, max_vals,
                                           n_train, n_validate, do_gradient=True,
                                           n_tries=15 )

gp = x[0]

gp.save_emulator( emulator_save_name )

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
    print( p_out[1] )
    print( p_out[2] )
