#!/usr/bin/env python

###############################################################################
# Script compute_input.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collection of defs for computation of inputs to modules.
#
# Usage: e.g.,
#   import common.compute_input as compute_input
#   spectral = compute_input.spectral()
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

import  numpy               as np
from    math                import *

# Class to define empty structure
from    pyscope.common.structures          import emptyStruct

# Global constants
import  pyscope.common.global_constants    as const

# Get library of various functions
import  pyscope.common.library_physics     as physics


def define_spectral(param):
    """
    Process spectral regions.
    """

    # 3 spectral regions
    param.spectral.reg1 = np.arange(param.spectral.reg1_min, \
                                    param.spectral.reg1_max, \
                                    param.spectral.reg1_int)

    param.spectral.reg2 = np.arange(param.spectral.reg2_min, \
                                    param.spectral.reg2_max, \
                                    param.spectral.reg2_int)

    param.spectral.reg3 = np.arange(param.spectral.reg3_min, \
                                    param.spectral.reg3_max, \
                                    param.spectral.reg3_int)

    param.spectral.wlS   = np.hstack([param.spectral.reg1, \
                                      param.spectral.reg2, \
                                      param.spectral.reg3])

    # Excitation in E-F matrix
    param.spectral.wlE = np.arange(param.spectral.wlE_min, \
                                   param.spectral.wlE_max, \
                                   param.spectral.wlE_int)

    # Chlorophyll
    param.spectral.wlF = np.arange(param.spectral.wlF_min, \
                                   param.spectral.wlF_max, \
                                   param.spectral.wlF_int)

    # Other spectral (sub)regions
    param.spectral.wlP   = param.spectral.reg1  # PROSPECT data range
    param.spectral.wlO   = param.spectral.reg1  # Optical part
    param.spectral.wlT   = np.hstack([param.spectral.reg2, \
                                      param.spectral.reg3])   # Thermal part
    wlS                  = param.spectral.wlS
    param.spectral.wlPAR = wlS[np.logical_and(wlS >= 400, wlS <= 700)]
                                                # PAR range

    # Additional parameters originally defined in SCOPE_mac_linux.m
    param.spectral.nwlP = np.size(param.spectral.wlP)
    param.spectral.nwlT = np.size(param.spectral.wlT)
    param.spectral.nwlS = np.size(param.spectral.wlS)

    param.spectral.IwlP = np.arange(0, param.spectral.nwlP)
    param.spectral.IwlT = np.arange(param.spectral.nwlP, \
                                    param.spectral.nwlP + param.spectral.nwlT)

    param.spectral.IwlF = np.arange(param.spectral.IwlF_min, \
                                    param.spectral.IwlF_max) - 399


    # Data used by aggreg routine to read in MODTRAN data
    param.spectral.SCOPEspec       = emptyStruct()

    param.spectral.SCOPEspec.nreg  = 3

    param.spectral.SCOPEspec.start = [min(param.spectral.reg1), \
                                      min(param.spectral.reg2), \
                                      min(param.spectral.reg3)]
    param.spectral.SCOPEspec.end   = [max(param.spectral.reg1), \
                                      max(param.spectral.reg2), \
                                      max(param.spectral.reg3)]
    param.spectral.SCOPEspec.res   = [param.spectral.reg1[1] - \
                                      param.spectral.reg1[0], \
                                      param.spectral.reg2[1] - \
                                      param.spectral.reg2[0], \
                                      param.spectral.reg3[1] - \
                                      param.spectral.reg3[0]]

    return param.spectral


def define_atmo(param):
    """
    Define atmospheric parameters. Computations were done in SCOPE_mac_linux.m.
    """

    # Aggregate MODTRAN data over SCOPE bands by averaging
    param.atmo.M   = physics.aggreg(param.atmo.atmofile, \
                                    param.spectral.SCOPEspec)

    param.atmo.Ta  = param.meteo.Ta

    return param.atmo


def define_canopy(param):
    """
    Define canopy parameters. Computations were done in SCOPE_mac_linux.m and
    in select_input.m.
    """

    param.canopy.litab    = [np.arange(param.canopy.litab_min1, \
                                 param.canopy.litab_max1, \
                                 param.canopy.litab_int1), \
                             np.arange(param.canopy.litab_min2, \
                                 param.canopy.litab_max2, \
                                 param.canopy.litab_int2)]

    param.canopy.lazitab  = np.arange(param.canopy.lazitab_min, \
                                param.canopy.lazitab_max, \
                                param.canopy.lazitab_int)


    nl              = param.canopy.nlayers
    param.canopy.x  = np.arange(-1.0/nl, (-1.0 - 1.0/nl), -1.0/nl)
    param.canopy.xl = np.append(0, param.canopy.x)  # add top level

    # Other derived canopy quantities
    param.canopy.hot      = param.canopy.leafwidth / param.canopy.hc
    param.canopy.lidf     = physics.leafangles(param.canopy.LIDFa, \
                                               param.canopy.LIDFb)

    if (param.options.calc_zo):

        param.canopy.zo, param.canopy.d = physics.zo_and_d(param.soil, \
                                                           param.canopy)

    return param.canopy


def define_directional(param):
    """
    Define directional parameters. Computations were done in SCOPE_mac_linux.m.
    """

    if (param.options.calc_directional):

        # Load multiple angles from file
        data = np.loadtxt(param.directional.anglesfile)

        # [deg] Observation zenith angles
        param.directional.tto = data[:, 0]
        param.directional.psi = data[:, 1]

        # [1] Number of Observation Angles
        param.directional.noa = np.size(param.directional.tto)

    return param.directional


def define_leafbio(param):
    """
    Define soil parameters. Computations that were done in select_input.m.
    """

    # Derived input
    if (param.leafbio.Type):

        param.leafbio.Type = 'C4'

    else:

        param.leafbio.Type = 'C3'

    if (param.options.Cca_function_of_Cab):

        param.leafbio.Cca = 0.25 * param.leafbio.Cab

    param.leafbio.fqe = np.append(param.leafbio.fqe/5.0, param.leafbio.fqe)

    return param.leafbio


def define_optipar(param):
    """
    Read in optipar file.
    """

    # Get spectral band to interpolate optipar onto
    wl        = param.spectral.wlP

    # Use exact same input as Matlab code. Note that columns are sorted
    # differently for other optipar files
    data                 = np.loadtxt(param.optipar.optifile)
    param.optipar.n      = np.interp(wl, data[:,0], data[:,1])  # nr
    param.optipar.absChl = np.interp(wl, data[:,0], data[:,2])  # Kab
    param.optipar.absCar = np.interp(wl, data[:,0], data[:,3])  # Kca
    param.optipar.absBro = np.interp(wl, data[:,0], data[:,4])  # Ks
    param.optipar.absH2O = np.interp(wl, data[:,0], data[:,5])  # Kw
    param.optipar.absDry = np.interp(wl, data[:,0], data[:,6])  # Kdm
    param.optipar.phiI   = np.interp(wl, data[:,0], data[:,8])
    param.optipar.phiII  = np.interp(wl, data[:,0], data[:,9])

    return param.optipar


def define_soil(param):
    """
    Define soil parameters. Computations that were done in select_input.m.
    """

    # Soil thermal inertia
    if (param.options.soil_heat_method == 1):

        param.soil.GAM = physics.soil_inertia(param.soil.SMC)

    else:

        param.soil.GAM = sqrt(param.soil.cs * param.soil.rhos * \
                              param.soil.lambdas)

    # Initialize soil reflectivity array
    rs       = np.zeros((param.spectral.nwlP + param.spectral.nwlT,))

    # Soil reflectivity file
    data     = np.loadtxt(param.soil.soil_file)

    # Load reflectivity into array
    rs[param.spectral.IwlP] = data[:, param.soil.spectrum]
    rslast            = rs[param.spectral.nwlP-1]

    # Extend array
    if (param.options.rt_thermal):

        rs[param.spectral.IwlT]  = np.ones((param.spectral.nwlT,)) * rslast

    else:

        rs[param.spectral.IwlT]  = np.ones((param.spectral.nwlT,)) * \
                                    param.soil.rs_thermal

    param.soil.refl = rs

    # initial soil surface temperature
    param.soil.Ts   = param.meteo.Ta * np.ones((2,))

    # From SCOPE_mac_linux.m
    if (param.options.simulation == 1):

        if (param.options.soil_heat_method < 2):

            param.soil.Tsold = param.meteo.Ta * np.ones((12,2))

    if (param.options.calc_rss_rbs):

        param.soil.rss = 11.2 * np.exp(42 * (0.22 - param.soil.SMC))
        param.soil.rbs = param.soil.rbs * param.canopy.LAI / 3.3

    return param.soil


def define_xyt(param):
    """
    Define time series parameters. Computations that were done in
    SCOPE_mac_linux.m.
    """
    
    param.xyt.diff_tmin = abs(param.xyt.t - param.xyt.startDOY)
    param.xyt.diff_tmax = abs(param.xyt.t - param.xyt.endDOY)

    param.xyt.I_tmin    = np.where(min(param.xyt.diff_tmin) == \
                                   param.xyt.diff_tmin)[0][0]

    param.xyt.I_tmax    = np.where(min(param.xyt.diff_tmax) == \
                                   param.xyt.diff_tmax)[0][0]

    return param.xyt


# EOF compute_input.py
