#!/usr/bin/env python

# Imports
import numpy as np
import gp_emulator

import context
import emulate_preprocess.p4d_scope_func as scope
import fourdvar.params.scope_em_file_defn as em_file_defn
from fourdvar.util.emulate_input_struct import EmulationInput

input_fname = em_file_defn.em_input_struct_fname[0]
emulate_fname = em_file_defn.emulation_fname[0]

#n_train = 500
#n_validate = 500
n_train = 10
n_validate = 10

scope.set_input( input_fname )
training_var = EmulationInput.load( input_fname )

#unravel arrays and construct single input vector for name, min, max
parameters = [ full_name.split('.')[-1] for full_name in training_var.get_list('name') ]

min_vals = np.array( training_var.get_list('min_val') )
max_vals = np.array( training_var.get_list('max_val') )

#to load previous emulator, use:
#gp = gp_emulator.GaussianProcess( emulator_file=emulate_fname )

x = gp_emulator.create_emulator_validation(scope.vector_scope, parameters, min_vals, max_vals,
                                           n_train, n_validate, do_gradient=True,
                                           n_tries=15 )

gp = x[0]

gp.save_emulator( emulate_fname )

#testing loop
ntest = 5
in_list = []
guess = []
actual = []
unc = []
grad = []
for i in range(ntest):
    n_in = min_vals.size
    span = max_vals - min_vals
    test_input = span*np.random.random(n_in) + min_vals
    in_list.append( test_input )
    p_out = gp.predict( test_input.reshape((1,-1)), do_deriv=True, do_unc=True )
    guess.append( p_out[0][0] )
    actual.append( scope.vector_scope( [test_input] ) )
    unc.append( p_out[1] )
    grad.append( p_out[2] )

for i in range(ntest):
    print( '\ntest input = {:}'.format(in_list[i]) )
    print( ' guess = {:}'.format(guess[i]) )
    print( 'target = {:}'.format(actual[i]) )
    print( 'unc = {:}'.format(unc[i]) ) #uncertainty
    print( 'grad = {:}'.format(p_out[2]) ) #gradient

print( 'std. of actual output: {:}'.format( np.array(actual).std() ) )
print( 'abs. err. = {:}'.format( abs(np.array(actual)-np.array(guess)) ) )
