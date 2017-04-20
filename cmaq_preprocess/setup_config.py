
import os

import _get_root

#uses paths found in:
#fourdvar/params/cmaq_config.py
#fourdvar/params/template_defn.py
#ensure paths listed in above files are correct.

# if True have run_setup create new template files
create_templates = True
#if True have run_setup create a new prior file
create_prior = True

# -EXTRA CHECKS-

#if True require emission file STIME to match cmaq_config
match_emis_stime = True

#if True require emission file TSTEP to match cmaq_config
match_emis_tstep = True


# -PRIOR/PHYSICAL_DATA SETTINGS-

#filepath to save new prior file to
phys_path = os.path.realpath( './prior.ncf' )

# spcs used in PhysicalData. must be a subset of spcs in icon & emis
# possible values:
# 'icon' to use all spcs in initial conditions file
# 'emis' to use all spcs in emissions file
# list of strings for a custom subset eg: ['CO2','CH4','CO']
phys_spcs = 'emis'

# number of layers for PhysicalData inital conditions
# possible values: 'icon' to read layers from file, int to use custom value
phys_icon_lays = 'icon'

# number of layers for PhysicalData emissions
# possible values: 'emis' to read layers from file, int to use custom value
phys_emis_lays = 'emis'

# length of an emission timestep for PhysicalData
# possible values:
# 'emis' to use timestep from emissions file
# [ days, HoursMinutesSeconds ] for custom length eg: half-hour avg. = [0,3000]
phys_tstep = [1,0] #daily average of emissions


# -OUTPUT SETTINGS FOR CMAQ-

# number of layers of emission file to use.
# possible values: int OR 'all' to find value from file
emis_lays = 'all'

# number of layers to output from forward run.
# possible values:
# 'icon' to use all layers in inital conditions file
# 'emis' to use all layers in emissions file
# integer to use a custom number of layers
conc_out_lays = 'icon'

# set of spcs to output from forward run.
# possible values:
# 'icon' to use all layers in inital conditions file
# 'emis' to use all layers in emissions file
# list of strings for a custom subset eg: ['CO2','CH4','CO']
conc_spcs = 'emis'

# number of layers to input as forcing to adjoint run.
# possible values:
# 'conc' to use all layers in concentration file
# integer to use a custom number of layers
force_lays = 'conc'

# number of emission layers to output from adjoint run
# possible values:
# 'emis' to use all layers in emissions file
# 'conc' to use all layers in concentration file
# integer to use a custom number of layers
sense_emis_lays = 'emis'
