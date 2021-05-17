
import numpy as np

import context
from fourdvar.util.emulate_input_struct import EmulationInput
from fourdvar.params.scope_em_file_defn import em_input_struct_fname

x = EmulationInput()

# V3 Reduces parameters to train over to stop emulator zero-ing out.

# [deg] Observation zenith angle
#x.add_var( 'angles.tto', 0, 60, None, False ) #TODO Set default to 45.
# [deg] Solar zenith angle
#x.add_var( 'angles.tts', 0, 60, None, False ) #TODO Set default to 0

# [m2 m-2] Leaf area index
#x.add_var( 'canopy.LAI', .1, 10., None, False ) #ORIGINAL ALEX VSN
x.add_var( 'canopy.LAI', .1, 7., None, False )
# Leaf inclination
x.add_var( 'canopy.LIDFa', -1, 1, None, False )
# Variation in leaf inclination
x.add_var( 'canopy.LIDFb', -1, 1, None, False )
# [m] Vegetation height
#x.add_var( 'canopy.hc', .1, 80, None, False ) #TODO set default to 5.
# [ug cm-2] Chlorophyll AB content
x.add_var( 'leafbio.Cab', 1, 100, None, True )
# [ug cm-2] Carotenoid content, usually 25% of Chlorophyll
#x.add_var( 'leafbio.Cca', 1, 30, None, True ) #TODO set to 25% Cab
# [umol m-2 s-1] maximum carboxylation capacity (at optimum temperature)
x.add_var( 'leafbio.Vcmo', 1, 250, None, True )

# [W m-2] Broadband incoming shortwave radiation (0.4-2.5 um)
#x.add_var( 'meteo.Rin', 1, 1300, None, False ) #ORIGINAL ALEX VSN
x.add_var( 'meteo.Rin', 1, 1000, None, False )
# [W m-2] Broadband incoming longwave radiation (2.5-50 um)
#x.add_var( 'meteo.Rli', 1, 350, None, False )
# [C] Air temperature
#x.add_var( 'meteo.Ta', -20, 50, None, False )
# [hPa] Atmospheric vapour pressure
#x.add_var( 'meteo.ea', 1, 40, None, False )
# [hPa] Air pressure
#x.add_var( 'meteo.p', 800, 1013, None, False )
# [ms-1] Wind speed at height z_
#x.add_var( 'meteo.u', 1, 20, None, False )
# [m] Measurement height of meteorological data
#x.add_var( 'meteo.z', 1, ??, None, False )

# volumetric soil moisture content in the root zone
#x.add_var( 'soil.SMC', .05, .7, None, False )

"""
# V2 Ranges modified to reduce extreme overheating edge cases.

# [deg] Observation zenith angle
x.add_var( 'angles.tto', 0, 60, None, False )
# [deg] Solar zenith angle
x.add_var( 'angles.tts', 0, 60, None, False )

# [m2 m-2] Leaf area index
#x.add_var( 'canopy.LAI', .1, 10., None, False ) #ORIGINAL ALEX VSN
x.add_var( 'canopy.LAI', .1, 7., None, False )
# Leaf inclination
x.add_var( 'canopy.LIDFa', -1, 1, None, False )
# Variation in leaf inclination
x.add_var( 'canopy.LIDFb', -1, 1, None, False )
# [m] Vegetation height
x.add_var( 'canopy.hc', .1, 80, None, False )
# [ug cm-2] Chlorophyll AB content
x.add_var( 'leafbio.Cab', 1, 100, None, True )
# [ug cm-2] Carotenoid content, usually 25% of Chlorophyll
x.add_var( 'leafbio.Cca', 1, 30, None, True )
# [g cm-2] Dry matter content
x.add_var( 'leafbio.Cdm', .0001, .05, None, False )
# [cm] Leaf water equivalent layer
x.add_var( 'leafbio.Cw', .001, .05, None, False )
# [fraction] Scenecent material fraction
x.add_var( 'leafbio.Cs', .0001, .3, None, False )
# [] Leaf thickness parameters
#x.add_var( 'leafbio.N', ??, ??, None, False )
# Respiration Rdparam*Vcmcax
#x.add_var( 'leafbio.Rdparam', ??, ??, None, False )
# [umol m-2 s-1] maximum carboxylation capacity (at optimum temperature)
x.add_var( 'leafbio.Vcmo', 1, 250, None, True )

# [W m-2] Broadband incoming shortwave radiation (0.4-2.5 um)
#x.add_var( 'meteo.Rin', 1, 1300, None, False ) #ORIGINAL ALEX VSN
x.add_var( 'meteo.Rin', 1, 1000, None, False ) #ORIGINAL ALEX VSN
# [W m-2] Broadband incoming longwave radiation (2.5-50 um)
x.add_var( 'meteo.Rli', 1, 350, None, False )
# [C] Air temperature
x.add_var( 'meteo.Ta', -20, 50, None, False )
# [hPa] Atmospheric vapour pressure
x.add_var( 'meteo.ea', 1, 40, None, False )
# [hPa] Air pressure
x.add_var( 'meteo.p', 800, 1013, None, False )
# [ms-1] Wind speed at height z_
x.add_var( 'meteo.u', 1, 20, None, False )
# [m] Measurement height of meteorological data
#x.add_var( 'meteo.z', 1, ??, None, False )

# volumetric soil moisture content in the root zone
x.add_var( 'soil.SMC', .05, .7, None, False )
"""
"""
# V1 Ranges provided by Alex.

x.add_var( 'angles.tto', 0, 60, None, False )
x.add_var( 'angles.tts', 0, 60, None, False )

x.add_var( 'canopy.LAI', .1, 10., None, False )
x.add_var( 'canopy.LIDFa', -1, 1, None, False )
x.add_var( 'canopy.LIDFb', -1, 1, None, False )
x.add_var( 'canopy.hc', .1, 80, None, False )
x.add_var( 'leafbio.Cab', 1, 100, None, True )
x.add_var( 'leafbio.Cca', 1, 30, None, True )
x.add_var( 'leafbio.Cdm', .0001, .05, None, False )
x.add_var( 'leafbio.Cw', .001, .05, None, False )
x.add_var( 'leafbio.Cs', .0001, .3, None, False )
#x.add_var( 'leafbio.N', ??, ??, None, False )
#x.add_var( 'leafbio.Rdparam', ??, ??, None, False )
x.add_var( 'leafbio.Vcmo', 1, 250, None, True )

x.add_var( 'meteo.Rin', 1, 1300, None, False )
x.add_var( 'meteo.Rli', 1, 350, None, False )
x.add_var( 'meteo.Ta', -20, 50, None, False )
x.add_var( 'meteo.ea', 1, 40, None, False )
x.add_var( 'meteo.p', 800, 1013, None, False )
x.add_var( 'meteo.u', 1, 20, None, False )
#x.add_var( 'meteo.z', 1, ??, None, False )

x.add_var( 'soil.SMC', .05, .7, None, False )
"""

x.save( em_input_struct_fname )
