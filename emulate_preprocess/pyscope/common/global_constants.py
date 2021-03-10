###############################################################################
# Script global_constants.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: lists global constants
# Note: this script corresponds to define_constants.m in SCOPE.
#
# Usage:
#   import global_constants as const
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


# Imports
from math import *

# List of global constants
A         = 6.02214E23   # [mol-1]       Constant of Avogadro
h         = 6.6262E-34   # [J s]         Planck's constant
c         = 299792458.0  # [m s-1]       Speed of light
cp        = 1004.0       # [J kg-1 K-1]  Specific heat of dry air
R         = 8.314        # [J mol-1K-1]  Molar gas constant
rhoa      = 1.2047       # [kg m-3]      Specific mass of air
g         = 9.81         # [m s-2]       Gravity acceleration
kappa     = 0.4          # []            Von Karman constant
MH2O      = 18.0         # [g mol-1]     Molecular mass of water
Mair      = 28.96        # [g mol-1]     Molecular mass of dry air
MCO2      = 44.0         # [g mol-1]     Molecular mass of carbon dioxide
sigmaSB   = 5.67E-8      # [W m-2 K-4]   Stefan Boltzman constant
deg2rad   = pi / 180.0   # [rad]         Conversion from deg to rad
C2K       = 273.15       # [K]           Melting point of water

# EOF global_constants.py