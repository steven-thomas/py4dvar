
import numpy as np

import context
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import em_input_struct_fname

x = EmulationInput()

#x.add_var( 'canopy.LIDFa', -0.40, -0.30, None, True )
x.add_var( 'canopy.kV', 0.4, 0.9, None, True )
x.add_var( 'leafbio.Cab', 60, 100, None, True )
x.add_var( 'leafbio.Cca', 10, 30, None, True )
x.add_var( 'leafbio.Vcmo', 20, 40, None, True )
#x.add_var( 'leafbio.fqe', .001, .02, None, True )
x.add_var( 'leafbio.fqe', np.array([0.0005,0.005]), np.array([0.004,0.02]), (2,), True )
#x.add_var( 'leafbio.stressfactor', 0, 1, None, True )

#x.add_var( 'angles.psi', 0, 180, None, False )
x.add_var( 'angles.tto', 0, 60, None, False )
x.add_var( 'angles.tts', 0, 60, None, False )
#x.add_var( 'atmo.Ta', , , None, False )
x.add_var( 'canopy.LAI', 2, 4, None, False )
x.add_var( 'canopy.hc', 1, 3, None, False )
x.add_var( 'leafbio.Cdm', 0.005, 0.02, None, False )
#x.add_var( 'meteo.Rin', 700, 900, None, False )
#x.add_var( 'meteo.Rli', 250, 350, None, False )
#x.add_var( 'meteo.Ta', 10, 30, None, False )
#x.add_var( 'meteo.ea', 10, 20, None, False )
#x.add_var( 'meteo.p', 950, 1000, None, False )
#x.add_var( 'meteo.u', 1, 3, None, False )
#x.add_var( 'xyt.LAT', 0, 80, None, False )
#x.add_var( 'xyt.LON', 0, 180, None, False )

#x.add_set( 'atmo.Ta', 'sum', ['meteo.Ta'] )

x.save( em_input_struct_fname[0] )
