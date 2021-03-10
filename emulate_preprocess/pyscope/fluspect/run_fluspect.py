#!/usr/bin/env python

###############################################################################
# Script run_fluspect.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the Fluspect module.
#
# Usage: e.g.,
#   from run_fluspect.py import *
#   runFluspect(param)
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


def runFluspect(param):
    """
    Run Fluspect module.
    """

    from pyscope.fluspect.fluspect import Fluspect

    f = Fluspect(param)

    # Define wavelength vectors
    f.setWavelength()

    # Compute LRT
    f.getLRT_original()     # SCOPE original algorithm
    #f.getLRT()             # Using Christian's modifications

    # # Write module output to file
    # f.writeOutput(param)

    return f.leafopt


# EOF run_fluspect.py
