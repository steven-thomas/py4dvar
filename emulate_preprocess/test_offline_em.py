
import numpy as np
import gp_emulator

import context
import emulate_preprocess.p4d_scope_func as scope
import emulate_preprocess.training_defn as training_defn
import fourdvar.params.scope_em_file_defn as em_file_defn
from fourdvar.util.emulate_input_struct import EmulationInput

input_fname = em_file_defn.em_input_struct_fname
emulate_fname = em_file_defn.emulate_fname_list[ training_defn.em_training_index ]

scope.set_input( input_fname )
test_var = EmulationInput.load( input_fname )

parameters = [ full_name.split('.')[-1] for full_name in test_var.get_list('name') ]
min_vals = np.array( test_var.get_list('min_val') )
max_vals = np.array( test_var.get_list('max_val') )
avg_vals = 0.5*(min_vals+max_vals)
vec_size = max_vals - min_vals

gp_em = gp_emulator.GaussianProcess( emulator_file=emulate_fname )


#testing loop
ntest = 5
in_list = []
guess = []
actual = []
unc = []
grad = []
for i in range(ntest):
    test_input = np.random.normal( avg_vals, .2*vec_size )
    test_input = np.clip( test_input, min_vals, max_vals )
    in_list.append( test_input )
    p_out = gp_em.predict( test_input.reshape((1,-1)), do_deriv=True, do_unc=True )
    guess.append( p_out[0][0] )
    actual.append( scope.vector_scope( [test_input] ) )
    unc.append( p_out[1] )
    grad.append( p_out[2] )

np.set_printoptions( precision=4 )
for i in range(ntest):
    print( '\ntest input = {:}'.format(in_list[i]) )
    print( ' guess = {:}'.format(guess[i]) )
    print( 'target = {:}'.format(actual[i]) )
    print( 'unc = {:}'.format(unc[i]) ) #uncertainty
    print( 'grad = {:}'.format(grad[i]) ) #gradient

print( 'std. of actual output: {:}'.format( np.array(actual).std() ) )
print( 'abs. err. = {:}'.format( abs(np.array(actual)-np.array(guess)) ) )
