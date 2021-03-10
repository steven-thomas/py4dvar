#!/usr/bin/env python

###############################################################################
# Script library_physics.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collection of defs for biochemical computations
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

import sys
import numpy             as np
import scipy.io          as spio
from   scipy             import integrate
from   math              import *

# Class to define empty structure
from   pyscope.common.structures        import emptyStruct

# Global constants
import pyscope.common.global_constants  as const

# Import libraries
import pyscope.common.library_aux       as library
import pyscope.common.library_physics   as physics


def biochemical(biochem_in):
    """
    This function calculates:
        - Stomatal resistance of a leaf or needle (s m-1)
        - Photosynthesis of a leaf or needle (umol m-2 s-1)
        - Fluorescence of a leaf or needle (fraction of fluor. in the dark)
    """

    # Calculates net assimilation rate A, fluorescence F using biochemical
    # model

    # Input (units are important):
    # Structure 'biochem_in' with the following elements:
    # Fluorescence_model            Integer with
    #                               0: With sustained quenching after drought,
    #                               as in Lee et al. (2013)
    #                               1: Calibrated for cotton data set: no
    #                               drought
    # Cs        % [umol m-3]            Initial estimate of conc. of CO2 in the
    #                                   bounary layer of the leaf
    # Q         % [umol photons m-2 s-1] Net radiation, PAR
    # T         % [oC or K]             Leaf temperature
    # eb        % [hPa]                 Intial estimate of the vapor pressure
    #                                   in leaf boundary layer
    # O         % [mmol m-3]            Concentration of O2 (in the boundary
    #                                   layer, but no problem to use ambient)
    # p         % [hPa]                 Air pressure
    # Vcmo      % [umol/m2/s]           Maximum carboxylation capacity
    # m         % []                    Ball-Berry coefficient 'm' for stomatal
    #                                   regulation
    # Type      % []                    Text parameter, either 'C3' for C3 or
    #                                   any other text for C4
    # tempcor   % []                    Boolean (0 or 1) whether or not
    #                                   temperature correction to Vcmax has to #                                   be applied.
    # Tsparams  % [],[],[K],[K],[K]     Vector of 5 temperature correction
    #                                   parameters, look in spreadsheet of
    #                                   PFTs. Only if tempcor=1, otherwise use
    #                                   dummy values
    # Rdparam   % []                    Respiration as fraction of Vcmax
    # stressfactor []                   Optional input: stress factor to
    #                                   reduce Vcmax (for example soil
    #                                   moisture, leaf age). Default value = 1.

    # Note: Always use the prescribed units. Temperature can be either C or K
    # Note: Input can be single numbers, vectors, or n-dimensional matrices

    # Output:
    # Structure 'biochem_out' with the following elements:
    # A         % [umol/m2/s]           Net assimilation rate of the leaves
    # Cs        % [umol/m3]             CO2 concentration in the boundary layer
    # eta0      % []                    Fluorescence as fraction of dark
    #                                   adapted (fs/fo)
    # rcw       % [s m-1]               Stomatal resistance
    # qE        % []                    Non photochemical quenching
    # fs        % []                    Fluorescence as fraction of PAR
    # Ci        % [umol/m3]             Internal CO2 concentration
    # Kn        % []                    Rate constant for excess heat
    # fo        % []                    Dark adapted fluorescence (fraction of
    #                                   aPAR)
    # fm        % []                    Light saturated fluorescence (fraction
    #                                   of aPAR)
    # qQ        % []                    Photochemical quenching
    # Vcmax     % [umol/m2/s]           Carboxylation capacity after
    #                                   temperature correction

    # Input

    # [umol/m2/s] Dark respiration rate at 25 oC as fraction of Vcmax
    Rdparam      = biochem_in.Rdparam

    # [] Temperature sensitivities of Vcmax, etc (dummy values of applTcorr was
    # selected above)
    Tparams      = biochem_in.Tparams

    Cs           = biochem_in.Cs
    Q            = biochem_in.Q
    T            = biochem_in.T
    eb           = biochem_in.eb
    O            = biochem_in.O
    p            = biochem_in.p
    Vcmo         = biochem_in.Vcmo
    m            = biochem_in.m
    Type         = biochem_in.Type
    tempcor      = biochem_in.tempcor
    stressfactor = biochem_in.stressfactor
    model_choice = biochem_in.Fluorescence_model

    # Convert temperatures to K if not already
    if (T.all() < 100):

        T        = T + 273.15

    rhoa         = 1.2047       # [kg m-3] Specific mass of air
    Mair         = 28.96        # [g mol-1] Molecular mass of dry air

    # Parameters (at optimum temperature)
    Kcopt        = 350.0        # [ubar] Kinetic coefficient for CO2 (Von
                                # Caemmerer and Furbank, 1999)
    Koopt        = 450.0        # [mbar] Kinetic coeeficient for  O2 (Von
                                # Caemmerer and Furbank, 1999)
    Kf           = 0.05         # [] Rate constant for fluorescence
    # Kd = 0.95                   # [] Rate constant for thermal deactivation
                                # at Fm
    Kp           = 4.0          # [] Rate constant for photochemisty
    kpopt        = Vcmo / 56.0 * 1.0e6 # [] PEPcase rate constant for C02,
                                # used here: Collatz et al: Vcmo = 39 umol m-1
                                # s-1; kp = 0.7 mol m-1 s-1.

    # Check if field is specified, if not give default value
    if hasattr(biochem_in, 'atheta'):

        atheta   = biochem_in.atheta

    else:

        atheta   = 0.8

    if (biochem_in.Fluorescence_model == 0):

        # Default drought values
        Knparams = np.array([5.01, 1.93, 10])

    else:

        # Default general values (cotton dataset)
        Knparams = np.array([2.48, 2.83, 0.114])

    # Temperature definitions
    Tref  = 25 + 273.15        # [K] Absolute temperature at 25C
    slti  = Tparams[0]
    # shti  = Tparams[1]
    Thl   = Tparams[2]
    # Tth   = Tparams[3]
    Trdm  = Tparams[4]

    # Convert pressures to bar
    Cs    = Cs * 1e-06 * p * 1.0e-3

    # Forced to be zero for C4 vegetation (this is a trick to prevent
    # oxygenase)
    if (Type == 'C4'):

        O = 0.0

    else:

        O = O * 1.0e-3 * p * 1.0e-3

    Kcopt = Kcopt * 1e-06
    Koopt = Koopt * 1.0e-3

    # Temperature corrections
    qt    = 0.1 * (T - Tref) * tempcor
    # TH  = 1 + tempcor * np.exp(shti * (T - Thh));
    TH    = 1.0 + tempcor * np.exp((- 220.0e3 + 703.0 * T) / (8.314 * T))
    TL    = 1.0 + tempcor * np.exp(slti * (Thl - T))

    Kc    = Kcopt * 2.1 ** qt
    Ko    = Koopt * 1.2 ** qt
    kp    = kpopt * 1.8 ** qt
    Kd    = np.maximum(0.0301 * (T - 273.15) + 0.0773, 0.8738)

    Rd    = Rdparam * Vcmo * (1.8 ** qt) / (1.0 + np.exp(1.3 * (T - Trdm)))

    if (Type == 'C3'):

        Vcmax = Vcmo * (2.1 ** qt) / TH * stressfactor

    else:

        Vcmax = Vcmo * (2.1 ** qt) / (TL * TH) * stressfactor

    spfy  = 2600.0 * 0.75 ** qt

    # Calculation of potential electron transport rate

    # Dark photochemistry fraction (Genty et al., 1989)
    po0   = Kp / (Kf + Kd + Kp)

    # Electron transport rate
    Je    = 0.5 * po0 * Q

    # Calculation of the intersection of enzyme and light limited curves;
    # This is the original Farquhar model
    gam   = 0.5 / spfy * O      # [bar] Compensation point

    # Calculation of internal CO2 concentration, photosynthesis
    RH    = eb / physics.satvap(T - 273.15)[0]

    # a     = 5
    # D0    = 5
    # gs0   = 1.0e-6

    if (Type == 'C3'):

        Ci     = np.maximum(0.3 * Cs, Cs * (1.0 - 1.6 / (m * RH)))
        Vc     = Vcmax * (Ci - gam) / ((Kc * (1.0 + O / Ko)) + Ci)
        Vs     = Vcmo / 2.0 * (1.8 ** qt)
        effcon = 0.2

    else:

        #if (biochem_in.A == -999):

        Ci     = np.maximum(0.1 * Cs, Cs * (1 - 1.6 / (m * RH)))

        #else:

        #    gs   = gs0 + a * np.max(0, biochem_in.A) / ((Cs - gam) * \
        #           (1.0 + (1.0 - RH) * satvap(T - 273.15) / D0))
        #    Ci   = Cs - biochem_in.A / gs

        #end

        Vc     = Vcmax
        Vs     = kp * Ci
        effcon = 0.17                   # Berry and Farquhar (1978): 1/0.167

    Ve     = Je * (Ci - gam) / (Ci + 2 * gam) * effcon

    a1, a2 = library.abc(atheta, -(Vc + Ve), Vc * Ve)
    V      = np.minimum(a1, a2) * (Ci > gam) + np.maximum(a1, a2) * (Ci <= gam)

    a1, a2 = library.abc(0.98, -(V + Vs), V * Vs)
    Ag     = np.minimum(a1, a2)
    A      = Ag - Rd

    # Actual electron transport rate
    Ja     = Ag / ((Ci - gam) / (Ci + 2 * gam)) / effcon

    rcw    = (Cs - Ci) / A * rhoa / Mair * 1.0e3 * 1.0e6 / \
                p * 1.0e3
    rcw[A <= 0] = 1.0e6

    # Fluorescence (Replace this part by Magnani or other model if needed)
    # Photochemical yield
    # Ignore error to deal with runtime warning about nan * 0 / 0
    with np.errstate(invalid = 'ignore'):

        ps     = po0 * Ja / Je

    ps[np.isnan(ps)] = 0.8

    eta, qE, qQ, fs, fo, fm, fo0, fm0, Kn = \
                        physics.Fluorescencemodel(ps, Kp, Kf, Kd, Knparams)

    Kpa    = ps / fs * Kf

    # Convert back to ppm
    Ci     = Ci * 1.0e6 / p * 1.0e3

    # Collect outputs
    biochem_out       = emptyStruct()

    biochem_out.A     = A
    biochem_out.Ci    = Ci
    biochem_out.eta   = eta
    biochem_out.rcw   = rcw
    biochem_out.qE    = qE
    biochem_out.fs    = fs
    biochem_out.Kn    = Kn
    biochem_out.fo0   = fo0
    biochem_out.fm0   = fm0
    biochem_out.fo    = fo
    biochem_out.fm    = fm
    biochem_out.qQ    = qQ
    biochem_out.Vcmax = Vcmax
    biochem_out.Kp    = Kpa
    biochem_out.ps    = ps
    biochem_out.Ja    = Ja
    # TODO: Why?
    biochem_in.A      = A

    return biochem_out


# EOF library_biochem.py
