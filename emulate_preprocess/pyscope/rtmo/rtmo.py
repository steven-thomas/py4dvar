#!/usr/bin/env python

###############################################################################
# Script rtmo.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: equivalent of RTMo module in SCOPE
# Note: this script corresponds to rtmo.m in SCOPE.
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

# Input:
#   spectral    information about wavelengths and resolutions
#   atmo        MODTRAN atmospheric parameters
#   soil        soil properties
#   leafopt     leaf optical properties
#   canopy      canopy properties (such as LAI and height) angles viewing and
#               observation angles
#   meteo       has the meteorological variables. Is only used to correct
#               the total irradiance if a specific value is provided
#               instead of the usual Modtran output.
#   rad         initialization of the structure of the output 'rad'
#   options     simulation options. Here, the option
#               'calc_vert_profiles' is used, a boolean that tells whether
#               or not to output data of 60 layers separately.

# Output:
#   gap         probabilities of direct light penetration and viewing
#   rad         a large number of radiative fluxes: spectrally distributed
#               and integrated, and canopy radiative transfer coefficients.
#   profiles    vertical profiles of radiation variables such as absorbed PAR.


import  numpy                           as np
from    scipy                           import integrate
from    math                            import *
import  os

# Class to define empty structure
from    pyscope.common.structures       import emptyStruct

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics


class RTMo():
    """
    Calculates the spectra of hemisperical and directional observed visible
    and thermal radiation (fluxes E and radiances L), as well as the single
    and bi-directional gap probabilities.
    """

    def __init__(self, param):
        """
        Prepare input parameters and initialize arrays.
        """

        # Load spectral bands
        spectral     = param.spectral

        self.wl      = spectral.wlS       # SCOPE wavelengths
        self.wlP     = spectral.wlP
        self.wlT     = spectral.wlT
        self.wlPAR   = spectral.wlPAR     # PAR wavelength range
        self.minPAR  = min(self.wlPAR)
        self.maxPAR  = max(self.wlPAR)
        self.nwl     = np.size(self.wl)

        # Indices for PAR wavelenghts within wl
        self.Ipar    = np.where(np.logical_and(self.wl >= self.minPAR, \
                                               self.wl <= self.maxPAR))

        # Additional indices and array lengths
        self.IwlP    = spectral.IwlP
        self.IwlT    = spectral.IwlT
        self.nwlP    = spectral.nwlP
        self.nwlT    = spectral.nwlT

        # Load atmo properties
        atmo         = param.atmo
        self.atmoM   = atmo.M
        self.Ta      = atmo.Ta

        # Load angle arrays
        angles       = param.angles
        self.tts     = angles.tts
        self.tto     = angles.tto
        self.psi     = angles.psi

        # Load canopy properties
        self.canopy  = param.canopy

        self.nl      = self.canopy.nlayers # Number of canopy layers (60)
        self.litab   = self.canopy.litab   # SAIL leaf inclination angles
        self.lazitab = self.canopy.lazitab # Leaf azimuth angles rel to sun
        self.nli     = self.canopy.nlincl  # Nr of leaf inclinations (13)
        self.nlazi   = self.canopy.nlazi   # Number of azimuth angles (36)
        self.LAI     = self.canopy.LAI     # Leaf area index
        self.lidf    = self.canopy.lidf    # Leaf inclination dist function
        self.x       = self.canopy.x       # All levels except for the top
        self.xl      = self.canopy.xl      # All levels + soil
        self.q       = self.canopy.hot

        self.dx      = 1.0 / float(self.nl)

        # [1] LAI of elementary layer
        self.iLAI    = float(self.LAI) / float(self.nl)

        # Get leafbio parameters
        leafbio      = param.leafbio

        self.rho_thermal = leafbio.rho_thermal
        self.tau_thermal = leafbio.tau_thermal

        # Get meteo parameters
        self.meteo   = param.meteo

        # Get soil properties
        soil         = param.soil

        self.rs      = soil.refl       # [nwl, nsoils] Soil reflectance spectra
        self.epss    = 1.0 - self.rs   # [nwl] Emissivity of soil

        # Initialize arrays

        # [nl+1] Abs. diffuse rad soil+veg
        # Should this be length nl or nl+1? Comment in SCOPE says nl+1, but
        # code has nl (not nl+1)
        self.Rndif      = np.zeros((self.nl,))

        # [nl] Incident and net PAR veg
        self.Pdif       = np.zeros((self.nl,))
        self.Pndif      = np.zeros((self.nl,))
        self.Pndif_Cab  = np.zeros((self.nl,))
        self.Rndif_PAR  = np.zeros((self.nl,))

        # [nl+1,nwl] Up and down diff. rad.
        self.Emin_      = np.zeros((self.nl + 1, self.nwl))
        self.Eplu_      = np.zeros((self.nl + 1, self.nwl))

        # [nl,nwl] Abs diff and PAR veg.
        self.Rndif_     = np.zeros((self.nl, self.nwl))

        # [nl, Ipar]
        self.Pndif_     = np.zeros((self.nl, np.size(self.Ipar)))
        self.Pndif_Cab_ = np.zeros((self.nl, np.size(self.Ipar)))
        self.Rndif_PAR_ = np.zeros((self.nl, np.size(self.Ipar)))

        # [nli,nlazi,nl] Inc and net rad and PAR sunlit
        self.Puc        = np.zeros((self.nli, self.nlazi, self.nl))
        self.Rnuc       = np.zeros((self.nli, self.nlazi, self.nl))
        self.Pnuc       = np.zeros((self.nli, self.nlazi, self.nl))
        self.Pnuc_Cab   = np.zeros((self.nli, self.nlazi, self.nl))
        self.Rnuc_PAR   = np.zeros((self.nli, self.nlazi, self.nl))

        # Initialize profiles structure
        self.profiles   = emptyStruct()


    def getLeafopt(self, param, leafopt):
        """
        Get leafopt output from Fluspect module and extend arrays.
        """

        # Initialize arrays
        self.rho     = np.zeros((self.nwlP + self.nwlT,))
        self.tau     = np.zeros((self.nwlP + self.nwlT,))

        # Output from Fluspect module
        self.leafopt = leafopt
        self.kChlrel = leafopt.kChlrel
        self.rho[self.IwlP] = leafopt.refl    # [nwl] Leaf/needle reflection
        self.tau[self.IwlP] = leafopt.trans   # [nwl] Leaf/needle transmission

        rlast    = self.rho[self.nwlP-1]
        tlast    = self.tau[self.nwlP-1]

        # Extend array
        if (param.options.rt_thermal):

            self.rho[self.IwlT] = np.ones((self.nwlT,)) * rlast
            self.tau[self.IwlT] = np.ones((self.nwlT,)) * tlast

        else:

            self.rho[self.IwlT] = np.ones((self.nwlT,)) * self.rho_thermal
            self.tau[self.IwlT] = np.ones((self.nwlT,)) * self.tau_thermal

        self.epsc = 1.0 - self.rho - self.tau # [nwl] Emissivity of leaves

        # Make the extension of refl and trans accessible to later modules
        self.leafopt.refl  = self.rho
        self.leafopt.trans = self.tau


    def computeGeometric(self):
        """
        Compute geometric quantities used for fluxes.
        """

        deg2rad = const.deg2rad

        # General geometric quantities (scalars)
        self.cos_tts = np.cos(self.tts * deg2rad)
        self.tan_tto = np.tan(self.tto * deg2rad)
        self.cos_tto = np.cos(self.tto * deg2rad)
        self.sin_tts = np.sin(self.tts * deg2rad)
        self.tan_tts = np.tan(self.tts * deg2rad)
        self.psi     = abs(self.psi - 360 * round(self.psi / 360))
        self.dso     = sqrt(self.tan_tts ** 2 + self.tan_tto ** 2 - \
                2.0 * self.tan_tts * self.tan_tto * np.cos(self.psi * deg2rad))

        # Convert litab to single vector
        litab1 = np.hstack(self.litab)

        # Geometric factors associated with extinction and scattering [13]
        self.chi_s, self.chi_o, self.frho, self.ftau = \
                physics.volscat(self.tts, self.tto, self.psi, litab1)

        self.cos_ttlo = np.cos(self.lazitab * deg2rad) # [36] Cos leaf azimuth
                                                       # angles
        self.cos_ttli = np.cos(litab1 * deg2rad) # [13] Cos leaf angles
        self.sin_ttli = np.sin(litab1 * deg2rad) # [13] Sinus leaf angles

        # p306{1} Extinction coefficient per leaf angle
        self.ksli  = self.chi_s / self.cos_tts # [13] In direction of sun
        self.koli  = self.chi_o / self.cos_tto # [13] In direction of observer

        # [13] p309{1} Area scattering coefficient fractions
        self.sobli = self.frho * pi / (self.cos_tts * self.cos_tto)
        self.sofli = self.ftau * pi / (self.cos_tts * self.cos_tto)
        self.bfli  = self.cos_ttli ** 2


        # Integration over angles using a vector inner product

        # Extinction coefficients
        self.k   = np.inner(self.ksli, self.lidf) # p306{1} In direction of sun
        self.K   = np.inner(self.koli, self.lidf) # p307{1} in direction of
                                                  # observer
        self.bf  = np.inner(self.bfli, self.lidf)

        # Weight of specular to directional scatter coefficients
        self.sob = np.inner(self.sobli, self.lidf) # Back scatter
        self.sof = np.inner(self.sofli, self.lidf) # Forward scatter

        # Geometric factors to be used later with rho and tau, f1 f2 of p304

        self.sdb = 0.5 * (self.k + self.bf) # fs*f1

        # Weight of specular to diffuse scatter coefficients
        self.sdf = 0.5 * (self.k - self.bf) # fs*f2: Forward scatter
        self.ddb = 0.5 * (1.0 + self.bf)      # f1^2+f2^2: Back scatter

        # Weight of diffuse to diffuse scatter coefficients
        self.ddf = 0.5 * (1.0 - self.bf)      # 2*f1*f2: Forward scatter

        # Weight of diffuse to directional scatter coefficients
        self.dob = 0.5 * (self.K + self.bf) # fo*f1: Back scatter
        self.dof = 0.5 * (self.K - self.bf) # fo*f2: Forward scatter

        # Solar irradiance factor for all leaf orientations (p305)
        self.Cs         = self.cos_ttli * self.cos_tts          # [nli]
        self.Ss         = self.sin_ttli * self.sin_tts          # [nli]
        self.cos_deltas = np.outer(self.Cs, np.ones((self.nlazi,))) + \
                          np.outer(self.Ss, self.cos_ttlo)      # [nli,nlazi]
        self.fs         = abs(self.cos_deltas / self.cos_tts)   # [nli,nlazi]

        # Probabilities Pos, Po, Pso: of viewing a leaf in direction, p154{1}
        self.Ps = np.exp(self.k * self.xl * self.LAI) # [nl+1] In solar dir
        self.Po = np.exp(self.K * self.xl * self.LAI) # [nl+1] In observ dir

        # Correct for finite dx
        self.Ps[0:self.nl] = self.Ps[0:self.nl] * (1.0 - np.exp(-self.k * \
            self.LAI * self.dx)) / (self.k * self.LAI * self.dx)
        self.Po[0:self.nl] = self.Po[0:self.nl] * (1.0 - np.exp(-self.K * \
            self.LAI * self.dx)) / (self.K * self.LAI * self.dx)

        self.Pso = np.zeros((np.shape(self.Po)))

        for j in np.arange(0, np.shape(self.xl)[0]):

            self.Pso[j] = (integrate.quad( lambda y: physics.Psofunction( \
                            self.K, self.k, self.LAI, self.q, self.dso, y), \
                            self.xl[j] - self.dx, self.xl[j] )[0]) / self.dx

        # Take care of rounding error
        self.Pso[self.Pso > self.Po] = np.array([self.Po[self.Pso > self.Po], \
                                    self.Ps[self.Pso > self.Po]]).min(axis=0)
        self.Pso[self.Pso > self.Ps] = np.array([self.Po[self.Pso > self.Ps], \
                                    self.Ps[self.Pso > self.Ps]]).min(axis=0)


    def computeUpDownFluxes(self):
        """
        Compute upward and downward fluxes.
        """

        # Scattering coefficients; vectors with length [nwl] (p305{1},p309{1})

        # Diffuse backscatter, diffuse incidence
        sigb  = self.ddb * self.rho + self.ddf * self.tau

        # Diffuse forward scatter, forward incidence
        sigf  = self.ddf * self.rho + self.ddb * self.tau

        # Diffuse backscatter, specular incidence
        sb    = self.sdb * self.rho + self.sdf * self.tau

        # Diffuse forward scatter, specular incidence
        sf    = self.sdf * self.rho + self.sdb * self.tau

        # Directional backscatter, diffuse incidence
        self.vb    = self.dob * self.rho + self.dof * self.tau

        # Directional forward scatter, diffuse incidence
        self.vf    = self.dof * self.rho + self.dob * self.tau

        # Bidirectional scatter
        self.w     = self.sob * self.rho + self.sof * self.tau

        a     = 1 - sigf                        # Attenuation
        m     = np.sqrt(a ** 2 - sigb ** 2)
        rinf  = (a - m) / sigb
        rinf2 = rinf * rinf

        # Direct solar radiation, all length [nwl]
        J1k = physics.calcJ1(-1, m, self.k, self.LAI)
        J2k = physics.calcJ2(0, m, self.k, self.LAI)
        J1K = physics.calcJ1(-1, m, self.K, self.LAI)
        J2K = physics.calcJ2(0, m, self.K, self.LAI)

        e1 = np.exp(-m * self.LAI)
        e2 = e1 ** 2
        re = rinf * e1

        denom = 1.0 - rinf2 * e2

        s1 = sf + rinf * sb
        s2 = sf * rinf + sb
        v1 = self.vf + rinf * self.vb
        v2 = self.vf * rinf + self.vb

        # Length [nwl]
        Pss = s1 * J1k
        Qss = s2 * J2k
        Poo = v1 * J1K
        Qoo = v2 * J2K

        # Scalars
        tau_ss = np.exp(-self.k * self.LAI)
        tau_oo = np.exp(-self.K * self.LAI)

        Z = (1.0 - tau_ss * tau_oo) / (self.K + self.k)

        # These all have length [nwl]
        tau_dd = (1.0 - rinf2) * e1 / denom
        rho_dd = rinf * (1.0 - e2) / denom
        tau_sd = (Pss - re * Qss) / denom
        tau_do = (Poo - re * Qoo) / denom
        rho_sd = (Qss - re * Pss) / denom
        rho_do = (Qoo - re * Poo) / denom

        T1 = v2 * s1 * (Z - J1k * tau_oo) / (self.K + m) + v1 * s2 * (Z -
            J1K * tau_ss) / (self.k + m)
        T2 = -(Qoo * rho_sd + Poo * tau_sd) * rinf

        rho_sod = (T1 + T2) / (1.0 - rinf2)
        rho_sos = self.w * np.sum(self.Pso[0:self.nl]) * self.iLAI
        rho_so  = rho_sod + rho_sos

        Pso2w   = self.Pso[self.nl]

        # Analytical rso following SAIL
        self.rso = rho_so + self.rs * Pso2w + \
                    ((tau_sd + tau_ss * self.rs * rho_dd) * tau_oo + \
                    (tau_sd + tau_ss) * tau_do) * self.rs / denom

        # Extract MODTRAN atmosphere parameters at the SCOPE wavelengths
        t1  = self.atmoM[:, 0]
        t3  = self.atmoM[:, 1]
        t4  = self.atmoM[:, 2]
        t5  = self.atmoM[:, 3]
        t12 = self.atmoM[:, 4]
        t16 = self.atmoM[:, 5]

        # Radiation fluxes, downward and upward (these all have dimenstion
        # [nwl]. First calculate hemispherical reflectances rsd and rdd
        # according to SAIL. These are assumed for the reflectance of the
        # surroundings. rdo is computed with SAIL as well.

        denom = 1.0 - self.rs * rho_dd

        # SAIL analytical reflectances
        self.rsd = rho_sd + (tau_ss + tau_sd) * self.rs * tau_dd / denom
        self.rdd = rho_dd + tau_dd * self.rs * tau_dd / denom
        self.rdo = rho_do + (tau_oo + tau_do) * self.rs * tau_dd / denom

        # Assume Fd of surroundings = 0 for the moment
        # Initial guess of temperature of surroundings from Ta
        Fd = np.zeros((self.nwl,))
        Ls = physics.Planck(self.wl, self.Ta + 273.15)

        # Solar and sky irradiance using 6 atmosperic functions
        self.Esun_ = pi * t1 * t4
        self.Esky_ = pi / (1.0 - t3 * self.rdd) * \
                    (t1 * (t5 + t12 * self.rsd) + Fd + \
                    (1.0 - self.rdd) * Ls * t3 + t16)

        # Fractional contributions of Esun and Esky to total incident radiation
        # in optical and thermal parts of the spectrum
        self.fEsuno = np.zeros((np.size(self.Esun_),))
        self.fEskyo = np.zeros((np.size(self.Esun_),))
        self.fEsunt = np.zeros((np.size(self.Esun_),))
        self.fEskyt = np.zeros((np.size(self.Esun_),))

        # Find optical spectrum
        J_o = self.wl < 3000

        # Optical fluxes, including conversion mW >> W
        Esunto = 0.001 * library.Sint(self.Esun_[J_o], self.wl[J_o]) # Sun
        Eskyto = 0.001 * library.Sint(self.Esky_[J_o], self.wl[J_o]) # Sky
        self.Etoto  = Esunto + Eskyto                                # Total

        # Fraction of contribution of fluxes to total light
        self.fEsuno[J_o] = self.Esun_[J_o] / self.Etoto # Sun fluxes
        self.fEskyo[J_o] = self.Esky_[J_o] / self.Etoto # Sky fluxes

        # Find thermal spectrum
        J_t = self.wl >= 3000

        # Thermal fluxes
        Esuntt = 0.001 * library.Sint(self.Esun_[J_t], self.wl[J_t]) # Sun
        Eskytt = 0.001 * library.Sint(self.Esky_[J_t], self.wl[J_t]) # Sky
        Etott  = Eskytt + Esuntt                                     # Total

        self.fEsunt[J_t] = self.Esun_[J_t] / Etott # Fraction from Esun
        self.fEskyt[J_t] = self.Esky_[J_t] / Etott # Fraction from Esky

        if (self.meteo.Rin != - 999):

            self.Esun_[J_o] = self.fEsuno[J_o] * self.meteo.Rin
            self.Esky_[J_o] = self.fEskyo[J_o] * self.meteo.Rin
            self.Esun_[J_t] = self.fEsunt[J_t] * self.meteo.Rli
            self.Esky_[J_t] = self.fEskyt[J_t] * self.meteo.Rli

        Eplu_1 = self.rs * ((tau_ss + tau_sd) * self.Esun_ + \
                    tau_dd * self.Esky_) / denom
        Eplu0  = rho_sd * self.Esun_ + rho_dd * self.Esky_ + tau_dd * Eplu_1
        Emin_1 = tau_sd * self.Esun_ + tau_dd * self.Esky_ + rho_dd * Eplu_1
        delta1 = self.Esky_ - rinf * Eplu0
        delta2 = Eplu_1 - rinf * Emin_1

        # Calculation of the fluxes in the canopy
        for i in np.arange(0, self.nwl):

            J1kx = physics.calcJ1(self.xl, m[i], self.k, self.LAI) # [nl]
            J2kx = physics.calcJ2(self.xl, m[i], self.k, self.LAI) # [nl]

            F1 = self.Esun_[i] * J1kx * (sf[i] + rinf[i] * sb[i]) + \
                    delta1[i] * np.exp(m[i] * self.LAI * self.xl) # [nl]
            F2 = self.Esun_[i] * J2kx * (sb[i] + rinf[i] * sf[i]) + \
                    delta2[i] * np.exp(-m[i] * self.LAI * (self.xl + 1.0))
                    # [nl]

            self.Emin_[:,i] = (F1 + rinf[i] * F2) / (1 - rinf2[i]) # [nl,nwl]
            self.Eplu_[:,i] = (F2 + rinf[i] * F1) / (1 - rinf2[i]) # [nl,nwl]

        # Incident and absorbed solar radiation

        # Incident solar PAR in PAR units
        self.Psun = 0.001 * library.Sint(physics.e2phot(self.wlPAR * 1e-09, \
                    self.Esun_[self.Ipar]), self.wlPAR)

        # Total absorbed solar radiation
        self.Asun = 0.001 * library.Sint(self.Esun_ * self.epsc, self.wl)

        # Absorbed solar radiation  in PAR range in moles m-2 s-1
        self.Pnsun = 0.001 * library.Sint(physics.e2phot(self.wlPAR * 1e-09, \
                    self.Esun_[self.Ipar] * self.epsc[self.Ipar]), self.wlPAR)

        self.Rnsun_PAR = 0.001 * library.Sint(self.Esun_[self.Ipar] * \
                    self.epsc[self.Ipar], self.wlPAR)

        # Absorbed solar radiation by Cab in PAR range in moles m-2 s-1
        self.Pnsun_Cab = 0.001 * library.Sint(physics.e2phot(self.wlPAR * \
                1e-09, self.kChlrel[self.Ipar] * self.Esun_[self.Ipar] * \
                    self.epsc[self.Ipar]), self.wlPAR)


    def computeOutgoingFluxes(self):
        """
        Compute outgoing fluxes, hemispherical and in viewing direction,
        spectrum.
        """

        # Hemispherical, spectral
        self.Eout_ = self.Eplu_[0,:].T # [nwl]

        # In viewing direction, spectral
        self.piLoc_ = (self.vb * \
            np.inner(self.Emin_[0:self.nl,:].T, self.Po[0:self.nl]) + \
            self.vf * \
            np.inner(self.Eplu_[0:self.nl,:].T, self.Po[0:self.nl]) + \
            self.w * self.Esun_ * sum(self.Pso[0:self.nl])) * self.iLAI

        self.piLos_ = self.rs * \
            np.inner(self.Emin_[self.nl,:].T, self.Po[self.nl]) + \
            self.rs * np.inner(self.Esun_, self.Pso[self.nl])

        self.piLo_  = self.piLoc_ + self.piLos_

        self.Lo_    = self.piLo_ / pi # [nwl]

        # Up and down and hemispherical out, cumulative over wavelength
        # [1] Hemispherical out (W m-2)
        # In optical range
        self.Eouto = 0.001 * library.Sint(self.Eout_[self.IwlP], self.wlP)

        # # In thermal range
        self.Eoutt = 0.001 * library.Sint(self.Eout_[self.IwlT], self.wlT)


    def computeNetFluxes(self, param):
        """
        Compute net fluxes, spectral and total, and incoming fluxes.
        """

        # Incident PAR at the top of canopy, spectral and spectrally integrated
        self.P_ = physics.e2phot(self.wl[self.Ipar] * 1e-09, \
                   (self.Esun_[self.Ipar] + self.Esky_[self.Ipar]))
        self.P  = 0.001 * library.Sint(self.P_, self.wlPAR)

        # Total direct radiation (incident and net) per leaf area (W m-2 leaf)
        self.Pdir      = self.fs * self.Psun        # [13 x 36] Incident
        self.Rndir     = self.fs * self.Asun        # [13 x 36] Net
        self.Pndir     = self.fs * self.Pnsun       # [13 x 36] Net PAR
        self.Pndir_Cab = self.fs * self.Pnsun_Cab   # [13 x 36] Net PAR Cab
        self.Rndir_PAR = self.fs * self.Rnsun_PAR   # [13 x 36] Net PAR energy

        # Canopy layers, diffuse radiation
        for j in np.arange(0,self.nl):

            # Diffuse incident radiation for the present layer 'j'
            # (mW m-2 um-1)
            self.E_ = 0.5 * (self.Emin_[j,:] + self.Emin_[j + 1,:] + \
                        self.Eplu_[j,:] + self.Eplu_[j + 1,:])

            # Incident PAR flux, integrated over all wavelengths
            # (moles m-2 s-1)
            # [nl] Including conversion mW >> W
            self.Pdif[j] = 0.001 * library.Sint(physics.e2phot(self.wlPAR * \
                    1e-09, self.E_[self.Ipar].T), self.wlPAR)

            # Net radiation (mW m-2 um-1) and net PAR (moles m-2 s-1 um-1),
            # per wavelength

            # [nl,nwl] Net (absorbed) radiation by leaves
            self.Rndif_[j,:] = self.E_ * self.epsc.T

            # [nl,nwl] Net (absorbed) as PAR photons
            self.Pndif_[j,:] = 0.001 * (physics.e2phot(self.wlPAR * 1e-09, \
                    np.hstack(self.Rndif_[j, self.Ipar]))).T

            # [nl,nwl] Net (absorbed) as PAR photons by Cab
            self.Pndif_Cab_[j,:] = 0.001 * (physics.e2phot(self.wlPAR * \
                    1e-09, self.kChlrel[self.Ipar] * \
                    np.hstack(self.Rndif_[j, self.Ipar]))).T

            # [nl,nwlPAR] Net (absorbed) as PAR energy
            self.Rndif_PAR_[j,:] = self.Rndif_[j,self.Ipar]

            # Net radiation (W m-2) and net PAR (moles m-2 s-1), integrated
            # over all wavelengths

            # [nl] Full spectrum net diffuse flux
            self.Rndif[j] = 0.001 * library.Sint(self.Rndif_[j,:], self.wl)

            # [nl] Absorbed PAR
            self.Pndif[j] = library.Sint(np.hstack(self.Pndif_[j, \
                    self.Ipar]), self.wlPAR)

            # [nl] Absorbed PAR by Cab integrated
            self.Pndif_Cab[j] = library.Sint(np.hstack(self.Pndif_Cab_[j, \
                    self.Ipar]), self.wlPAR)

            # [nl] Absorbed PAR by Cab integrated
            self.Rndif_PAR[j] = 0.001 * library.Sint(np.hstack( \
                    self.Rndif_PAR_[j, self.Ipar]), self.wlPAR)

        # Soil layer, direct and diffuse radiation

        # [1] Absorbed solar flux by the soil
        self.Rndirsoil = 0.001 * library.Sint(self.Esun_ * self.epss, self.wl)

        # [1] Absorbed diffuse downward flux by the soil (W m-2)
        self.Rndifsoil = 0.001 * library.Sint(self.Emin_[self.nl,:] * \
                    self.epss.T, self.wl)

        # net (n) radiation R and net PAR P per component: sunlit (u), shaded
        # (h) soil(s) and canopy (c)
        # [W m-2 leaf or soil surface um-1]
        # [nl] Shaded leaves or needles
        self.Rnhc     = self.Rndif
        self.Pnhc     = self.Pndif
        self.Pnhc_Cab = self.Pndif_Cab
        self.Rnhc_PAR = self.Rndif_PAR

        # [13,36,nl] Total fluxes on sunlit leaves or needles
        for j in np.arange(0, self.nl):

            self.Puc[:,:,j]      = self.Pdir + self.Pdif[j]
            self.Rnuc[:,:,j]     = self.Rndir + self.Rndif[j]
            self.Pnuc[:,:,j]     = self.Pndir + self.Pndif[j]
            self.Pnuc_Cab[:,:,j] = self.Pndir_Cab + self.Pndif_Cab[j]
            self.Rnuc_PAR[:,:,j] = self.Rndir_PAR + self.Rndif_PAR[j]

        # [1] Shaded soil
        self.Rnhs = self.Rndifsoil
        self.Rnus = self.Rndifsoil + self.Rndirsoil

        if param.options.calc_vert_profiles:

            profile_type = 'angles'

            # [nli,nlo,nl] Mean net radiation sunlit leaves
            self.Pnu1d     = physics.meanleaf(self.canopy, self.Pnuc, \
                    profile_type, self.Ps)
            self.Pnu1d_Cab = physics.meanleaf(self.canopy, self.Pnuc_Cab, \
                    profile_type, self.Ps)

            # [nl] Mean photos leaves, per layer
            self.profiles.Pn1d     = (1.0 - self.Ps[0:self.nl]) * \
                    self.Pnhc + self.Ps[0:self.nl] * self.Pnu1d
            self.profiles.Pn1d_Cab = (1.0 - self.Ps[0:self.nl]) * \
                    self.Pnhc_Cab + self.Ps[0:self.nl] * self.Pnu1d_Cab


    def createOutputStructures(self):
        """
        Fill RTMo output structures
        """

        # Initialize gap output structure
        self.gap     = emptyStruct()

        # Place results in gap output structure
        self.gap.k   = self.k
        self.gap.K   = self.K
        self.gap.Ps  = self.Ps
        self.gap.Po  = self.Po
        self.gap.Pso = self.Pso

        # Initialize rad output structure
        self.rad     = emptyStruct()

        # Place results in rad output structure
        self.rad.rsd     = self.rsd
        self.rad.rdd     = self.rdd
        self.rad.rdo     = self.rdo
        self.rad.rso     = self.rso

        self.rad.vb      = self.vb
        self.rad.vf      = self.vf

        # [2162x1] Incident solar spectrum (mW m-2 um-1)
        self.rad.Esun_   = self.Esun_

        # [2162x1] Incident sky spectrum (mW m-2 um-1)
        self.rad.Esky_   = self.Esky_

        # [1] Incident spectrally integrated PAR (moles m-2 s-1)
        self.rad.inPAR   = self.P

        # [2162x1] Normalized spectrum of direct light (optical)
        self.rad.fEsuno  = self.fEsuno

        # [2162x1] Normalized spectrum of diffuse light (optical)
        self.rad.fEskyo  = self.fEskyo

        # [2162x1] Normalized spectrum of direct light (thermal)
        self.rad.fEsunt  = self.fEsunt

        # [2162x1] Normalized spectrum of diffuse light (thermal)
        self.rad.fEskyt  = self.fEskyt

        # [61x2162] Upward diffuse radiation in the canopy (mW m-2 um-1)
        self.rad.Eplu_   = self.Eplu_

        # [61x2162] Downward diffuse radiation in the canopy (mW m-2 um-1)
        self.rad.Emin_   = self.Emin_

        # [2162x1] TOC radiance in observation direction (mW m-2 um-1 sr-1)
        self.rad.Lo_     = self.Lo_

        # [2162x1] TOC upward radiation (mW m-2 um-1)
        self.rad.Eout_   = self.Eout_

        # [1] TOC spectrally integrated upward optical ratiation (W m-2)
        self.rad.Eouto   = self.Eouto

        # [1] TOC spectrally integrated upward thermal ratiation (W m-2)
        self.rad.Eoutt   = self.Eoutt

        # [1] Net radiation (W m-2) of shaded soil
        self.rad.Rnhs    = self.Rnhs

        # [1] Net radiation (W m-2) of sunlit soil
        self.rad.Rnus    = self.Rnus

        # [60x1] Net radiation (W m-2) of shaded leaves
        self.rad.Rnhc    = self.Rnhc

        # [13x36x60] Net radiation (W m-2) of sunlit leaves
        self.rad.Rnuc    = self.Rnuc

        # [60x1] Net PAR (moles m-2 s-1) of shaded leaves
        self.rad.Pnh     = self.Pnhc

        # [13x36x60] Net PAR (moles m-2 s-1) of sunlit leaves
        self.rad.Pnu     = self.Pnuc

        # [60x1] Net PAR absorbed by Cab (moles m-2 s-1) of shaded leaves
        self.rad.Pnh_Cab = self.Pnhc_Cab

        # [13x36x60] Net PAR absorbed by Cab (moles m-2 s-1) of sunlit leaves
        self.rad.Pnu_Cab = self.Pnuc_Cab

        # [60x1] Net PAR absorbed by Cab (moles m-2 s-1) of shaded leaves
        self.rad.Rnh_PAR = self.Rnhc_PAR

        # [13x36x60] Net PAR absorbed (W m-2) of sunlit leaves
        self.rad.Rnu_PAR = self.Rnuc_PAR

        self.rad.Etoto   = self.Etoto


    def writeOutput(self, param):
        """
        Write output from RTMo module to file.
        """

        # Specify output directory
        output_dir = library.create_output_dir(param, 'rtmo')

        # Specify time step
        step       = str(param.xyt.k)

        # Output gap to pickle file
        gap_file   = output_dir + "/" + "gap" + step + ".pkl"
        library.write_pickle(gap_file, self.gap)

        # Output rad to pickle file
        rad_file   = output_dir + "/" + "rad" + step + ".pkl"
        library.write_pickle(rad_file, self.rad)

        # Output profile vector fields to pickle file
        if param.options.calc_vert_profiles:

            profiles_file = output_dir + "/" + "profiles" + step + ".pkl"
            library.write_pickle(profiles_file, self.profiles)


# EOF rtmo.py