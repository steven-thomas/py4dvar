
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

#----- Create test input ------------------------------------
x = EmulationInput()

#(1) LIDFa = leaf inclination (unitless), -0.35
#x.add_var( 'canopy.LIDFa', -0.40, -0.30, None, True )
#No change in actual output.

#(1) kV = extinction coefficient for Vcmax in the vertical (maximum at the top). 0 for uniform Vcmax (units unknown), 0.6396
#x.add_var( 'canopy.kV', 0.6, 0.66, None, True )
#x.add_var( 'canopy.kV', 0.4, 0.9, None, True )

#(1) Cab = Chlorophyll AB content (ug cm-2), 80
#x.add_var( 'leafbio.Cab', 60, 100, None, True )
# good.

#(1) Cca = Carotenoid content (ug cm-2), 20
#x.add_var( 'leafbio.Cca', 10, 30, None, True )
# good.

#?(1) Cw = leaf water equivalent layer (cm), 0.009
#x.add_var( 'leafbio.Cw', .005, .015, None, True )
# good.

#?(5) Tparam = five parameters specifying the temperature response (deg.K), [0.2, 0.3, 281, 308, 328]
#x.add_var( 'leafbio.Tparam',[0.1, 0.2, 271, 298, 318], [0.3, 0.4, 291, 318, 328], None, True )
# multi-element input currently broken.

#(1) Vcmo = maximum carboxylation capacity (at optimum temperature) (umol m-2 s-1), 30
#x.add_var( 'leafbio.Vcmo', 20, 40, None, True )
# good.

#(2) fqe = fluorescence quantum yield efficiency at photosystem level (unitless), 0.01
#actual values listed in code: [0.002 0.01 ]
x.add_var( 'leafbio.fqe', np.array([0.0005,0.005]), np.array([0.004,0.02]), (2,), True )
#broken, needs multiple.

#?(1) stressfactor = optional input: stress factor to reduce Vcmax (for example soil moisture, leaf age) (unitless), 1
#x.add_var( 'leafbio.stressfactor', 0, 1, None, True )
#No change in actual output.


#(1) psi = solar/obs azimuth diff. (deg.), 90
#x.add_var( 'angles.psi', 0, 180, None, False )
#No change in actual output.

#(1) tto = obs. zenith angle (deg.), 0
#x.add_var( 'angles.tto', 0, 60, None, False )
# good.

#(1) tts = solar zenith angle (deg.), 30
#x.add_var( 'angles.tts', 0, 60, None, False )
# good.

#(1) CD1 = Verhoef et al. (1997) fitting parameter (units unknown), 20.6
#x.add_var( 'canopy.CD1', 15, 25, None, False )
#No change in actual output.

#(1) LAI = Leaf area index (m2 m-2), 3
#x.add_var( 'canopy.LAI', 2, 4, None, False )
# good.

#?(1) hc = veg. height (m), 2
#x.add_var( 'canopy.hc', 1, 3, None, False )
# good.

#(1) Cdm = Dry matter content (g cm-2), 0.012
#x.add_var( 'leafbio.Cdm', 0.005, 0.02, None, False )
# good.

#?(1) rho_thermal = broadband thermal reflectance (unitless), 0.01
#x.add_var( 'leafbio.rho_thermal', 0.005, 0.02, None, False )
# almost no affect.

#?(1) tau_thermal = broadband thermal transmittance (unitless), 0.01
#x.add_var( 'leafbio.tau_thermal', 0.005, 0.02, None, False )
# almost no affect.

#(1) Rin = broadband incoming shortwave radiation (W m-2), 800
#x.add_var( 'meteo.Rin', 700, 900, None, False )
# bad guess, better training?

#(1) Rli = broadband incoming longwave radiation (W m-2), 300
#x.add_var( 'meteo.Rli', 250, 350, None, False )
# bad guess, better training?

#?(1) Ta = air temperature (deg.C), 20
#x.add_var( 'meteo.Ta', 10, 30, None, False )
# little impact, good.

#(1) ea = atmospheric vapour pressure (hPa), 15
#x.add_var( 'meteo.ea', 10, 20, None, False )
# good.

#(1) p = air pressure (hPa), 970
#x.add_var( 'meteo.p', 950, 1000, None, False )
# bad guess, better training?

#(1) u = wind speed at height z (m s-1), 2
#x.add_var( 'meteo.u', 1, 3, None, False )
# good.

#(1) LAT = Latitude (deg.), 52.25
#x.add_var( 'xyt.LAT', 0, 80, None, False )
#No change in actual output.

#(1) LON = Longitude (deg.), 5.69
#x.add_var( 'xyt.LON', 0, 180, None, False )
#No change in actual output.


#set function : when input is dependant on other inputs.
#x.add_set( 'atmo.Ta', 'sum', ['meteo.Ta'] )


#unknown is should include.
#?(1) Rdparam = <Respiration = Rdparam * Vcmcax> (unitless), 0.015
#x.add_var( 'leafbio.Rdparam', 0.01, 0.02, None, False )
#little impact, good.

#----- Create Emulated SCOPE (tiny-test) --------------------
training_var = x

#spectral weighting term for output flourescence
spec_weight = np.zeros((211,))
spec_weight[122] = 1.

n_train = 5
n_validate = 5

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

#testing loop
ntest = 5
in_list = []
guess = np.zeros(ntest)
actual = np.zeros(ntest)
unc = np.zeros(ntest)
grad = []
for i in range(ntest):
    n_in = min_vals.size
    span = max_vals - min_vals
    test_input = span*np.random.random(n_in) + min_vals
    in_list.append( test_input )
    p_out = gp.predict( test_input.reshape((1,-1)), do_deriv=True, do_unc=True )
    guess[i] = p_out[0][0]
    actual[i] = vector_scope( [test_input] )
    unc[i] = p_out[1][0]
    grad.append( p_out[2] )

for i in range(ntest):
    print( '\ntest input = {:}'.format(in_list[i]) )
    print( ' guess = {:}'.format(guess[i]) )
    print( 'target = {:}'.format(actual[i]) )
    print( 'unc = {:}'.format(unc[i]) ) #uncertainty
    print( 'grad = {:}'.format(grad[i]) ) #gradient

print( '\nSTD = {:}'.format( actual.std() ) )
print( 'ACC = {:}'.format( (abs(actual-guess)).mean() ) )
print( 'UNC = {:}'.format( (abs(unc)).mean() ) )
