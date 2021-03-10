#!/usr/bin/env python

###############################################################################
# Script run_config.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: Run the config module.
#
# Usage: e.g.,
#   from run_config.py import *
#   runConfig(sys_argv)
#
# Input: system arguments passed on in sys_argv dictionary.
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

def setup_config_input( fname=None ):
    """
    Run config module, which collects input and constructs the parameter
    dictionary.
    """

    from pyscope.config.config import Config

    c = Config()

    # Initialize pySCOPE simulation
    c.initRun( fname )

    # Parse default run options and parameter values
    c.parseDefaults()

    # Parse input file provided by user
    c.parseUserInput()

    # Overwrite defaults with user provided input parameters
    c.mergeInput()

    return c

def process_config( c ):

    # Process time series if required
    c.processTime()

    # Compute some additional parameters that are inserted in global struct
    c.computeParam()

    ## Create output files
    #c.createOutput()

    ## Write input parameters to file
    #c.writeLog()

    return c.param

def runConfig(sys_argv):
    """
    Run config module, which collects input and constructs the parameter
    dictionary.
    """

    from config import Config

    c = Config()

    # Initialize pySCOPE simulation
    c.initRun(sys_argv)

    # Parse default run options and parameter values
    c.parseDefaults()

    # Parse input file provided by user
    c.parseUserInput()

    # Overwrite defaults with user provided input parameters
    c.mergeInput()

    # Process time series if required
    c.processTime()

    # Compute some additional parameters that are inserted in global struct
    c.computeParam()

    # Create output files
    c.createOutput()

    # Write input parameters to file
    c.writeLog()

    return c.param


# EOF run_config.py
