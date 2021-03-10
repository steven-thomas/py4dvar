#!/usr/bin/env python

###############################################################################
# Script run_rtmt_sb.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the RTMt_sb module.
#
# Usage: e.g.,
#   from run_rtmt_sb.py import *
#   runRTMt_sb(param, leafopt)
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


def runRTMt_sb(param, leafopt, rad, gap, T_struct, obsdir):
    """
    Run RTMt_sb module.
    """

    from pyscope.rtmt.rtmt_sb     import RTMt_sb

    r = RTMt_sb(param, leafopt, rad, gap, T_struct, obsdir)

    # Compute geometric quantities used for fluxes
    r.computeGeometric()

    # Compute upward and downward fluxes
    r.computeUpDownFluxes()

    # Compute net fluxes
    r.computeNetFluxes()

    # Create data structure for output
    r.createOutputStructures()

    # Write module output to file
    # Not wanted here, given that this feeds into the ebal module within a
    # while loop?
    # r.writeOutput(param)

    return r.rad


# EOF run_rtmt_sb.py
