###############################################################################
# Script default_options.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: lists simulation options
# Note: this script corresponds to the options structure in SCOPE_mac_linux.m,
# which is read from setoptions.m.
#
# Usage:
#   import default_options as options
#
# Author:
# Laura Alisic Jewell <Laura.A.Jewell@jpl.nasa.gov>, Jet Propulsion Laboratory
#
# Copyright (c) 2015-2016, California Institute of Technology.
# ALL RIGHTS RESERVED. This work is supported in part by the W.M. Keck 
# Institute for Space Studies.
#
# Last modified: Jan 06, 2016 by Laura Alisic Jewell
###############################################################################


# From SCOPE_mac_linux.m:
Cca_function_of_Cab = 0

# Calculate the complete energy balance
calc_ebal           = 1

# Calculate vertical profiles of fluxes and temperatures
calc_vert_profiles  = 0

# Calculate chlorophyll fluorescence in observation direction
calc_fluor          = 1

# Calculate spectrum of thermal radiation with spectral emissivity instead of
# broadband
calc_planck         = 0

# Calculate BRDF and directional temperature for many angles specified in a
# file
calc_directional    = 0

# 0: provide emissivity values as input
# 1: use values from fluspect and soil at 2400 nm for the TIR range
rt_thermal          = 0

# 0: use the zo and d values provided in the inputdata
# 1: calculate zo and d from the LAI, canopy height, CD1, CR, CSSOIL
# (recommended if LAI changes in time series)
calc_zo             = 0

# 0: standard calculation of thermal inertia from soil characteristics
# 1: empiricaly calibrated formula (make function)
# 2: as constant fraction of soil net radiation
soil_heat_method    = 2

# 0: empirical, with sustained NPQ (fit to Flexas' data)
# 1: empirical, with sigmoid for Kn
# 2: Magnani 2012 model
Fluorescence_model  = 0

# 0: use resistance rss and rbs as provided in inputdata
# 1:  calculate rss from soil moisture content and correct rbs for LAI
# (calc_rssrbs.m)
calc_rss_rbs        = 0

# Correct Vcmax and rate constants for temperature in biochemical.m
apply_T_corr        = 1

# Verifiy the results (compare to saved 'standard' output) to test the code
verify              = 1

# Write header lines in output files
save_headers        = 1

# Create plots
makeplots           = 0

# 0: Individual runs. Specify one value for constant input, and an equal number
# (>1) of values for all input that varies between the runs
# 1: Time series (uses text files with meteo input as time series)
# 2: Lookup-Table (specify the values to be included; all possible combinations
# of inputs will be used)
simulation          = 0

# Log level
# 0: Default logging
# 1: Extensive logging, useful for debugging
log_level           = 0


# EOF default_options.py