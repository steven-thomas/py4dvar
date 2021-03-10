#!/usr/bin/env python

###############################################################################
# Script rtmf.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: equivalent of RTMf module in SCOPE
# Note: this script corresponds to rtmf.m in SCOPE.
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
#   rad         a large number of radiative fluxes: spectrally distributed
#               and integrated, and canopy radiative transfer coefficients
#   soil        soil properties
#   leafopt     leaf optical properties
#   canopy      canopy properties (such as LAI and height)
#   gap         probabilities of direct light penetration and viewing
#   angles      viewing and observation angles
#   profiles    vertical profiles of fluxes
#
# Output:
#   rad         a large number of radiative fluxes: spectrally distributed
#               and integrated, and canopy radiative transfer coefficients.
#               Here, fluorescence fluxes are added


import  numpy                           as np
from    scipy                           import integrate
from    math                            import *
import  os

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics


class RTMf():
    """
    Calculates the spectrum of fluorescent radiance in the observer's direction
    in addition to the total TOC spectral hemispherical upward Fs flux
    """

    def __init__(self, param, leafopt, gap, rad, profiles):
        """
        Prepare input parameters and initialize arrays.
        """

        # Load parameters

        self.param        = param
        self.leafopt      = leafopt
        self.gap          = gap
        self.rad          = rad

        # Profiles
        self.profiles     = profiles

        if (self.param.options.calc_ebal == 0):

            self.profiles.etah = np.ones((60, ))
            self.profiles.etau = np.ones((13, 36, 60))


        # SCOPE wavelengths, make column vectors
        self.wlS          = param.spectral.wlS.T
        self.wlF          = param.spectral.wlF.T            # Fluorescence
        self.wlE          = param.spectral.wlE.T            # Excitation

        # Find indices of intersections
        self.iwlfi        = np.hstack(np.in1d(self.wlS, self.wlE).nonzero())
        self.iwlfo        = np.hstack(np.in1d(self.wlS, self.wlF).nonzero())

        self.nf           = np.size(self.iwlfo)
        self.ne           = np.size(self.iwlfi)

        self.nl           = param.canopy.nlayers
        self.LAI          = param.canopy.LAI
        self.litab        = np.hstack(param.canopy.litab)
        self.lazitab      = param.canopy.lazitab
        self.lidf         = param.canopy.lidf

        self.nlinc        = np.size(self.litab)
        self.nlazi        = np.size(self.lazitab)

        # Total number of leaf orientations
        self.nlori        = self.nlinc * self.nlazi
        self.layers       = np.arange(0, self.nl)

        # Added for rescattering of SIF fluxes
        self.vb           = rad.vb[self.iwlfo]
        self.vf           = rad.vf[self.iwlfo]

        self.Ps           = gap.Ps                          # [nl+1]
        self.Po           = gap.Po
        self.Pso          = gap.Pso

        self.Qso          = (self.Pso[self.layers] + \
                            self.Pso[self.layers + 1]) / 2.0
        self.Qs           = (self.Ps[self.layers] + \
                            self.Ps[self.layers + 1]) / 2.0
        self.Qo           = (self.Po[self.layers] + \
                            self.Po[self.layers + 1]) / 2.0
        self.Qsho         = self.Qo - self.Qso

        # For speedup the calculation only uses wavelength i and wavelength o
        # part of the spectrum

        self.Esunf_       = rad.Esun_[self.iwlfi]

        # transpose into [nf,nl+1] matrix
        self.Eminf_       = rad.Emin_[:, self.iwlfi].T
        self.Epluf_       = rad.Eplu_[:, self.iwlfi].T
        self.iLAI         = float(self.LAI) / float(self.nl)  # LAI of a layer

        # Optical quantities

        # [nf] Leaf/needle reflectance
        self.rho          = leafopt.refl[self.iwlfo]

        # [nf] Leaf/needle transmittance
        self.tau          = leafopt.trans[self.iwlfo]

        self.MbI          = leafopt.MbI
        self.MbII         = leafopt.MbII
        self.MfI          = leafopt.MfI
        self.MfII         = leafopt.MfII

        # [nf] Soil reflectance
        self.rs           = self.param.soil.refl[self.param.spectral.IwlF]

        # Initializations

        self.etah         = np.zeros((self.nl,))

        # Modified dimensions to facilitate vectorization
        self.etau         = np.zeros((self.nl, self.nlori))

        self.Mb           = np.zeros((self.nf, self.ne))
        self.Mf           = np.zeros((self.nf, self.ne))

        self.LoF_         = np.zeros((self.nf, 2))
        self.Fhem_        = np.zeros((self.nf, 2))
        self.Fiprofile    = np.zeros((self.nl + 1, 2))


    def computeGeometric(self):
        """
        Compute geometric quantities used for fluorescence.
        """

        # Geometric factors
        self.deg2rad   = const.deg2rad
        self.tto       = self.param.angles.tto
        self.tts       = self.param.angles.tts
        self.psi       = self.param.angles.psi

        self.cos_tto   = np.cos(self.tto * self.deg2rad)        # [nlinc]
        self.sin_tto   = np.sin(self.tto * self.deg2rad)        # [nlinc]
        self.cos_tts   = np.cos(self.tts * self.deg2rad)        # [nlinc]
        self.sin_tts   = np.sin(self.tts * self.deg2rad)        # [nlinc]
        self.cos_ttli  = np.cos(self.litab * self.deg2rad)      # [nlinc]
        self.sin_ttli  = np.sin(self.litab * self.deg2rad)      # [nlinc]

        self.cos_phils = np.cos(self.lazitab * self.deg2rad)    # [nlazi]
        self.cos_philo = np.cos((self.lazitab - self.psi) * self.deg2rad)
                                                                # [nlazi]

        # [nlinc,nlazi] Geometric factors for all leaf angle/azimuth classes
        self.cds     = np.outer( (self.cos_ttli * self.cos_tts), \
                                  np.ones((self.nlazi,)) ) + \
                       np.outer( (self.sin_ttli * self.sin_tts), \
                                  self.cos_phils )

        self.cdo     = np.outer( (self.cos_ttli * self.cos_tto), \
                                  np.ones((self.nlazi,)) ) + \
                       np.outer( (self.sin_ttli * self.sin_tto), \
                                  self.cos_philo )

        self.fs      = self.cds / self.cos_tts
        self.absfs   = np.abs(self.fs)
        self.fo      = self.cdo / self.cos_tto
        self.absfo   = np.abs(self.fo)
        self.fsfo    = self.fs * self.fo
        self.absfsfo = np.abs(self.fsfo)
        self.foctl   = self.fo * \
                       np.outer( self.cos_ttli, np.ones((self.nlazi,)) )
        self.fsctl   = self.fs * \
                       np.outer( self.cos_ttli, np.ones((self.nlazi,)) )
        self.ctl2    = np.outer( self.cos_ttli ** 2, np.ones((self.nlazi,)) )


    def computeFluorescence(self):
        """
        Compute fluorescence in observation direction
        """

        # Fluorescence efficiencies from ebal, after default fqe has been
        # applied

        self.etahi   = self.profiles.etah

        # Make dimensions [nl,nlinc,nlazi]
        self.etaur   = np.transpose(self.profiles.etau, (2, 0, 1))

        # Expand orientations in a vector >> [nl,nlori]
        self.etaui   = self.etaur.reshape(self.nl, self.nlori)

        # Fluorescence matrices and efficiencies for PSI and PSII
        self.Emin_   = np.zeros((self.nl + 1, self.nf))
        self.Eplu_   = np.zeros((self.nl + 1, self.nf))

        # Do for both photosystems II and I
        for PS in np.arange(1, -1, -1):

            if (PS == 0):

                self.Mb      = self.MbI
                self.Mf      = self.MfI
                self.etah[:] = 1.0
                self.etau[:] = 1.0

            elif (PS == 1):

                self.Mb      = self.MbII
                self.Mf      = self.MfII
                self.etah[:] = self.etahi[:]
                self.etau[:] = self.etaui[:]

            # [nf,ne]
            self.Mplu = 0.5 * (self.Mb + self.Mf)
            self.Mmin = 0.5 * (self.Mb - self.Mf)

            # Inner products: we convert incoming radiation to a fluorescence
            # spectrum using the matrices.
            # Resolution assumed is 1 nm

            # [nf,nl+1]  = (nf,ne) * (ne,nl+1)
            # [351, 61]  = [351, 211] * [211, 61]
            self.MpluEmin = np.dot(self.Mplu, self.Eminf_)
            self.MpluEplu = np.dot(self.Mplu, self.Epluf_)
            self.MminEmin = np.dot(self.Mmin, self.Eminf_)
            self.MminEplu = np.dot(self.Mmin, self.Epluf_)

            # Integration by inner product
            self.MpluEsun = np.dot(self.Mplu, self.Esunf_)
            self.MminEsun = np.dot(self.Mmin, self.Esunf_)

            # lidf-weighted cosine squared of leaf inclination
            self.xdd2     = np.mean(np.inner(self.ctl2.T, self.lidf), axis = 0)

            # lidf-weighted mean of etau per layer [nl]
            self.mn_etau  = np.inner( np.mean(  self.etau.reshape(self.nl, \
                                                                 self.nlinc, \
                                                                 self.nlazi), \
                                                axis = 2 ), \
                                      self.lidf )

            # We calculate the spectrum for all individual leaves, sunlit and
            # shaded

            self.Fmin     = np.zeros((self.nf, self.nl + 1))
            self.Fplu     = np.zeros((self.nf, self.nl + 1))
            self.Fmin_    = np.zeros((self.nf, self.nl + 1, 2))
            self.Fplu_    = np.zeros((self.nf, self.nl + 1, 2))
            self.G1       = np.zeros((self.nl + 1, ))
            self.G2       = np.zeros((self.nl + 1, ))

            for i in np.arange(0, self.nf):

                # [nl, nlori]
                self.Qso_wfEs  = np.outer( self.Qso, np.reshape( \
                                    self.absfsfo * self.MpluEsun[i] + \
                                    self.fsfo * self.MminEsun[i], self.nlori))
                self.Qs_sfEs   = np.outer( self.Qs, np.reshape( \
                                    self.absfs * self.MpluEsun[i] - \
                                    self.fsctl * self.MminEsun[i], self.nlori))
                self.Qs_sbEs   = np.outer( self.Qs, np.reshape( \
                                    self.absfs * self.MpluEsun[i] + \
                                    self.fsctl * self.MminEsun[i], self.nlori))

                # [nl]
                self.Mplu_i = np.ones((self.nl, ))
                self.Mmin_i = np.ones((self.nl, ))
                self.Mplu_i[self.layers] = self.MpluEmin[i, self.layers] + \
                                           self.MpluEplu[i, self.layers + 1]
                self.Mmin_i[self.layers] = self.MminEmin[i, self.layers] - \
                                           self.MminEplu[i, self.layers + 1]

                # [nl]
                self.sigfEmini_sigbEplui = self.Mplu_i.T - \
                                           self.xdd2 * self.Mmin_i.T
                self.sigbEmini_sigfEplui = self.Mplu_i.T + \
                                           self.xdd2 * self.Mmin_i.T

                # [nl]
                self.Qso_Mplu  = self.Qso * self.Mplu_i.T
                self.Qso_Mmin  = self.Qso * self.Mmin_i.T
                self.Qsho_Mplu = self.Qsho * self.Mplu_i.T
                self.Qsho_Mmin = self.Qsho * self.Mmin_i.T

                self.Qso_vEd   = np.outer( self.Qso_Mplu, \
                                    np.reshape(self.absfo, self.nlori) ) + \
                                 np.outer( self.Qso_Mmin, \
                                    np.reshape(self.foctl, self.nlori) )
                self.Qsh_vEd   = np.outer( self.Qsho_Mplu, \
                                    np.reshape(self.absfo, self.nlori) ) + \
                                 np.outer( self.Qsho_Mmin, \
                                    np.reshape(self.foctl, self.nlori) )

                # Directly observed fluorescence contributions from sunlit and
                # shaded leaves

                self.piLs     = np.inner( np.mean( np.reshape( self.etau * \
                                        (self.Qso_wfEs + self.Qso_vEd), \
                                        (self.nl, self.nlinc, self.nlazi) ), \
                                        axis = 2), self.lidf)

                self.piLd     = self.etah * np.inner( np.mean( np.reshape( \
                                                    self.Qsh_vEd, (self.nl, \
                                                    self.nlinc, self.nlazi)), \
                                                    axis = 2), self.lidf)

                self.piLo1    = self.iLAI * sum(self.piLs)
                self.piLo2    = self.iLAI * sum(self.piLd)

                self.Qs_Fsmin = np.inner( np.mean( np.reshape( \
                                    (self.etau * self.Qs_sfEs), \
                                    (self.nl, self.nlinc, self.nlazi) ), \
                                    axis = 2), self.lidf) + \
                                    self.Qs * self.mn_etau * \
                                    self.sigfEmini_sigbEplui

                self.Qs_Fsplu = np.inner( np.mean( np.reshape( \
                                    (self.etau * self.Qs_sbEs), \
                                    (self.nl, self.nlinc, self.nlazi) ), \
                                    axis = 2), self.lidf) + \
                                    self.Qs * self.mn_etau * \
                                    self.sigbEmini_sigfEplui

                self.Qd_Fdmin = (1.0 - self.Qs) * self.etah * \
                                self.sigfEmini_sigbEplui
                self.Qd_Fdplu = (1.0 - self.Qs) * self.etah * \
                                self.sigbEmini_sigfEplui

                self.Fmin[i, self.layers + 1] = self.Qs_Fsmin + self.Qd_Fdmin
                self.Fplu[i, self.layers]     = self.Qs_Fsplu + self.Qd_Fdplu

                self.t2   = self.xdd2 * (self.rho[i] - self.tau[i]) / 2.0
                self.att  = 1.0 - (self.rho[i] + self.tau[i]) / 2.0 + self.t2
                self.sig  = (self.rho[i] + self.tau[i]) / 2.0 + self.t2
                self.m    = sqrt(self.att ** 2 - self.sig ** 2)
                self.rinf = (self.att - self.m) / self.sig
                self.fac  = 1.0 - self.m * self.iLAI
                self.facs = (self.rs[i] - self.rinf) / \
                            (1.0 - self.rs[i] * self.rinf)


                # Transformed SIF fluxes calculated numerically

                # To ensure we will enter the loop the first time
                self.G1[0] = 2.0
                self.Gnew  = 0.0

                # These are the source functions
                self.dF1 = (self.Fmin[i, self.layers + 1] + \
                            self.rinf * self.Fplu[i, self.layers]) * self.iLAI
                self.dF2 = (self.rinf * self.Fmin[i, self.layers + 1] + \
                            self.Fplu[i, self.layers]) * self.iLAI

                while np.abs(self.Gnew - self.G1[0]) > 0.001:

                    self.G1[0] = self.Gnew

                    for j in np.arange(1, self.nl + 1):

                        self.G1[j] = self.fac * self.G1[j - 1] + \
                                        self.dF1[j - 1]

                    self.G2[self.nl] = self.G1[self.nl] * self.facs

                    for j in np.arange(self.nl-1, -1, -1):

                        self.G2[j] = self.fac * self.G2[j + 1] + self.dF2[j]

                    self.Gnew = -self.rinf * self.G2[0]


                # Inverse transformation to get back the hemispherical fluxes

                self.Fplu_[i, :, PS] = (self.rinf * self.G1 + self.G2) / \
                                       (1.0 - self.rinf ** 2)
                self.Fmin_[i, :, PS] = (self.rinf * self.G2 + self.G1) / \
                                       (1.0 - self.rinf ** 2)

                self.Fhem_[i, PS]    = self.Fplu_[i, 0, PS]

                # The following contributions are coming from:
                # - Rescattered SIF at observed leaves (3)
                # - SIF flux reflected by observed soil (4)

                self.piLo3       = self.iLAI * np.inner( (self.vb[i] * \
                                    self.Fmin_[i, self.layers, PS] + \
                                    self.vf[i] * \
                                    self.Fplu_[i, self.layers + 1, PS]), \
                                    self.Qo )

                self.piLo4       = self.rs[i] * \
                                    self.Fmin_[i, self.nl, PS] * \
                                    self.Po[self.nl]

                self.piLtoti     = self.piLo1 + self.piLo2 + self.piLo3 + \
                                    self.piLo4

                self.LoF_[i, PS] = self.piLtoti / pi


            for ilayer in np.arange(0, self.nl):

                self.Fiprofile[ilayer, PS] = 0.001 * \
                                        library.Sint(self.Fplu[:, ilayer], \
                                                     self.param.spectral.wlF)


    def createOutputStructures(self):
        """
        Fill RTMf output structures
        """

        # Put output in the rad structure
        self.rad.LoF_              = self.LoF_[:, 0] + self.LoF_[:, 1]
        self.rad.LoF1_             = self.LoF_[:, 0]
        self.rad.LoF2_             = self.LoF_[:, 1]
        self.rad.Fhem_             = self.Fhem_[:, 0] + self.Fhem_[:, 1]

        self.rad.Eoutf             = 0.001 * library.Sint( \
                                                np.sum(self.Fhem_, axis = 1), \
                                                self.param.spectral.wlF)
        self.rad.Eminf_            = self.Emin_
        self.rad.Epluf_            = self.Eplu_

        # Put output in the profiles structure
        self.profiles.fluorescence = self.Fiprofile[:, 0] + \
                                     self.Fiprofile[:, 1]


    def writeOutput(self, param):
        """
        Write output from RTMf module to file.
        """

        # Specify output directory
        output_dir    = library.create_output_dir(param, 'rtmf')

        # Specify time step
        step          = str(param.xyt.k)

        # Write output structures using pickle

        # rad structure
        rad_file      = output_dir + "/" + "rad" + step + ".pkl"
        library.write_pickle(rad_file, self.rad)

        # profiles structure
        profiles_file = output_dir + "/" + "profiles" + step + ".pkl"
        library.write_pickle(profiles_file, self.profiles)


# EOF rtmf.py