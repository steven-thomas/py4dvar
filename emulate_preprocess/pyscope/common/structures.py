#!/usr/bin/env python

###############################################################################
# Script structures.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collection of defs for structure creation.
#
# Note: corresponding SCOPE functions:
#   assignvarnames.m
#   initialize_output_structures.m
#   select_input.m
#
# Usage: call defs from other python code.
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


class emptyStruct():
    """
    Creates empty structure that can be used like a Matlab structure.
    """

    pass


# EOF structures.py