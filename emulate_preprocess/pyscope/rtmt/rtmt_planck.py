#!/usr/bin/env python

###############################################################################
# Script rtmt_planck.py
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
#   Symbol      Description                 Unit            Dimension
#   ------      -----------                 ----            ---------
#   Tcu         temperature sunlit leaves   C               [13,36,nl]
#   Tch         temperature shaded leaves   C               [nl]
#   Tsu         temperature sunlit soil     C               [1]
#   Tsu         temperature shaded soil     C               [1]
#   rad         a structure containing
#   soil        a structure containing soil reflectance
#   canopy      a structure containing LAI and leaf inclination

#   Ps          probability of sunlit leaves                [nl+1]
#   Po          probability of viewing a leaf or soil       [nl+1]
#   Pso         probability of viewing a sunlit leaf/soil   [nl+1]
#   K           extinction coefficient in viewing dir       [1]
#   tto         viewing angle               (degrees)       [1]
#   psi         azimuth angle difference between solar and viewing position
#
# Output
#   Symbol      Description                             Unit        Dimension
#   ------      -----------                             ----        ---------
#   Loutt_      Spectrum of outgoing hemispherical rad  (W m-2 um-1)[nwl]
#   Lot_        Spectrum of outgoing rad in viewing dir (W m-2 um-1)[nwl]
#   Eplu        Total downward diffuse radiation        (W m-2)     [nl+1]
#   Emin        Total downward diffuse radiation        (W m-2)     [nl+1]
#
# Notes:
#   nl      number of layers
#   nwl     number of wavelengths of input (net PAR)
# '_'means: a flux at different wavelengths (a vertically oriented vector)


import  numpy                           as np
from    scipy                           import integrate
from    math                            import *
import  os

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics


class RTMt_planck():
    """
    Calculates the spectrum of outgoing thermal radiation in hemispherical and
    viewing direction
    """

    def __init__(self, param, leafopt, gap, rad, thermal):
        """
        Prepare input parameters and initialize arrays.
        """

        # Load parameters
        self.param   = param
        self.leafopt = leafopt
        self.gap     = gap
        self.rad     = rad
        self.thermal = thermal

        # For speedup the calculation only uses thermal part of the spectrum
        self.IT      = param.spectral.IwlT
        self.wlt     = param.spectral.wlT

        self.deg2rad = const.deg2rad
        self.nl      = param.canopy.nlayers
        self.lidf    = param.canopy.lidf
        self.litab   = np.hstack(param.canopy.litab)
        self.lazitab = param.canopy.lazitab
        self.nlazi   = np.size(self.lazitab)
        self.tto     = param.angles.tto
        self.psi     = param.angles.psi
        self.Ps      = gap.Ps
        self.Po      = gap.Po
        self.Pso     = gap.Pso
        self.K       = gap.K

        # Length [nwl]
        self.rho     = leafopt.refl[self.IT]     # Leaf/needle reflection
        self.tau     = leafopt.trans[self.IT]    # Leaf/needle transmission
        self.rs      = param.soil.refl[self.IT]  # Soil reflectance
        self.epsc    = 1.0 - self.rho - self.tau # Emissivity vegetation
        self.epss    = 1.0 - self.rs             # Emissivity soil

        self.crit    = 0.01                      # Desired minimum accuracy
        self.LAI     = param.canopy.LAI
        self.dx      = 1.0 / self.nl
        self.iLAI    = self.LAI * self.dx

        # Temperatures
        self.Tcu     = thermal.Tcu
        self.Tch     = thermal.Tch
        self.Tsu     = thermal.Ts[1]
        self.Tsh     = thermal.Ts[0]

        self.obsdir  = 1

        # Initialization of output variables
        self.Hcsui   = np.zeros((self.nl,))                      # [nl]
        self.piLot_  = np.zeros((np.size(self.IT),))             # [1,nwlt]
        self.Emin_   = np.zeros((self.nl + 1,np.size(self.IT)))  # [nl+1,nwlt]
        self.Eplu_   = np.zeros((self.nl + 1,np.size(self.IT)))  # [nl+1,nwlt]


    def computeGeometric(self):
        """
        Compute geometric quantities used for fluxes.
        """

        # Geometric factors of observer
        if (self.obsdir):

            # [1] Cos observation angle
            self.cos_tto = np.cos(self.tto * self.deg2rad)

            # [1] Sin observation angle
            self.sin_tto = np.sin(self.tto * self.deg2rad)


        # Geometric factors associated with extinction and scattering

        # [nli] Cos leaf inclination angles
        self.cos_ttl = np.cos(self.litab * self.deg2rad)

        if self.obsdir:

            # [nli] Sin leaf inclination angles
            self.sin_ttl  = np.sin(self.litab * self.deg2rad)

            # [nlazi] Cos leaf orientation angles
            self.cos_ttlo = np.cos((self.lazitab - self.psi) * self.deg2rad)

        self.bfli = self.cos_ttl ** 2                   # [nli]
        self.bf   = np.inner(self.bfli, self.lidf)      # [1]

        # [1] Geometric factors to be used later with rho and tau, f1 f2
        # of pag 304
        self.ddb = 0.5 * (1.0 + self.bf)    # W of dif2dif back (f1^2 + f2^2)
        self.ddf = 0.5 * (1.0 - self.bf)    # W of dif2dif forward (2*f1*f2)

        if self.obsdir:

            self.dob = 0.5 * (self.K + self.bf)  # W of dif2dir back (fo*f1)
            self.dof = 0.5 * (self.K - self.bf)  # W of dif2dir back (fo*f1)

        # Factor fo for all leaf angle/azumith classes
        if self.obsdir:

            self.Co         = self.cos_ttl * self.cos_tto   # [nli] pag 305
            self.So         = self.sin_ttl * self.sin_tto   # [nli] pag 305

            # [nli, nlazi] Projection of leaves in direction of sun
            # (pag 125-126)
            self.cos_deltao = np.outer(self.Co, np.ones((self.nlazi)).T) + \
                              np.outer(self.So, self.cos_ttlo)

            # [nli, nlazi] Leaf area projection factors in direction of
            # observation
            self.fo         = self.cos_deltao / np.abs(self.cos_tto)


    def computeUpDownFluxes(self):
        """
        Compute upward and downward fluxes.
        """

        # Calculation of upward and downward fluxes

        # [nwlt] Diffuse backscatter scattering coefficient for diffuse
        # incidence, pag 305
        self.sigb    = self.ddb * self.rho + self.ddf * self.tau

        # [nwlt] Diffuse forward scattering coefficient for forward incidence
        self.sigf    = self.ddf * self.rho + self.ddb * self.tau

        if self.obsdir:

            # [nwlt] Directional backscatter scattering coefficient for
            # diffuse  incidence
            self.vb = self.dob * self.rho + self.dof * self.tau

            # [nwlt] Directional forward scattering coefficient for diffuse
            # incidence
            self.vf = self.dof * self.rho + self.dob * self.tau

        self.a       = 1.0 - self.sigf                 # [nwlt] Attenuation
        self.m       = np.sqrt(self.a ** 2 - self.sigb ** 2)    # [nwlt]

        # [nwlt] Reflection coefficient for infinite thick canopy
        self.rinf    = (self.a - self.m) / self.sigb

        self.rinf2   = self.rinf * self.rinf                    # [nwlt]

        self.fHs     = (1.0 - self.rinf2) * (1.0 - self.rs) \
                        / (1.0 - self.rinf * self.rs)
        self.fHc     = self.iLAI * self.m * (1.0 - self.rinf)
        self.fbottom = (self.rs - self.rinf) / (1.0 - self.rinf * self.rs)


        for i in np.arange(0, np.size(self.IT)):

            # Radiance by components
            self.Hcsui3 = physics.Planck(self.wlt[i], self.Tcu + 273.15,  \
                                         self.epsc[i])
            self.Hcshi  = physics.Planck(self.wlt[i], self.Tch + 273.15,  \
                                         self.epsc[i])
            self.Hssui  = physics.Planck(self.wlt[i], self.Tsu + 273.15, \
                                         self.epss[i])
            self.Hsshi  = physics.Planck(self.wlt[i], self.Tsh + 273.15, \
                                         self.epss[i])

            # Radiance by leaf layers Hc and by soil Hs
            for j in np.arange(0, self.nl):

                # [nli,nlazi] Sunlit leaves
                self.Hcsui2   = self.Hcsui3[:,:,j]

                # [nl] Sunlit vegetation radiance per layer
                self.Hcsui[j] = np.mean(np.inner(self.Hcsui2.T, self.lidf))

            # [nl] Emitted vegetation radiance per layer
            self.Hci = self.Hcsui * self.Ps[0:self.nl] + \
                        self.Hcshi * (1.0 - self.Ps[0:self.nl])

            # [1] Emitted soil radiance per layer
            self.Hsi = self.Hssui * self.Ps[self.nl] + \
                        self.Hsshi * (1.0 - self.Ps[self.nl])

            # Diffuse radiation
            cont       = 1              # [1] Continue iteration (1:yes, 0:no)
            counter    = 0              # [1] Iteration counter

            self.F1    = np.zeros((self.nl + 1,))           # [nl+1]
            self.F2    = np.zeros((self.nl + 1,))           # [nl+1]
            self.F1top = 0                                  # [1]

            while cont:

                self.F1topn = -self.rinf[i] * self.F2[1]
                self.F1[1]  = self.F1topn

                for j in np.arange(0, self.nl):
                    self.F1[j+1] = self.F1[j] * (1.0 - self.m[i] * \
                                   self.iLAI) + self.fHc[i] * self.Hci[j]

                self.F2[self.nl] = self.fbottom[i] * self.F1[self.nl] + \
                                   self.fHs[i] * self.Hsi

                for j in np.arange(self.nl-1, -1, -1):
                    self.F2[j] = self.F2[j+1] * (1.0 - self.m[i] * \
                                 self.iLAI) + self.fHc[i] * self.Hci[j]

                # [1] Check to continue
                cont       = abs(self.F1topn - self.F1top) > self.crit

                self.F1top = self.F1topn             # [1]  Reset F1topn
                counter    = counter + 1

            self.Emini = (self.F1 + self.rinf[i] * self.F2) / \
                         (1.0 - self.rinf2[i])
            self.Eplui = (self.F2 + self.rinf[i] * self.F1) / \
                         (1.0 - self.rinf2[i])

            # Downwelling diffuse radiance per layer
            self.Emin_[:,i] = self.Emini

            # Upwelling diffuse radiance
            self.Eplu_[:,i] = self.Eplui

            # Directional radiation
            if self.obsdir:

                for j in np.arange(0, self.nl):
                    self.Hcsui2   = self.Hcsui3[:,:,j] * abs(self.fo)
                    self.Hcsui[j] = np.mean(np.inner(self.Hcsui2.T, self.lidf))

                # Directional emitted radiation by shaded leaves
                self.piLo1     = self.iLAI * self.epsc[i] * self.K * \
                                 np.sum( self.Hcshi * (self.Po[0:self.nl] - \
                                                       self.Pso[0:self.nl]) )

                # Directional emitted radiation by sunlit leaves
                self.piLo2     = self.iLAI * self.epsc[i] * \
                                 np.sum(self.Hcsui * (self.Pso[0:self.nl]))

                # Directional scattered radiation by vegetation for diffuse
                # incidence
                self.piLo3     = self.iLAI * (np.inner( \
                                 (self.vb[i] * self.Emini[0:self.nl] + \
                                  self.vf[i] * self.Eplui[0:self.nl]).T, \
                                 self.Po[0:self.nl]))

                self.piLo4     = self.epss[i] * self.Hsshi * \
                                 (self.Po[self.nl] - self.Pso[self.nl])

                # Directional emitted radiation by sunlit/shaded soil
                self.piLo5     = self.epss[i] * self.Hssui * self.Pso[self.nl]

                # Directional scattered radiation by soil for diffuse incidence
                self.piLo6     = self.rs[i] * self.Emini[self.nl] * \
                                 self.Po[self.nl]

                # Directional total radiation
                self.piLot_[i] = self.piLo1 + np.sum(self.piLo2) + \
                                 self.piLo3 + self.piLo4 + self.piLo5 + \
                                 self.piLo6

                self.Lot_      = self.piLot_ / pi


    def createOutputStructures(self):
        """
        Fill RTMt_planck output structures
        """

        self.rad.Lot_        = np.zeros((np.size(self.param.spectral.wlS),))
        self.rad.Eoutte_     = np.zeros((np.size(self.param.spectral.wlS),))

        # Put output in the rad structure

        self.rad.Lot_[self.IT]    = self.Lot_

        # Emitted diffuse radiance at top
        self.rad.Eoutte_[self.IT] = self.Eplu_[0,:]

        self.rad.Eplut_      = self.Eplu_
        self.rad.Emint_      = self.Emin_


    def writeOutput(self, param):
        """
        Write output from RTMt_planck module to file.
        """

        # Specify output directory
        output_dir = library.create_output_dir(param, 'rtmt')

        # Specify time step
        step       = str(param.xyt.k)

        # Output rad to pickle file
        rad_file   = output_dir + "/" + "rad" + step + ".pkl"
        library.write_pickle(rad_file, self.rad)


# EOF rtmt_planck.py