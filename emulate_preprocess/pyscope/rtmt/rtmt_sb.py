#!/usr/bin/env python

###############################################################################
# Script rtmt_sb.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: equivalent of RTMt_sb module in SCOPE
# Note: this script corresponds to RTMt_sb.m in SCOPE.
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
#   options     calculation options
#   spectral    information about wavelengths and resolutions
#   rad         a large number of radiative fluxes: spectrally distributed
#               and integrated, and canopy radiative transfer coefficients
#   soil        soil properties
#   leafopt     leaf optical properties
#   canopy      canopy properties (such as LAI and height)
#   gap         probabilities of direct light penetration and viewing
#   angles      viewing and observation angles
#   Tcu         Temperature of sunlit leaves    (oC), [13x36x60]
#   Tch         Temperature of shaded leaves    (oC), [13x36x60]
#   Tsu         Temperature of sunlit soil      (oC), [1]
#   Tsh         Temperature of shaded soil      (oC), [1]
#
# Output:
#   rad         a large number of radiative fluxes: spectrally distributed
#               and integrated, and canopy radiative transfer coefficients.
#               Here, thermal fluxes are added


import  numpy                           as np
from    scipy                           import integrate
from    math                            import *
import  os

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics


class RTMt_sb():
    """
    Calculates the spectra of hemisperical and directional observed visible
    and thermal radiation (fluxes E and radiances L), as well as the single
    and bi-directional gap probabilities.
    """

    def __init__(self, param, leafopt, rad, gap, T_struct, obsdir):
        """
        Prepare input parameters and initialize arrays.
        """

        # Load parameters

        self.rad = rad

        # Extract parameters from input arguments
        self.Tcu     = T_struct[0]
        self.Tch     = T_struct[1]
        self.Tsu     = T_struct[2]
        self.Tsh     = T_struct[3]
        self.obsdir  = obsdir

        # Take 10 microns as representative wavelength for the thermal
        self.IT      = (param.spectral.wlS == 10000).nonzero()[0][0]

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

        self.rho     = leafopt.refl[self.IT]     # [nwl] Leaf/needle reflection
        self.tau     = leafopt.trans[self.IT]  # [nwl] Leaf/needle transmission

        self.rs      = param.soil.refl[self.IT]  # [nwl] Soil reflectance

        self.epsc    = 1.0 - self.rho - self.tau # [nwl] Emissivity vegetation
        self.epss    = 1.0 - self.rs             # [nwl] Emissivity soil
        self.crit    = 1.0e-2                    # [1] Desired minimum accuracy

        self.LAI     = param.canopy.LAI
        self.dx      = 1.0 / self.nl
        self.iLAI    = self.LAI * self.dx

        # Initializations
        self.Rnhc    = np.zeros((self.nl,))             # [nl]
        self.Rnuc    = np.zeros((np.shape(self.Tcu)))   # [13,36,nl]


    def computeGeometric(self):
        """
        Compute geometric quantities used for fluxes.
        """

        # Geometric factors of observer
        if (self.obsdir):

            # [1] cos observation angle
            self.cos_tto = np.cos(self.tto * self.deg2rad)

            # [1] sin observation angle
            self.sin_tto = np.sin(self.tto * self.deg2rad)

        self.cos_ttl = np.cos(self.litab * self.deg2rad)

        # Geometric factors associated with extinction and scattering
        if self.obsdir:

            self.sin_ttl  = np.sin(self.litab * self.deg2rad)
            self.cos_ttlo = np.cos((self.lazitab - self.psi) * self.deg2rad)

        self.bfli = self.cos_ttl ** 2
        self.bf   = np.inner(self.bfli, self.lidf)

        # Geometric factors to be used later with rho and tau, f1 f2
        # of pag 304
        self.ddb = 0.5 * (1.0 + self.bf)            # f1^2 + f2^2
        self.ddf = 0.5 * (1.0 - self.bf)            # 2*f1*f2

        if self.obsdir:

            self.dob = 0.5 * (self.K + self.bf)     # fo*f1
            self.dof = 0.5 * (self.K - self.bf)     # fo*f1

        # Factor fo for all leaf angle/azumith classes
        if self.obsdir:

            self.Co         = self.cos_ttl * self.cos_tto   # [nli] pag 305
            self.So         = self.sin_ttl * self.sin_tto   # [nli] pag 305

            # [nli, nlazi] Projection of leaves in  in direction of sun
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

        # Calculation of upward and downward fluxes pag 305

        # [nwlt] Diffuse scattering coefficient
        self.sigb = self.ddb * self.rho + self.ddf * self.tau # Backscatter
        self.sigf = self.ddf * self.rho + self.ddb * self.tau # Forward scatter

        if self.obsdir:

            # [nwlt] Directional scattering coefficient for diffuse  incidence
            self.vb = self.dob * self.rho + self.dof * self.tau # Backscatter
            self.vf = self.dof * self.rho + self.dob * self.tau # Forward

        self.a       = 1.0 - self.sigf          # [nwlt] Attenuation
        self.m       = np.sqrt(self.a * self.a - self.sigb * self.sigb)

        # [nwlt] Reflection coefficient for infinite thick canopy
        self.rinf    = (self.a - self.m) / self.sigb
        self.rinf2   = self.rinf * self.rinf

        self.fHs     = (1.0 - self.rinf2) * (1.0 - self.rs) / \
                       (1.0 - self.rinf * self.rs)
        self.fHc     = self.iLAI * self.m * (1.0 - self.rinf)
        self.fbottom = (self.rs - self.rinf) / (1.0 - self.rs * self.rinf)

        # Radiance by components
        self.Hcsu3 = physics.Stefan_Boltzmann(self.Tcu)  # By sunlit leaves
        self.Hcsh  = physics.Stefan_Boltzmann(self.Tch)  # By shaded leaves
        self.Hssu  = physics.Stefan_Boltzmann(self.Tsu)  # By sunlit soil
        self.Hssh  = physics.Stefan_Boltzmann(self.Tsh)  # By shaded soil

        # Radiance by leaf layers Hv and by soil Hs (modified by JAK 2015-01)

        # Vector for computing the mean
        self.v1 = np.kron(np.ones((np.shape(self.Hcsu3)[1],)).T, \
                          1.0 / np.shape(self.Hcsu3)[1])

        # Create a block matrix from the 3D array
        self.Hcsu2 = self.Hcsu3.reshape(np.shape(self.Hcsu3)[0], -1)

        # Compute column means for each level
        a = np.inner(self.Hcsu2.T, self.lidf).reshape(np.shape\
                    (self.Hcsu3) [1],-1).T
        self.Hcsu = np.inner(self.v1, a)

        # Hemispherical emittance
        self.Hc   = self.Hcsu * (self.Ps[0:self.nl]) + \
                    self.Hcsh * (1.0 - self.Ps[0:self.nl])  # by leaf layers
        self.Hs   = self.Hssu * (self.Ps[self.nl]) + \
                    self.Hssh * (1.0 - self.Ps[self.nl])    # by soil surface

        # Diffuse radiation
        cont    = 1             # Continue iteration (1:yes, 0:no)
        counter = 0             # Number of iterations
        F1      = np.zeros((self.nl + 1,))
        F2      = np.zeros((self.nl + 1,))
        F1top   = 0

        while cont:

            F1topn = - self.rinf * F2[0]
            F1[0]  = F1topn

            for j in np.arange(0, self.nl):

                F1[j + 1] = F1[j] * (1.0 - self.m * self.iLAI) + \
                            self.fHc * self.Hc[j]

            F2[self.nl] = self.fbottom * F1[self.nl] + self.fHs * self.Hs

            for j in np.arange(self.nl-1,-1,-1):

                F2[j] = F2[j + 1] * (1.0 - self.m * self.iLAI) + \
                        self.fHc * self.Hc[j]

            cont    = np.abs(F1topn - F1top) > self.crit
            F1top   = F1topn
            counter = counter + 1

        self.Emin = (F1 + self.rinf * F2) / (1.0 - self.rinf2)
        self.Eplu = (F2 + self.rinf * F1) / (1.0 - self.rinf2)

        # Directional radiation
        if self.obsdir:

            # Directional emitted radation by shaded leaves
            self.piLo1 = self.iLAI * self.epsc * self.K * \
                         np.inner(self.Hcsh.T, (self.Po[0:self.nl] - \
                                                self.Pso[0:self.nl]))

            # JAK 2015-01: replaced earlier loop by this:
            # all-at-once with more efficient mean
            self.absfo_rep = np.kron(np.ones((self.nl)).T, np.abs(self.fo))

            # Compute column means for each level
            b = np.inner((self.Hcsu2 * self.absfo_rep).T, self.lidf)
            self.piLo2 = self.iLAI * self.epsc * \
                        np.inner( b.reshape(np.shape(self.Hcsu3)[1], -1).T, \
                        self.v1).T * self.Pso[0:self.nl]

            # Directional scattered radiation by vegetation for diffuse
            # incidence
            self.piLo3 = self.iLAI * np.inner(\
                (self.vb * self.Emin[0:self.nl] + \
                 self.vf * self.Eplu[0:self.nl]).T, self.Po[0:self.nl])

            # Directional emitted radiation by shaded soil
            self.piLo4 = self.epss * self.Hssh * \
                (self.Po[self.nl] - self.Pso[self.nl])

            # Directional emitted radiation by sunlit soil
            self.piLo5 = self.epss * self.Hssu * self.Pso[self.nl]

            # Directional scattered radiation by soil for diffuse incidence [1]
            self.piLo6 = self.rs * self.Emin[self.nl] * self.Po[self.nl]
            self.piLot = self.piLo1 + np.sum(self.piLo2) + self.piLo3 + \
                         self.piLo4 + self.piLo5 + self.piLo6

        else:

            self.piLot = np.nan

        self.Lot = self.piLot / pi


    def computeNetFluxes(self):
        """
        Compute net fluxes, spectral and total, and incoming fluxes.
        """

        # Net radiation per component, in W m-2 (leaf or soil surface)
        for j in np.arange(0, self.nl):

            self.Rnuc[:,:,j] = (self.Emin[j] + self.Eplu[j + 1] - \
                2.0 * self.Hcsu3[:,:,j]) * self.epsc
            self.Rnhc[j]     = (self.Emin[j] + self.Eplu[j + 1] - \
                2.0 * self.Hcsh[j]) * self.epsc

        self.Rnus = (self.Emin[self.nl] - self.Hssu) * self.epss # Sunlit soil
        self.Rnhs = (self.Emin[self.nl] - self.Hssh) * self.epss # Shaded soil


    def createOutputStructures(self):
        """
        Fill RTMt_sb output structures
        """

        # Put output in the rad structure
        self.rad.Emint  = self.Emin
        self.rad.Eplut  = self.Eplu
        self.rad.Eoutte = self.Eplu[0]
        self.rad.Lot    = self.Lot
        self.rad.Rnuct  = self.Rnuc
        self.rad.Rnhct  = self.Rnhc
        self.rad.Rnust  = self.Rnus
        self.rad.Rnhst  = self.Rnhs


    def writeOutput(self, param):
        """
        Write output from RTMt_sb module to file.
        """

        # Specify output directory
        output_dir = library.create_output_dir(param, 'rtmt')

        # Specify time step
        step       = str(param.xyt.k)

        # Write output fields: do we want this? Gets produced in each ebal
        # iteration. Maybe not so useful?


# EOF rtmt_sb.py