#!/usr/bin/env python

###############################################################################
# Script library_physics.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collection of defs for various conversions and physics computations
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

import  sys
import  inspect
import  numpy               as np
import  scipy.io            as spio
from    scipy               import integrate
from    math                import *

# Class to define empty structure
from    pyscope.common.structures          import emptyStruct

# Global constants
import  pyscope.common.global_constants    as const


def aggreg(atmofile, SCOPEspec):
    """
    Aggregate MODTRAN data over SCOPE bands by averaging (over rectangular band
    passes)
    """

    # Read .atm file with MODTRAN data
    s   = np.loadtxt(atmofile, skiprows=3)

    wlM = s[:, 1]
    T   = s[:, 2:20]

    # Extract 6 relevant columns from T:
    # 1: <Eso*costts/pi>
    # 3: <rdd>
    # 4: <tss>
    # 5: <tsd>
    # 12: <tssrdd>
    # 16: <La(b)>
    U     = np.array([T[:,0], T[:,2], T[:,3], T[:,4], T[:,11], T[:,15]]).T

    nwM   = np.shape(wlM)[0]

    nreg  = SCOPEspec.nreg
    streg = np.array(SCOPEspec.start)
    enreg = np.array(SCOPEspec.end)
    width = np.array(SCOPEspec.res)

    # Nr. of bands in each region
    nwreg = np.int32((enreg - streg) / width) + 1

    off   = np.zeros((nreg,), dtype=np.int)

    # off is exactly same as in Matlab (no +/- 1)
    for i in np.arange(1, nreg):

        off[i] = off[i - 1] + nwreg[i - 1]

    nwS = np.sum(nwreg)
    n   = np.zeros((nwS,))                # Count of MODTRAN data added to band
    S   = np.zeros((nwS, 6))              # Intialize sums
    j   = np.zeros((nreg,), dtype=np.int) # Band index within regions

    # For each frequency in wlM vector from atmo file:
    for iwl in np.arange(0, nwM):

        w = wlM[iwl]                      # MODTRAN wavelength

        # For each region:
        for r in np.arange(0, nreg):

            j[r] = np.int32(round(round(w - streg[r]) / (width[r])) + 1)

            # Test if index is in valid range
            if ((j[r] > 0) & (j[r] <= nwreg[r])):

                k      = j[r] + off[r] - 1  # SCOPE band index
                S[k,:] = S[k,:] + U[iwl,:]  # Accumulate from contributing
                                            # MODTRAN data
                n[k]   = n[k] + 1.0

    M = np.zeros((np.shape(S)[0], 6))

    # Calculate averages per SCOPE band
    for i in np.arange(0, 6):

        M[:,i] = S[:,i] / n

    return M


def calcJ1(x, m, k, LAI):
    """
    Function introduced for numerically stable solutions
    """

    if (np.all(abs(m - k) > 0.001)):

        J1 = (np.exp(m * LAI * x) - np.exp(k * LAI * x)) / (k - m)

    else:

        J1 = -0.5 * (np.exp(m * LAI * x) + np.exp(k * LAI * x)) * LAI * \
                x * ((1.0 - 1.0 / 12.0 * (k - m)**2 * LAI ** 2.0 * x** 2))

    return J1


def calcJ2(x, m, k, LAI):
    """
    Function introduced for numerically stable solutions
    """

    J2 = (np.exp(k * LAI * x) - np.exp(-k * LAI) * \
            np.exp(-m * LAI * (1.0 + x))) / (k + m)

    return J2


def calczenithangle(Doy, t, Omega_g, Fi_gm, Long, Lat):
    """
    Calculate pi/2 - angle of the sun with the slope of the surface
    """

    # Input:
    # Doy       Day of the year
    # t         Time of the day (hours, GMT)
    # Omega_g   Slope azimuth angle (deg)
    # Fi_gm     Slope of the surface (deg)
    # Long      Longitude (decimal)
    # Lat       Latitude (decimal)

    # Output:
    # Fi_s      'Classic' zenith angle: perpendicular to horizontal plane
    # Fi_gs     Solar angle perpendicular to surface slope
    # Fi_g      Projected slope of the surface in the plane through the solar
    #           beam and the vertical

    #varargin = cellarray(args)
    #nargin   = 6 - [Doy, t, Omega_g, Fi_gm, Long, Lat].count(None) + len(args)

    # Count number of arguments passed to this function
    arglist = [Doy, t, Omega_g, Fi_gm, Long, Lat]

    #nargin = 3 - arglist.count(None) + len(args)
    nargin = sum(x is not None for x in arglist)

    # Parameters (if not already supplied)
    if (nargin < 6):

        Long = 13.75
        Lat  = 45.5

        if (nargin < 4):

            Omega_g = 210.0
            Fi_gm   = 30.0

    # Convert angles into radial

    # Convert day of year to radials
    G       = (Doy - 1.0) / 365.0 * 2.0 * pi

    # Convert direction of slope to radials
    Omega_g = Omega_g / 180.0 * pi

    # Convert maximum slope to radials
    Fi_gm   = Fi_gm / 180.0 * pi

    # Convert latitude to radials
    Lat     = Lat / 180.0 * pi

    # Compute the declination of the sun
    d       = 0.006918 - 0.399912 * np.cos(G) + 0.070247 * np.sin(G) - \
              0.006758 * np.cos(2.0 * G) + 0.000907 * np.sin(2.0 * G) - \
              0.002697 * np.cos(3.0 * G) + 0.00148 * np.sin(3.0 * G)

    # Equation of time
    Et      = 0.017 + 0.4281 * np.cos(G) - 7.351 * np.sin(G) - \
              3.349 * np.cos(2.0 * G) - 9.731 * np.sin(2.0 * G)

    # Compute the time of the day when the sun reaches its highest angle
    # de Pury and Farquhar (1997), Iqbal (1983)
    tm      = 12.0 + (4.0 * (-Long) - Et) / 60.0

    # Compute the hour angle of the sun
    Omega_s = (t - tm) / 12.0 * pi

    # Compute the zenith angle (equation 3.28 in De Bruin)
    Fi_s    = np.arccos( np.inner(np.sin(d), np.sin(Lat)) + \
                         np.inner(np.cos(d), np.cos(Lat)) * np.cos(Omega_s) )

    # Compute the slope of the surface Fi_g in the same plane as the solar beam
    Fi_g    = np.arctan(np.tan(Fi_gm) * np.cos(Omega_s - Omega_g))

    # Compute the angle of the sun with the vector perpendicular to the surface
    Fi_gs   = Fi_s + Fi_g

    return Fi_s, Fi_gs, Fi_g, Omega_s


def compute_fluxes(param, gap, rad):
    """
    Compute basic fluxes without energy balance
    """

    # Initialize output structures
    fluxes     = emptyStruct()
    thermal    = emptyStruct()

    # Matrix containing values for Ps of canopy
    Fc = (1.0 - gap.Ps[:-1]) / float(param.canopy.nlayers)

    # Net PAR leaves
    fluxes.aPAR     = param.canopy.LAI * (np.dot(Fc, rad.Pnh) + \
                        meanleaf(param.canopy, rad.Pnu, \
                                'angles_and_layers', gap.Ps))
    fluxes.aPAR_Cab = param.canopy.LAI * (np.dot(Fc, rad.Pnh_Cab) + \
                        meanleaf(param.canopy, rad.Pnu_Cab, \
                                'angles_and_layers', gap.Ps))
    fluxes.aPAR_Wm2 = param.canopy.LAI * (np.dot(Fc, rad.Rnh_PAR) + \
                        meanleaf(param.canopy, rad.Rnu_PAR, \
                                'angles_and_layers', gap.Ps))

    # Set other fluxes in data structure to NaN
    fluxes.Rntot  = np.nan
    fluxes.lEtot  = np.nan
    fluxes.lEtot  = np.nan
    fluxes.Htot   = np.nan
    fluxes.Rnctot = np.nan
    fluxes.lEctot = np.nan
    fluxes.Hctot  = np.nan
    fluxes.Actot  = np.nan
    fluxes.Rnstot = np.nan
    fluxes.lEstot = np.nan
    fluxes.Hstot  = np.nan
    fluxes.Gtot   = np.nan
    fluxes.Resp   = np.nan

    # Set fields in thermal data structure to NaN
    thermal.Ta    = np.nan
    thermal.Ts    = [np.nan, np.nan]
    thermal.Tcave = np.nan
    thermal.Tsave = np.nan
    thermal.raa   = np.nan
    thermal.rawc  = np.nan
    thermal.raws  = np.nan
    thermal.ustar = np.nan

    # Set additional fields in rad data structure to NaN
    rad.Eoutte    = np.nan

    return fluxes, thermal


def dcum(a, b, theta):
    """
    Cumulative leaf inclination density function, used by leafangles
    """

    rd = const.deg2rad #pi / 180.0

    if (a > 1.0):

        F = 1.0 - cos(theta * rd)

    else:

        eps    = 1e-08
        delx   = 1.0
        x      = 2.0 * rd * theta
        theta2 = x

        while np.max(delx > eps):

            y    = a * sin(x) + 0.5 * b * sin(2.0*x)
            dx   = 0.5 * (y - x + theta2)
            x    = x + dx
            delx = abs(dx)


        # Cumulative leaf inclination density function
        # pag 139 thesis says: F = 2*(y+p)/pi.
        # Since theta2=theta*2 (in rad), this makes F = (2*y + 2*theta)/pi
        F = (2.0 * y + theta2) / pi

    return F


def e2phot(la, E):
    """
    Calculates the number of moles of photons corresponding to E Joules of
    energy of wavelength lambda (m)
    """

    A          = const.A
    e          = ephoton(la)
    photons    = E / e
    molphotons = photons / A

    return molphotons


def ephoton(la):
    """
    Calculates the energy content (J) of 1 photon of wavelength lambda (m)
    """

    h = const.h
    c = const.c
    E = h * c / la

    return E


def Fluorescencemodel(ps, Kp, Kf, Kd, Knparams):
    """
    Compute fluorescense.
    """

    # Dark photochemistry fraction (Genty et al., 1989)
    po0     = Kp / (Kf + Kd + Kp)

    # Degree of light saturation
    x       = 1.0 - ps / po0
    Kno     = Knparams[0]
    alpha   = Knparams[1]
    beta    = Knparams[2]

    # Using exp(-beta) expands the interesting region between 0-1

    # This is the most expensive operation in this fn; doing it twice almost
    # doubles the time spent here
    x_alpha = x ** alpha
    Kn      = Kno * (1.0 + beta) * x_alpha / (beta + x_alpha)

    # Dark adapted fluorescence yield Fo
    fo0     = Kf / (Kf + Kp + Kd)
    fo      = Kf / (Kf + Kp + Kd + Kn)

    # Light adapted fluorescence yield Fm
    fm      = Kf / (Kf + Kd + Kn)
    fm0     = Kf / (Kf + Kd)

    fs      = fm * (1.0 - ps)
    eta     = fs / fo0

    qQ      = 1.0 - (fs - fo) / (fm - fo)       # Photochemical quenching
    qE      = 1.0 - (fm - fo) / (fm0 - fo0)     # Non-photochemical quenching

    eta     = (1.0 + 5.0) / 5.0 * eta - 1.0 / 5.0

    return eta, qE, qQ, fs, fo, fm, fo0, fm0, Kn


def heatfluxes(ra, rs, Tc, ea, Ta, e_to_q, PSI, Ca, Ci):
    """
    Calculate latent and sensible heat flux.
    """

    # Input:
    #   ra          Aerodynamic resistance for heat         s m-1
    #   rs          Stomatal resistance                     s m-1
    #   Tc          Leaf temperature                        oC
    #   ea          Vapor pressure above canopy             hPa
    #   Ta          Air temperature above canopy            oC
    #   e_to_q      Conv. from vapor pressure to abs hum    hPa-1
    #   PSI         Leaf water potential                    J kg-1
    #   Ca          Ambient CO2 concentration               umol m-3
    #   Ci          Intercellular CO2 concentration         umol m-3
    #
    # Output:
    #   lEc         Latent heat flux of a leaf              W m-2
    #   Hc          Sensible heat flux of a leaf            W m-2
    #   ec          Vapor pressure at the leaf surface      hPa
    #   Cc          CO2 concentration at the leaf surface   umol m-3

    # Constants
    rhoa = const.rhoa
    cp   = const.cp
    MH2O = const.MH2O
    R    = const.R

    lam  = (2.501 - 0.002361 * Tc) * 1000000.0      # [J kg-1] Evapor. heat
    ei   = satvap(Tc)[0] * np.exp(0.001 * PSI * MH2O / R / (Tc + 273.15))
    qi   = ei * e_to_q
    qa   = ea * e_to_q

    lE   = rhoa / (ra + rs) * lam * (qi - qa)   # [W m-2] Latent heat flux
    H    = (rhoa * cp) / ra * (Tc - Ta)         # [W m-2] Sensible heat flux

    # [W m-2] Vapor pressure at the leaf surface
    ec   = ea + (ei - ea) * ra / (ra + rs)

    # [umol m-2 s-1] CO2 concentration at the leaf surface
    Cc   = Ca - (Ca - Ci) * ra / (ra + rs)

    return lE, H, ec, Cc


def leafangles(a, b):
    """
    Equivalent of leafangles.m.

    Subroutine FluorSail_dladgen Version 2.3

    For more information look to page 128 of "theory of radiative transfer
    models applied in optical remote sensing of vegetation canopies"
    """

    F    = np.zeros((13))
    lidf = np.zeros((13))

    for i in np.arange(0, 8):

        theta    = (i+1.0) * 10.0           # theta_l = 10:80
        F[i]     = dcum(a, b, theta)

    for i in np.arange(8, 12):

        theta    = 80.0 + (i - 7.0) * 2.0   # theta_l = 82:88
        F[i]     = dcum(a, b, theta)

    for i in np.arange(12, 13):

        F[i]     = 1                        # theta_l = 90:90

    for i in np.arange(12, 0, -1):

         lidf[i] = F[i] - F[i-1]            # lidf = dF/dtheta

    lidf[0] = F[0]                          # Boundary condition

    return lidf


def meanleaf(canopy, F, choice, Ps):
    """
    Calculates the layer average and the canopy average of leaf properties
    per layer, per leaf angle and per leaf azimuth (36)
    """

    # Input:
    # F       input matrix (3D)   [nli, nlazi,nl]
    # choice  integration method:
    #         'angles': integration over leaf angles
    #         'angles_and_layers' : integration over leaf layers and leaf
    #         angles
    # Ps      fraction sunlit per layer [nl]

    # Output:
    # Fout    in case of choice = 'angles': [nl]
    #         in case of choice = 'angles_and_layers': [1]


    nl    = canopy.nlayers
    nli   = canopy.nlincl
    nlazi = canopy.nlazi
    lidf  = canopy.lidf

    Fout  = np.zeros((nli, nlazi, nl))

    # Integration over leaf angles
    if (choice == 'angles'):

        for j in np.arange(0, nli):

            Fout[j,:,:] = F[j,:,:] * lidf[j] # [nli, nlazi,nl]

        Fsum = Fout.sum(axis=0).sum(axis=0) / nlazi  # [1,1,nl]

        # FIXME: Unclear why permutation is needed (currently doesn't work)
        #Fout = permute_(Fout,[3,1,2])
        #Fsum = np.transpose(Fsum, (2, 0, 1)).shape # [nl]

    # Not implemented
    elif (choice == 'layers'):

        pass

    # Integration over both leaf angles and layers
    elif (choice == 'angles_and_layers') :

        for i in np.arange(0, nli):

            Fout[i,:,:] = F[i,:,:] * lidf[i]

        for j in np.arange(0, nl):

            Fout[:,:,j] = Fout[:,:,j] * Ps[j]

        Fsum = Fout.sum(axis=0).sum(axis=0).sum(axis=0) / nlazi / nl

    return Fsum


def Planck(wl=None, Tb=None, em=None, *args, **kwargs):
    """
    Function from Planck.m.
    """

    # Count number of arguments passed to this function
    arglist = [wl, Tb, em]

    #nargin = 3 - arglist.count(None) + len(args)
    nargin = sum(x is not None for x in arglist)

    c1 = 1.191066e-22
    c2 = 14388.33

    if (nargin < 3):

        em = np.ones(np.shape(Tb))

    Lb = em * c1 * (wl * 1e-09) ** (-5) / (np.exp(c2 / (wl * 0.001 * Tb)) - 1)

    return Lb


def Psofunction(K, k, LAI, q, dso, xl):
    """
    Factor for correlation of Ps and Po (length [nl+1])
    """

    if (dso != 0):

        alf = (dso / q) * 2.0 / (k + K)
        pso = np.exp((K + k) * LAI * xl + \
            sqrt(K * k) * LAI / (alf) * (1.0 - np.exp(xl * (alf))))

    else:

        pso = np.exp((K + k) * LAI * xl - np.sqrt(K * k) * LAI * xl)

    return pso


def psim(z, L, unst, st):
    """
    Subfunction pm for stability correction (eg. Paulson, 1970)
    """

    # L had indexing, but it is just a scalar at the moment. Removed indexing
    # for now, from both L and pm

    pm       = np.zeros((np.shape(L)))

    if (np.size(unst) > 0):

        x        = (1.0 - 16.0 * z / L) ** (1.0 / 4.0)
        pm       = 2.0 * np.log((1.0 + x) / 2.0) + \
                   np.log((1.0 + x ** 2.0) / 2.0) - \
                   2.0 * atan(x) + pi / 2.0             # Unstable

    if (np.size(st) > 0):

        pm       = -5.0 * z / L                         # Stable

    return pm


def psih(z, L, unst, st):
    """
    Subfunction ph for stability correction (eg. Paulson, 1970)
    """

    # L had indexing, but it is just a scalar at the moment. Removed indexing
    # for now, from both L and ph

    ph       = np.zeros((np.shape(L)))

    if (np.size(unst) > 0):

        x        = (1.0 - 16.0 * z / L) ** (1.0 / 4.0)
        ph       = 2.0 * np.log((1.0 + x ** 2.0) / 2.0)     # Unstable

    if (np.size(st) > 0):

        ph       = -5.0 * z / L                             # Stable

    return ph


def phstar(z, zR, d, L, st, unst):
    """
    Subfunction phs for stability correction (eg. Paulson, 1970)
    """

    # L had indexing, but it is just a scalar at the moment. Removed indexing
    # for now, from both L and phs

    phs       = np.zeros((np.shape(L)))

    if (np.size(unst) > 0):

        x         = (1.0 - 16.0 * z / L) ** 0.25
        phs       = (z - d) / (zR - d) * (x ** 2 - 1.0) / (x ** 2 + 1.0)
        # Unstable

    if (np.size(st) > 0):

        phs       = -5.0 * z / L                                # Stable

    return phs


def resistances(resist_in):
    """
    Calculate aerodynamic and boundary resistances for soil and vegetation.
    """

    #   Source:     Wallace and Verhoef (2000) 'Modelling interactions in
    #               mixed-plant communities: light, water and carbon dioxide',
    #               in: Bruce Marshall, Jeremy A. Roberts (ed), 'Leaf
    #               Development and Canopy Growth',
    #               Sheffield Academic Press, UK. ISBN 0849397693

    #               ustar:  Tennekes, H. (1973) 'The logaritmic wind profile',
    #               J. Atmospheric Science, 30, 234-238

    #               Psih:   Paulson, C.A. (1970), The mathematical
    #               representation of wind speed and temperature in the
    #               unstable atmospheric surface layer. J. Applied Meteorol. 9,
    #               857-861

    # Note: Equation numbers refer to equation numbers in Wallace and Verhoef
    # (2000)

    # Input:
    # resist_in   aerodynamic resistance parameters and wind speed
    #
    # The strucutre resist_in contains the following elements:
    # u         =   windspeed
    # L         =   stability
    # LAI       =   Leaf Area Index
    # rbs       =   Boundary Resistance of soil                         [s m-1]
    # rss       =   Surface resistance of soil for vapour transport     [s m-1]
    # rwc       =   Within canopy Aerodynamic Resistance canopy         [s m-1]
    # z0m       =   Roughness lenght for momentum for the vegetation    [m]
    # d         =   Displacement height (Zero plane)                    [m]
    # z         =   Measurement height                                  [m]
    # h         =   Vegetation height                                   [m]

    # Output:
    # resist_out  aeorodynamic resistances
    #
    # The strucutre resist_out contains the following elements:
    # ustar     =   Friction velocity                                   [m s-1]
    # raa       =   Aerodynamic resistance above the canopy             [s m-1]
    # rawc      =   Total resistance within the canopy (canopy)         [s m-1]
    # raws      =   Total resistance within the canopy (soil)           [s m-1]
    # rai       =   Aerodynamic resistance in inertial sublayer         [s m-1]
    # rar       =   Aerodynamic resistance in roughness sublayer        [s m-1]
    # rac       =   Aerodynamic resistance in canopy layer (above z0+d) [s m-1]
    # rbc       =   Boundary layer resistance (canopy)                  [s m-1]
    # rwc       =   Aerodynamic Resistance within canopy(canopy)(Update)[s m-1]
    # rbs       =   Boundary layer resistance (soil) (Update)           [s m-1]
    # rws       =   Aerodynamic resistance within canopy(soil)          [s m-1]
    # rss       =   Surface resistance vapour transport(soil)(Update)   [s m-1]
    # uz0       =   windspeed at z0                                     [m s-1]
    # Kh        =   Diffusivity for heat                                [m2s-1]

    # Parameters
    kappa = const.kappa
    Cd    = resist_in.Cd
    u     = resist_in.u
    L     = resist_in.L
    LAI   = resist_in.LAI
    rbs   = resist_in.rbs
    # rss   = resist_in.rss
    rwc   = resist_in.rwc
    z0m   = resist_in.zo
    d     = resist_in.d
    z     = resist_in.z
    h     = resist_in.hc
    w     = resist_in.w

    # Derived parameters

    # Top of roughness sublayer, bottom of intertial sublayer
    zr    = 2.5 * h                         # [m]

    # Dimensionless wind extinction coefficient (W&V eq. 33)
    n     = Cd * LAI / (2 * kappa ** 2)     # []

    # Stability correction functions

    # Correction for non-neutral conditions
    # neu    = (L >= -.001 & L <= .001).nonzero()[0][0]
    unst   = np.where(L < -4)[0]
    st     = np.where(L > 4000.0)[0]

    # Stability correction functions, friction velocity and Kh = Km = Kv
    pm_z   = psim(z - d, L, unst, st)
    ph_z   = psih(z - d, L, unst, st)
    pm_h   = psim(h - d, L, unst, st)
    # ph_h  = psim(h - d, L, unst, st)
    ph_zr  = psih(zr - d, L, unst, st) * (z >= zr) + ph_z * (z < zr)
    phs_zr = phstar(zr, zr, d, L, st, unst)
    phs_h  = phstar(h, zr, d, L, st, unst)

    # W&V Eq 30
    ustar  = max(0.001, kappa * u / (np.log((z - d) / z0m) - pm_z))
    Kh     = kappa * ustar * (zr - d)                       # W&V Eq 35

    # Wind speed at height h and z0m
    #uh     = np.max(ustar / kappa * ((np.log((h - d) / z0m) - pm_h)), 0.01)
    # use np.maximum instead of np.max
    uh     = np.maximum(ustar / kappa * ((np.log((h - d) / z0m) - pm_h)), 0.01)
    uz0    = uh * np.exp(n * ((z0m + d) / h - 1))           # W&V Eq 32

    # Resistances

    # W&V Eq 41
    rai    = (z > zr) * ((1.0 / (kappa * ustar) * \
                ((np.log((z - d) / (zr - d)) - ph_z + ph_zr))))

    # W&V Eq 39
    rar    = 1.0 / (kappa * ustar) * (((zr - h) / (zr - d))) - phs_zr + phs_h

    # W&V Eq 42
    rac    = h * np.sinh(n) / (n * Kh) * (np.log((np.exp(n) - 1) / \
                (np.exp(n) + 1)) - np.log((np.exp(n * (z0m + d) / h) - 1) / \
                (np.exp(n * (z0m + d) / h) + 1)))

    # W&V Eq 43
    rws    = h * np.sinh(n) / (n * Kh) * \
                (np.log((np.exp(n * (z0m + d) / h) - 1) / \
                (np.exp(n * (z0m + d) / h) + 1)) - \
                np.log((np.exp(n * (0.01) / h) - 1) / \
                (np.exp(n * (0.01) / h) + 1)))

    # W&V Eq 31, but slightly different
    rbc    = 70.0 / LAI * np.sqrt(w / uz0)

    # Aerodynamic resistance
    raa    = rai + rar + rac                # Above the canopy, W&V Figure 8.6
    rawc   = rwc + rbc                      # Within the canopy (canopy)
    raws   = rws + rbs                      # Within the canopy (soil)

    # Output structure
    resist_out = emptyStruct()

    resist_out.Kh       = []

    # W&V Eq 35
    # Kh, ustar and L are just scalars, so removed indexing
    if (np.size(unst) > 0):

        resist_out.Kh   = kappa * ustar * (zr - d) * \
                                ((1 - 16 * (h - d) / L) ** 0.5)

    if (np.size(st) > 0):

        resist_out.Kh   = kappa * ustar * (zr - d) * \
                                ((1 + 5 * (h - d) / L) ** - 1)

    resist_out.uz0      = uz0
    resist_out.ustar    = ustar
    resist_out.rai      = rai
    resist_out.rar      = rar
    resist_out.rac      = rac
    resist_out.rws      = rws
    resist_out.rbc      = rbc

    # To prevent unrealistically high resistances
    resist_out.raa      = min(400.0, raa)
    resist_out.rawc     = min(400.0, rawc)
    resist_out.raws     = min(400.0, raws)

    return resist_out


def satvap(T):
    """
    Calculates the saturated vapour pressure at temperature T (degrees C)
    and the derivative of es to temperature s (kPa/C)
    """
    # The output is in mbar or hPa. The approximation formula that is used is:
    # es(T) = es(0)*10^(aT/(b+T));
    # Where es(0) = 6.107 mb, a = 7.5 and b = 237.3 degrees C
    # and s(T) = es(T)*ln(10)*a*b/(b+T)^2

    # Constants
    a  = 7.5
    b  = 237.3     # Degrees C

    # Calculation
    es = 6.107 * 10.0 ** (7.5 * T / (b + T))
    s  = es * np.log(10) * a * b / (b + T) ** 2

    return es, s


def soil_inertia(SMC):
    """
    Soil inertia method by Murray and Verhoef
    """

    theta_s  = 0.435           # Saturated water content, m3/m3
    gamma_s  = 0.96            # Soil texture dependent parameter
    dels     = 1.33            # Shape parameter
    phis     = 0.435           # Phis == theta_s
    QC       = 0.6             # Quartz content

    Sr       = SMC / theta_s
    ke       = exp(gamma_s * (1 - Sr**(gamma_s - dels)))

    lambda_qc  = 7.7           # Thermal conductivity of quartz, constant
    lambda_wtr = 0.57          # Thermal conductivity of water, W/m.K, constant

    lambda_d   = -0.56 * phis + 0.51
    lambda_s   = (lambda_qc ** (QC)) * lambda_d ** (1.0 - QC)
    lambda_w   = (lambda_s ** (1 - phis)) * lambda_wtr ** (phis)
    lambdas    = ke * (lambda_w - lambda_d) + lambda_d

    Hcs = 2.0e6
    Hcw = 4.2e6
    Hc  = (Hcw * SMC) + (1 - theta_s) * Hcs
    GAM = sqrt(lambdas*Hc)

    return GAM


def Stefan_Boltzmann(T_C):
    """
    Compute Stefan-Boltzmann factor
    """

    C2K     = const.C2K
    sigmaSB = const.sigmaSB

    H       = sigmaSB * (T_C + C2K) ** 4

    return H


def calctav(alfa, nr):
    """
    Helper definition for Fluspect module, using the original SCOPE algorithm.
    """

    rd  = pi / 180.0
    n2  = nr ** 2

    # This is np in SCOPE, renamed np1 to avoid conflict with numpy
    np1 = n2 + 1.0

    nm  = n2 - 1.0
    a   = (nr + 1.0) * (nr + 1.0) / 2.0
    k   = -(n2 - 1.0) * (n2 - 1.0) / 4.0
    sa  = np.sin(alfa * rd)

    if (abs(alfa - 90) < 1.0e-6):

        b1 = 0

    else:

        b1  = np.sqrt((sa ** 2 - np1 / 2.0) * (sa ** 2 - np1 / 2.0) + k)

    b2  = sa ** 2 - np1 / 2.0
    b   = b1 - b2
    b3  = b ** 3
    a3  = a ** 3
    ts  = (k ** 2.0 / (6.0 * b3) + k / b - b / 2.0) - \
          (k ** 2.0 / (6.0 * a3) + k / a - a / 2.0)

    tp1 = -2.0 * n2 * (b - a) / (np1 ** 2)
    tp2 = -2.0 * n2 * np1 * np.log(b / a) / (nm ** 2)
    tp3 = n2 * (1.0 / b - 1.0 / a) / 2.0
    tp4 = 16.0 * n2 ** 2.0 * (n2 ** 2 + 1.0) * \
            np.log((2.0 * np1 * b - nm ** 2) / (2.0 * np1 * a - nm ** 2)) / \
            (np1 ** 3.0 * nm ** 2)
    tp5 = 16.0 * n2 ** 3.0 * (1.0 / (2.0 * np1 * b - nm ** 2) - \
            1.0 / (2.0 * np1 * a - nm ** 2)) / (np1 ** 3)

    tp  = tp1 + tp2 + tp3 + tp4 + tp5

    tav = (ts + tp) / (2.0 * sa ** 2)

    return tav


def tav(teta, ref):
    """
    Helper definition for Fluspect module, according to Christian Frankenberg's
    modifications to calctav.
    """

    s     = len(ref)
    teta  = teta*np.pi/180.
    refr2 = ref*ref
    ax    = (ref + 1.)**2/2.
    bx    = -(refr2 - 1.)**2/4.

    if (teta == 0):

        return 4.*ref / (ref + 1.)**2

    else:

        if teta == np.pi/2:

            b1 = np.zeros((s,))

        else:

            b1 = np.sqrt((np.sin(teta)**2 - (refr2 + 1.)/2.)**2 + bx)

        b2  = np.sin(teta)**2 - (refr2 + 1.)/2.
        b0  = b1 - b2

        ts  = (bx**2 / (6.*b0**3) + bx/b0 - b0/2.) - \
                (bx**2 / (6.*ax**3) + bx/ax - ax/2.)

        tp1 = -2.*refr2*(b0 - ax) / (refr2 + 1.)**2
        tp2 = -2.*refr2*(refr2 + 1.) * np.log(b0/ax) / (refr2 - 1.)**2
        tp3 = refr2*(1./b0 - 1./ax)/2.
        tp4 = 16.*refr2**2 * (refr2**2 + 1.) * np.log((2.*(refr2 + 1.)*b0 - \
                (refr2 - 1.)**2) / (2.*(refr2+1.)*ax - \
                (refr2 - 1.)**2)) / ((refr2 + 1.)**3 * (refr2 - 1.)**2)
        tp5 = 16.*refr2**3 * (1. / (2.*(refr2 + 1.)*b0 - ((refr2 - 1.)**2)) - \
                1./(2.*(refr2 + 1.) * ax - (refr2 - 1.)**2)) / (refr2 + 1.)**3

        tp  = tp1 + tp2 + tp3 + tp4 + tp5

        res = (ts + tp) / (2.*np.sin(teta)**2)

        return res


def volscat(tts, tto, psi, ttli):
    """
    Volume scattering used in geometric factors.
    tts:  [1]  Sun zenith angle in degrees
    tto:  [1]  Observation zenith angle in degrees
    psi:  [1]  Difference of azimuth angle between solar and viewing position
    ttli: [13] Leaf inclination array
    """

    deg2rad  = const.deg2rad

    nli      = np.size(ttli)
    psi_rad  = psi * deg2rad * np.ones((nli,))

    cos_psi  = np.cos(psi * deg2rad)  # cosine of relative azimuth angle
    cos_ttli = np.cos(ttli * deg2rad) # cosine of normal of upperside of leaf
    sin_ttli = np.sin(ttli * deg2rad) # sine of normal of upperside of leaf

    cos_tts  = np.cos(tts * deg2rad)  # cosine of sun zenith angle
    sin_tts  = np.sin(tts * deg2rad)  # sine of sun zenith angle
    cos_tto  = np.cos(tto * deg2rad)  # cosine of observer zenith angle
    sin_tto  = np.sin(tto * deg2rad)  # sine of observer zenith angle

    Cs       = cos_ttli * cos_tts     # p305{1}
    Ss       = sin_ttli * sin_tts     # p305{1}
    Co       = cos_ttli * cos_tto     # p305{1}
    So       = sin_ttli * sin_tto     # p305{1}

    As       = np.array([Ss, Cs]).max(axis=0)
    Ao       = np.array([So, Co]).max(axis=0)

    bts      = np.arccos(-Cs / As)    # p305{1}
    bto      = np.arccos(-Co / Ao)    # p305{2}

    chi_o    = 2.0 / pi * ((bto - pi / 2.0) * Co + np.sin(bto) * So)
    chi_s    = 2.0 / pi * ((bts - pi / 2.0) * Cs + np.sin(bts) * Ss)

    delta1   = abs(bts - bto)               # p308{1}
    delta2   = pi - abs(bts + bto - pi)     # p308{1}

    Tot      = psi_rad + delta1 + delta2    # p130{1}

    bt1      = np.array([psi_rad, delta1]).min(axis=0)
    bt3      = np.array([psi_rad, delta2]).max(axis=0)
    bt2      = Tot - bt1 - bt3

    T1       = 2.0 * Cs * Co + Ss * So * cos_psi
    T2       = np.sin(bt2) * (2.0 * As * Ao + \
                Ss * So * np.cos(bt1) * np.cos(bt3))

    Jmin     = bt2 * T1 - T2
    Jplus    = (pi - bt2) * T1 + T2

    frho     = Jplus / (2.0 * pi ** 2)
    ftau     = -Jmin / (2.0 * pi ** 2)

    # pag.309 wl-> pag 135{1}
    frho     = np.array([np.zeros((nli,)), frho]).max(axis=0)
    ftau     = np.array([np.zeros((nli,)), ftau]).max(axis=0)

    return chi_s, chi_o, frho, ftau


def zo_and_d(soil, canopy):
    """
    Calculates roughness length for momentum and zero plane displacement from
    vegetation height and LAI.
    Source: Verhoef, McNaughton & Jacobs (1997), HESS 1, 81-91
    """

    # Constants
    kappa = const.kappa

    # Parameters
    CR     = canopy.CR
    CSSOIL = soil.CSSOIL
    CD1    = canopy.CD1
    Psicor = canopy.Psicor
    LAI    = canopy.LAI
    h      = canopy.hc

    # Calculation of length
    sq     = sqrt(CD1 * LAI / 2.0)
    G1     = max(3.3, (CSSOIL + CR*LAI/2.0)**(-0.5))

    # Eq 12 in Verhoef et al (1997)
    d      = (LAI > 1e-07 and h > 1e-07) * h * (1 - (1 - np.exp(-sq)) / sq)
    zom    = (h - d) * np.exp(-kappa * G1 + Psicor)

    return zom, d


# EOF library_physics.py
