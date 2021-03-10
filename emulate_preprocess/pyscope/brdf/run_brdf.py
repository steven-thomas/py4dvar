#!/usr/bin/env python

###############################################################################
# Script run_brdf.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the BRDF module.
#
# Usage: e.g.,
#   from run_brdf.py import *
#   runBRDF(param, leafopt, gap, rad, profiles)
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


def runBRDF(param, leafopt, gap, rad, thermal, profiles):
    """
    Run BRDF module.
    """

    from pyscope.brdf.brdf import BRDF

    b = BRDF(param, leafopt, gap, rad, thermal, profiles)

    # Calculate BRDF and directional temperature for different angles
    b.computeBRDF()

    # Write module output to file
    b.writeOutput(param)

    return b.directional


# EOF run_brdf.py
