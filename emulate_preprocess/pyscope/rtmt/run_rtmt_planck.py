#!/usr/bin/env python

###############################################################################
# Script run_rtmt_planck.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the RTMt_planck module.
#
# Usage: e.g.,
#   from run_rtmt_planck.py import *
#   runRTMt_planck(param, leafopt)
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


def runRTMt_planck(param, leafopt, gap, rad, thermal):
    """
    Run RTMt_planck module.
    """

    from pyscope.rtmt.rtmt_planck     import RTMt_planck

    r = RTMt_planck(param, leafopt, gap, rad, thermal)

    # Compute geometric quantities used for fluxes
    r.computeGeometric()

    # Compute upward and downward fluxes
    r.computeUpDownFluxes()

    # Create data structure for output
    r.createOutputStructures()

    # Write module output to file
    r.writeOutput(param)

    return r.rad


# EOF run_rtmt_planck.py
