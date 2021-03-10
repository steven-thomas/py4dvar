#!/usr/bin/env python

###############################################################################
# Script run_rtmf.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the RTMf module.
#
# Usage: e.g.,
#   from run_rtmf.py import *
#   runRTMf(param, leafopt, gap, rad, profiles)
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


def runRTMf(param, leafopt, gap, rad, profiles):
    """
    Run RTMf module.
    """

    from pyscope.rtmf.rtmf import RTMf

    r = RTMf(param, leafopt, gap, rad, profiles)

    # Compute geometric quantities used for fluorescence
    r.computeGeometric()

    # Compute fluorescence in observation direction
    r.computeFluorescence()

    # Create data structure for output
    r.createOutputStructures()

    # # Write module output to file
    # r.writeOutput(param)

    return r.rad, r.profiles


# EOF run_rtmf.py
