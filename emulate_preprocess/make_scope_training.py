#!/usr/bin/env python

# Imports
import numpy as np
import gp_emulator
import pickle

import context
import emulate_preprocess.p4d_scope_func as scope
import emulate_preprocess.training_defn as training_defn
import fourdvar.params.scope_em_file_defn as em_file_defn
from fourdvar.util.emulate_input_struct import EmulationInput

input_fname = em_file_defn.em_input_struct_fname

n_train = 500
n_validate = 500
#n_train = 10
#n_validate = 10

scope.set_input( input_fname )
training_var = EmulationInput.load( input_fname )

#unravel arrays and construct single input vector for name, min, max
parameters = [ full_name.split('.')[-1] for full_name in training_var.get_list('name') ]

min_vals = np.array( training_var.get_list('min_val') )
max_vals = np.array( training_var.get_list('max_val') )

#use create emulate function to choose input set, but don't save results.
x = gp_emulator.create_emulator_validation(scope.vector_scope, parameters, min_vals, max_vals,
                                           n_train, n_validate, do_gradient=True,
                                           n_tries=15 )

gp = x[0]

#archive input/output sets for later emulation training
with open( training_defn.train_input_raw_fname, 'wb' ) as f:
    pickle.dump( scope.vector_input_archive, f)
with open( training_defn.train_output_raw_fname, 'wb' ) as f:
    pickle.dump( scope.vector_output_archive, f)

print( '\nsaved {:} training sets\n'.format(len(scope.vector_output_archive)) )

#quick test, will probably return NaN output.
n_in = min_vals.size
span = max_vals - min_vals
test_input = span*np.random.random(n_in) + min_vals
p_out = gp.predict( test_input.reshape((1,-1)), do_deriv=True, do_unc=True )
guess = p_out[0][0]
actual = scope.vector_scope( [test_input] )
unc = p_out[1]
grad = p_out[2]

print( '\ntest input = {:}'.format(test_input) )
print( ' guess = {:}'.format(guess) )
print( 'target = {:}'.format(actual) )
print( 'unc = {:}'.format(unc) )
print( 'grad = {:}'.format(grad) )
