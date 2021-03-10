#!/usr/bin/env python

###############################################################################
# Script run_ebal.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the Ebal module.
#
# Usage: e.g.,
#   from run_ebal.py import *
#   runEbal(param, leafopt, gap, rad)
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


def runEbal(param, leafopt, gap, rad, profiles):
    """
    Run Ebal module.
    """

    from pyscope.ebal.ebal import Ebal

    # If calc_ebal: compute energy balance

    e = Ebal(param, leafopt, gap, rad, profiles)

    # Energy balance and radiative transfer loop
    e.loopEnergyBalance()

    # Calculate output per layer
    e.calculateLayers()

    # Calculate spectrally integrated quantities, sums, and averages
    e.calculateTotals()

    # Create data structure for output
    e.createOutputStructures()

    # # Write module output to file
    # e.writeOutput(param)

    return e.fluxes, e.rad, e.profiles, e.thermal, e.biochem_out


# EOF run_ebal.py
