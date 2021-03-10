###############################################################################
# Script default_values.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: structure of parameter values used in the simulation
# Note: this script corresponds to inputdata.txt in SCOPE, and also replaces
# the function select_input.m and assignvarnames.m.
#
# Usage: e.g.,
#   from config.default_values import input_leafbio
#   leafbio = input_leafbio()
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

# Class to define empty structure
from pyscope.common.structures  import emptyStruct


def default_angles():
    """
    Define angles input parameters.
    """

    # Initialize structure
    angles = emptyStruct()

    # Angles
    angles.tts          = 85 #30        # [deg] Solar zenith angle
    angles.tto          = 0         # [deg] Observation zenith angle
    angles.psi          = 90        # [deg] Azimuthal difference between solar
                                    # and observation angle
    return angles


def default_atmo():
    """
    Define atmosphere input parameters.
    """

    # Initialize structure
    atmo = emptyStruct()

    # Data file
    atmo.atmofile = './data/working/input/radiationdata/FLEX-S3_std.atm'

    return atmo


def default_canopy():
    """
    Define canopy input parameters.
    """

    # Initialize structure
    canopy = emptyStruct()

    # Canopy
    canopy.LAI          = 3         # [m2 m-2] Leaf area index
    canopy.hc           = 2         # [m] Vegetation height
    canopy.LIDFa        = -0.35     # Leaf inclination
    canopy.LIDFb        = -0.15     # Variation in leaf inclination
    canopy.leafwidth    = 0.1       # [m] Leaf width
    canopy.rb           = 10        # [s m-1] Leaf boundary resistance
    canopy.Cd           = 0.3       # Leaf drag coefficient
    canopy.CR           = 0.35      # Verhoef et al. (1997) Drag coefficient
                                    # for isolated tree
    canopy.CD1          = 20.6      # Verhoef et al. (1997) Fitting parameter
    canopy.Psicor       = 0.2       # Verhoef et al. (1997) Roughness layer
                                    # correction
    canopy.rwc          = 0         # [s m-1] Within canopy layer resistance

    canopy.kV           = 0.6396    # Extinction coefficient for Vcmax in the
                                    # vertical (maximum at the top). 0 for
                                    # uniform Vcmax
    canopy.nlayers      = 60
    canopy.nlincl       = 13
    canopy.nlazi        = 36

    # Never change the angles unless 'ladgen' is also adapted
    canopy.litab_min1   = 5
    canopy.litab_max1   = 76
    canopy.litab_int1   = 10
    canopy.litab_min2   = 81
    canopy.litab_max2   = 90
    canopy.litab_int2   = 2

    canopy.lazitab_min  = 5
    canopy.lazitab_max  = 356
    canopy.lazitab_int  = 10

    return canopy


def default_directional():
    """
    Define directional input parameters.
    """

    # Initialize structure
    directional = emptyStruct()

    # File with observation angles
    directional.anglesfile = './data/working/input/directional/brdf_angles2.dat'

    return directional


def default_leafbio():
    """
    Define leafbio input parameters.
    """

    # Initialize structure
    leafbio = emptyStruct()

    # PROSPECT
    leafbio.Cab           = 80      # [ug cm-2] Chlorophyll AB content
    leafbio.Cca           = 20      # [ug cm-2] Carotenoid content, usually
                                    # 25% of Chlorophyll
    leafbio.Cdm           = 0.012   # [g cm-2] Dry matter content
    leafbio.Cw            = 0.009   # [cm] Leaf water equivalent layer
    leafbio.Cs            = 0       # [fraction] Scenecent material fraction
    leafbio.N             = 1.4     # [] Leaf thickness parameters

    # Leaf_Biochemical
    leafbio.Vcmo          = 30      # [umol m-2 s-1] maximum carboxylation
                                    # capacity (at optimum temperature)
    leafbio.m             = 8       # Ball-Berry stomatal conductance parameter
    leafbio.Type          = 0       # Photochemical pathway: 0=C3, 1=C4
    leafbio.Tparam        = [0.2, 0.3, 281, 308, 328]  #See PFT.xls. These are
                                    # five parameters specifying the
                                    # temperature response.

    # Fluorescence
    leafbio.fqe           = 0.01    # Fluorescence quantum yield efficiency at
                                    # photosystem level

    leafbio.Rdparam       = 0.015   # Respiration Rdparam*Vcmcax
    leafbio.rho_thermal   = 0.01    # Broadband thermal reflectance
    leafbio.tau_thermal   = 0.01    # Broadband thermal transmittance

    # Leaf_Biochemical (magnani model)
    leafbio.Tyear         = 15      # [C] mean annual temperature
    leafbio.beta          = 0.507   # [] "fraction of photons partitioned to
                                    # PSII (0.507 for C3, 0.4 for C4; Yin et
                                    # al. 2006; Yin and Struik 2012)"
    leafbio.kNPQs         = 0       # [s-1] Rate constant of sustained thermal
                                    # dissipation (Porcar-Castell 2011)
    leafbio.qLs           = 1       # [] Fraction of functional reaction
                                    # centres (Porcar-Castell 2011)
    leafbio.stressfactor  = 1       # "optional input: stress factor to reduce
                                    # Vcmax (for example soil moisture, leaf
                                    # age). Default value = 1."

    return leafbio


def default_meteo():
    """
    Define meteo input parameters.
    """

    # Initialize structure
    meteo = emptyStruct()

    # Meteo (values in data files, in the time series option, can overrule
    # these values)
    meteo.zo    = 0.246             # [m] Roughness length for momentum of the
                                    # canopy
    meteo.d     = 1.34              # [m] Displacement height
    meteo.z     = 10                # [m] Measurement height of meteorological
                                    # data
    meteo.Rin   = 800               # [W m-2] Broadband incoming shortwave
                                    # radiation (0.4-2.5 um)
    meteo.Ta    = 20                # [C] Air temperature
    meteo.Rli   = 300               # [W m-2] Broadband incoming
                                    # longwave radiation (2.5-50 um)
    meteo.p     = 970               # [hPa] Air pressure
    meteo.ea    = 15                # [hPa] Atmospheric vapour pressure
    meteo.u     = 2                 # [ms-1] Wind speed at height z_
    meteo.Ca    = 380               # [ppm] Atmospheric CO2 concentration
    meteo.Oa    = 209               # [per mille] Atmospheric O2 concentration

    return meteo


def default_numiter():
    """
    Define numerical iteration and convergence parameters.
    """

    # Initialize structure
    numiter = emptyStruct()

    # Numerical parameters
    numiter.maxit   = 300           # Maximum number of iterations
    numiter.maxEBer = 1             # [W m-2] Maximum accepted error in energy
                                    # balance
    numiter.Wc      = 1             # Weight coefficient for iterative
                                    # calculation of Tc

    return numiter


def default_optipar():
    """
    Define optipar file name.
    """

    optipar = emptyStruct()

    # File name to optipar data
    optipar.optifile = \
    './data/working/input/fluspect_parameters/Optipar_fluspect_2014.txt'

    return optipar


def default_paths():
    """
    Define input and output paths.
    """

    paths = emptyStruct()

    # Input file
    paths.user_file   = "None" #"user_input.cfg"

    # Input directory
    paths.input       = "./data/working/input/"

    # Output directory
    paths.output_base = "output"

    # Input parameter file name
    paths.logname     = "input_parameters.txt"

    return paths


def default_soil():
    """
    Define soil input parameters.
    """

    # Initialize structure
    soil = emptyStruct()

    soil.spectrum       = 1         # Spectrum number (column in the database
                                    # soil_file)
    soil.rss            = 500       # [s m-1] Soil resistance for evaporation
                                    # from the pore space
    soil.rs_thermal     = 0.06      # Broadband soil reflectance in the thermal
                                    # range (1-emissivity)
    soil.cs             = 1.18E+03  # [J m-2 K-1] Volumetric heat capacity of
                                    # the soil
    soil.rhos           = 1.80E+03  # [kg m-3] Specific mass of the soil
    soil.CSSOIL         = 0.01      # Verhoef et al. (1997) Drag coefficient
                                    # for soil
    soil.lambdas        = 1.55      # [J m-1 K-1] Heat conductivity of the soil
    soil.rbs            = 10        # [s m-1] Soil boundary layer resistance
    soil.SMC            = 0.25      # volumetric soil moisture content in the
                                    # root zone

    # Not originally in the Matlab structure: soil reflectivity file name
    soil.soil_file      = './data/working/input/soil_spectrum/soilnew.txt'

    return soil


def default_spectral():
    """
    Define spectral regions.
    """

    # Initialize structure
    spectral = emptyStruct()

    # Spectral region 1: used for wlP, wlO, wlS
    spectral.reg1_min = 400
    spectral.reg1_max = 2401
    spectral.reg1_int = 1

    # Spectral region 2: used for wlT, wlS
    spectral.reg2_min = 2500
    spectral.reg2_max = 15001
    spectral.reg2_int = 100

    # Spectral region 3: used for wlT, wlS
    spectral.reg3_min = 16000
    spectral.reg3_max = 50001
    spectral.reg3_int = 1000

    # Other spectral (sub)regions

    # Excitation in E-F matrix
    spectral.wlE_min = 400
    spectral.wlE_max = 751
    spectral.wlE_int = 1

    # Chlorophyll
    spectral.wlF_min = 640
    spectral.wlF_max = 851
    spectral.wlF_int = 1

    # Additional parameters
    spectral.IwlF_min = 639
    spectral.IwlF_max = 850

    return spectral


def default_xyt():
    """
    Define xyt input parameters.
    """

    # Initialize structure
    xyt = emptyStruct()

    # Timeseries (this option is only for time series)
    xyt.startDOY        = 169       # Julian day (decimal) of start of
                                    # simulations
    xyt.endDOY          = 170       # Julian day (decimal) of end of
                                    # simulations
    xyt.LAT             = 52.25     # [decimal deg] Latitude
    xyt.LON             = 5.69      # [decimal deg] Longitude
    xyt.timezn          = 1         # [hours] East of Greenwich

    # Files for timeseries
    xyt.Dataset_dir     = "for_verification"
    xyt.t_file          = "t_.dat"
    xyt.year_file       = "year_.dat"
    xyt.Rin_file        = "Rin_.dat"
    xyt.Rli_file        = "Rli_.dat"
    xyt.p_file          = "p_.dat"
    xyt.Ta_file         = "Ta_.dat"
    xyt.ea_file         = "ea_.dat"
    xyt.u_file          = "u_.dat"

    # Optional (leave as "None" for constant values)
    xyt.CO2_file        = "None"
    xyt.z_file          = "None"
    xyt.tts_file        = "None"

    # Optional two column tables (first column DOY second column value)
    xyt.LAI_file        = "None"
    xyt.hc_file         = "None"
    xyt.SMC_file        = "None"
    xyt.Vcmax_file      = "None"
    xyt.Cab_file        = "None"

    return xyt


# EOF default_values.py
