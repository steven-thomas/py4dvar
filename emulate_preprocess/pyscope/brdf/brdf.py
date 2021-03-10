#!/usr/bin/env python

###############################################################################
# Script brdf.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: equivalent of calc_brdf module in SCOPE
# Note: this script corresponds to calc_brdf.m in SCOPE.
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
#   directional


import  numpy                           as np
from    math                            import *
import  os

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics

# Get other modules
from    pyscope.rtmo                    import run_rtmo
from    pyscope.rtmf                    import run_rtmf
from    pyscope.rtmt                    import run_rtmt_sb
from    pyscope.rtmt                    import run_rtmt_planck


class BRDF():
    """
    Calculate BRDF and directional temperature for many angles specified in a
    file
    """

    def __init__(self, param, leafopt, gap, rad, thermal, profiles):
        """
        Prepare input parameters and initialize arrays.
        """

        # Load parameters
        self.param              = param
        self.directional        = param.directional
        self.directional_angles = param.angles
        self.leafopt            = leafopt
        self.gap                = gap
        self.rad                = rad
        self.thermal            = thermal
        self.profiles           = profiles

        # Define other quantities
        self.tts                = param.angles.tts
        self.noa                = param.directional.noa

        # [noa_o] Angles for hotspot oversampling
        self.psi_hoversampling  = np.array([0.0, 0.0, 0.0, 0.0, 0.0, \
                                            2.0, 358.0])
        self.tto_hoversampling  = np.asarray([self.tts, self.tts + 2.0, \
                                              self.tts + 4.0, self.tts - 2.0, \
                                              self.tts - 4.0, self.tts, \
                                              self.tts])

        # [1] Number of oversampling angles
        self.noah_o             = np.size(self.tto_hoversampling)

        # Angles for plane oversampling
        self.psi_poversampling  = np.hstack([0.0*np.ones((6,)), \
                                             180.0*np.ones((6,)), \
                                             90.0*np.ones((6,)), \
                                             270.0*np.ones((6,))])
        self.tto_poversampling  = np.hstack([np.arange(10, 61, 10), \
                                              np.arange(10, 61, 10), \
                                              np.arange(10, 61, 10), \
                                              np.arange(10, 61, 10)])

        # [1] Number of oversampling angles
        self.noap_o             = np.size(self.tto_poversampling)

        # Observer angles
        self.directional.psi    = np.hstack([self.directional.psi, \
                                             self.psi_hoversampling, \
                                             self.psi_poversampling])
        self.directional.tto    = np.hstack([self.directional.tto, \
                                             self.tto_hoversampling, \
                                             self.tto_poversampling])

        # Total number of angles
        self.ntotal             = self.noa + self.noah_o + self.noap_o

        # Initialize arrays

        # [nwlS, noa+noa_o+noap_o]
        self.directional.brdf_  = np.zeros((np.size(self.param.spectral.wlS), \
                                            self.ntotal))

        # [noa+noa_o+noap_o]
        self.directional.Lot         = np.zeros((self.ntotal,))
        self.directional.Eoutte      = np.zeros((self.ntotal,))
        self.directional.BrightnessT = np.zeros((self.ntotal,))

        # [nwlF, noa+noa_o+noap_o]
        self.directional.LoF_   = np.zeros((np.size(self.param.spectral.wlF), \
                                            self.ntotal))
        self.directional.Lot_   = np.zeros((np.size(self.param.spectral.wlT), \
                                            self.ntotal))


    def computeBRDF(self):
        """
        Compute BRDF and directional temperature given angles.
        """

        # Loop over the angles
        for j in np.arange(0, self.ntotal):

            if (self.param.options.log_level):

                print( 'Angle : {:}'.format(self.directional_angles.tto) )

            # Optical BRDF
            self.directional_angles.tto = self.directional.tto[j]
            self.directional_angles.psi = self.directional.psi[j]

            # Replace param.angles with self.directional_angles in local
            # instance that does not affect the global param structure
            param_BRDF        = self.param
            param_BRDF.angles = self.directional_angles

            leafopt, directional_gap, directional_rad, prof = \
                                run_rtmo.runRTMo(param_BRDF, self.leafopt)

            # [nwl] BRDF (spectral) (nm-1)
            self.directional.brdf_[:,j]  = directional_rad.rso

            # Thermal directional brightness temperatures (Planck)
            if (self.param.options.calc_planck):

                directional_rad = run_rtmt_planck.runRTMt_planck(param_BRDF, \
                                            self.leafopt, directional_gap, \
                                            directional_rad, self.thermal)

                # [nwlt] Emitted diffuse radiance at top
                self.directional.Lot_[:,j]  = \
                                directional_rad.Lot_[self.param.spectral.IwlT]

            # Thermal directional brightness temperatures (Stefan-Boltzmann)
            else:

                T_struct         = [self.thermal.Tcu, self.thermal.Tch, \
                                    self.thermal.Ts[1], self.thermal.Ts[1]]
                obsdir           = 1
                directional_rad  = run_rtmt_sb.runRTMt_sb(param_BRDF, \
                                            self.leafopt, directional_rad, \
                                            directional_gap, T_struct, obsdir)

                self.directional.Lot[j]         = directional_rad.Eoutte
                self.directional.BrightnessT[j] = (pi * self.rad.Lot / \
                                                    const.sigmaSB)**0.25

            if (self.param.options.calc_fluor):

                directional_rad, prof = run_rtmf.runRTMf(param_BRDF, \
                                            self.leafopt, directional_gap, \
                                            directional_rad, self.profiles)

                self.directional.LoF_[:,j] = directional_rad.LoF_


    def writeOutput(self, param):
        """
        Write output from BRDF module to file.
        """

        # Specify output directories
        output_dir       = library.create_output_dir(param, 'brdf')

        # Specify time step
        step             = str(param.xyt.k)

        # Write output structures using pickle

        # directional structure
        directional_file = output_dir + "/" + "directional" + step + ".pkl"

        library.write_pickle(directional_file, self.directional)


# EOF brdf.py
