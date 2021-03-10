#!/usr/bin/env python

###############################################################################
# Script run_rtmo.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the RTMo module.
#
# Usage: e.g.,
#   from run_rtmo.py import *
#   runRTMo(param, leafopt)
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


def runRTMo(param, leafopt):
    """
    Run RTMo module.
    """

    from pyscope.rtmo.rtmo import RTMo

    r = RTMo(param)

    # Get leafopt output from Fluspect and extend arrays
    r.getLeafopt(param, leafopt)

    # Compute geometric quantities used for fluxes
    r.computeGeometric()

    # Compute upward and downward fluxes
    r.computeUpDownFluxes()

    # Compute outgoing fluxes and spectrum
    r.computeOutgoingFluxes()

    # Compute net fluxes and incoming fluxes
    r.computeNetFluxes(param)

    # Create data structure for output
    r.createOutputStructures()

    # # Write module output to file
    # r.writeOutput(param)

    return r.leafopt, r.gap, r.rad, r.profiles


# EOF run_rtmo.py
