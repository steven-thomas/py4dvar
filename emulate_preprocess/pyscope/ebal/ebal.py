#!/usr/bin/env python

###############################################################################
# Script ebal.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: equivalent of ebal module in SCOPE
# Note: this script corresponds to ebal.m in SCOPE.
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
#   iter        numerical parameters used in the iteration for energy balance
#               closure
#   options     calculation options
#   spectral    spectral resolutions and wavelengths
#   rad         incident radiation
#   gap         probabilities of direct light penetration and viewing
#   leafopt     leaf optical properties
#   angles      viewing and observation angles
#   soil        soil properties
#   canopy      canopy properties
#   leafbio     leaf biochemical parameters

# Output:
#   iter        numerical parameters used in the iteration for energy balance
#               closure
#   fluxes      energy balance, turbulent, and CO2 fluxes
#   rad         radiation spectra
#   profiles    vertical profiles of fluxes
#   thermal     temperatures, aerodynamic resistances and friction velocity


import  numpy                           as np
import  os
from    math                            import *

# Class to define empty structure
from    pyscope.common.structures       import emptyStruct

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics
import  pyscope.common.library_biochem  as bio

# Call other modules
from    pyscope.rtmt                    import run_rtmt_sb


class Ebal():
    """
    Calculates the energy balance of a vegetated surface.
    """

    def __init__(self, param, leafopt, gap, rad, profiles):
        """
        Prepare input parameters and initialize arrays.
        """

        # Global constants
        self.MH2O      = const.MH2O
        self.Mair      = const.Mair
        self.rhoa      = const.rhoa
        self.cp        = const.cp
        self.g         = const.g
        self.kappa     = const.kappa
        self.sigmaSB   = const.sigmaSB

        # Parameters and previously computed quantities
        self.param     = param
        self.leafopt   = leafopt
        self.gap       = gap
        self.rad       = rad
        self.profiles  = profiles

        # Initializations and other preparations for the iteration loop
        self.counter   = 0                       # Iteration counter of ebal
        self.maxit     = param.numiter.maxit
        self.maxEBer   = param.numiter.maxEBer
        self.Wc        = param.numiter.Wc

        self.loop_flag = 1   # Flag is 0 when the calculation has finished

        self.Ta        = param.meteo.Ta
        self.ea        = param.meteo.ea
        self.Ca        = param.meteo.Ca
        self.p         = param.meteo.p

        self.Ts        = param.soil.Ts
        self.GAM       = param.soil.GAM

        self.nl        = param.canopy.nlayers
        self.kV        = param.canopy.kV
        self.xl        = param.canopy.xl
        self.LAI       = param.canopy.LAI

        self.Rnuc      = rad.Rnuc
        self.Ps        = gap.Ps

        k              = param.xyt.k      # Time step counter
        self.t         = param.xyt.t[k]


        if ((param.options.soil_heat_method < 2) and \
            (param.options.simulation == 1)):

            # Duration of the time interval (s)
            if (k > 0):

                Deltat = (self.t - param.xyt.t[k - 1]) * 86400.0

            else:

                Deltat = 1.0 / 48.0 * 86400.0

            self.x     = [[np.arange(0,12)], [np.arange(0,12)]].T * Deltat
            self.Tsold = soil.Tsold


        # Leaf temperature
        self.Tch       = (self.Ta + 0.1) * np.ones((self.nl,))      # Shaded
        self.Tcu       = (self.Ta + 0.3) * np.ones((np.shape(self.Rnuc)))
                                                                    #Sunlit

        # Leaf H2O
        self.ech       = self.ea * np.ones((self.nl,))              # Shaded
        self.ecu       = self.ea * np.ones((np.shape(self.Rnuc)))   # Sunlit

        # Leaf CO2
        self.Cch       = self.Ca * np.ones((self.nl,))              # Shaded
        self.Ccu       = self.Ca * np.ones((np.shape(self.Rnuc)))   # Sunlit

        # self.Tsold    = self.Ts # Soil temperature of the previous time step
        self.L         = -1.0     # Monin-Obukhov length

        self.SoilHeatMethod = param.options.soil_heat_method

        if not (param.options.simulation == 1):

            self.SoilHeatMethod = 2


        # Conversion of vapor pressure [Pa] to absolute humidity [kg kg-1]
        self.e_to_q    = self.MH2O / self.Mair / self.p

        # Matrix containing values for 1-Ps and Ps of soil
        self.Fs        = np.array([1.0 - self.Ps[-1], self.Ps[-1]])

        # Matrix containing values for Ps of canopy
        self.Fc        = (1.0 - self.Ps[0:-1]).T / self.nl

        # Here could be a stress factor for vcmax as a function of SMC defined,
        # but this is at present not incorporated.
        # Modification from Matlab code: SMCsf does not exist yet in any case,
        # so don't need to test for its existence to then set it to value.
        self.SMCsf     = 1

        self.fVh       = np.exp(self.kV * self.xl[0:-1])
        self.fVu       = np.ones((np.shape(self.Rnuc)))     # [13, 36, 60]

        for i in np.arange(0, 60):

            self.fVu[:,:,i] = self.fVh[i]


    def loopEnergyBalance(self):
        """
        Energy balance and radiative transfer loop
        """

        # Flag is 1 while energy balance does not close
        while (self.loop_flag):

            # Net radiation of the components

            #SPT dbgping
            #print( 'SPT shaded/sunlit max temp:', self.Tch.max(), self.Tcu.max() )
            
            # Thermal radiative transfer model for vegetation emission (with
            # Stefan-Boltzman's equation)
            T_struct = [self.Tcu, self.Tch, self.Ts[1], self.Ts[0]]
            obsdir   = 1
            self.rad = run_rtmt_sb.runRTMt_sb(self.param, self.leafopt, \
                                              self.rad, self.gap, \
                                              T_struct, obsdir)

            # Add net radiation of (1) solar and sky and (2) thermal emission
            # model

            self.Rnhct = self.rad.Rnhct
            self.Rnuct = self.rad.Rnuct
            self.Rnhst = self.rad.Rnhst
            self.Rnust = self.rad.Rnust

            self.Rnhc  = self.rad.Rnhc
            self.Rnuc  = self.rad.Rnuc
            self.Rnhs  = self.rad.Rnhs
            self.Rnus  = self.rad.Rnus

            # Net radiation
            self.Rnch  = self.Rnhc + self.Rnhct     # Canopy (shaded)
            self.Rncu  = self.Rnuc + self.Rnuct     # Canopy (sunlit)
            self.Rnsh  = self.Rnhs + self.Rnhst     # Soil   (shaded)
            self.Rnsu  = self.Rnus + self.Rnust     # Soil   (sunlit)
            self.Rns   = [self.Rnsh, self.Rnsu]#.T   # Soil   (sun+sh)

            # Aerodynamic roughness
            # Calculate friction velocity [m s-1] and aerodynamic resistances
            # [s m-1]

            resist_in = emptyStruct()

            #resist_in.u     = np.max(self.param.meteo.u, 0.2)
            #SPT wrong max function, use max or np.maximum
            resist_in.u     = np.maximum(self.param.meteo.u, 0.2)
            resist_in.L     = self.L
            resist_in.LAI   = self.param.canopy.LAI
            resist_in.rbs   = self.param.soil.rbs
            resist_in.rss   = self.param.soil.rss
            resist_in.rwc   = self.param.canopy.rwc
            resist_in.zo    = self.param.meteo.zo
            resist_in.d     = self.param.meteo.d
            resist_in.z     = self.param.meteo.z
            resist_in.hc    = self.param.canopy.hc
            resist_in.w     = self.param.canopy.leafwidth
            resist_in.Cd    = self.param.canopy.Cd

            self.resist_out = physics.resistances(resist_in)

            self.ustar      = self.resist_out.ustar
            self.raa        = self.resist_out.raa
            self.rawc       = self.resist_out.rawc
            self.raws       = self.resist_out.raws

            # Biochemical processes

            # Photosynthesis (A), fluorescence factor (F), and stomatal
            # resistance (rcw), for shaded (1) and sunlit (h) leaves
            biochem_in = emptyStruct()

            biochem_in.Fluorescence_model = \
                                        self.param.options.Fluorescence_model
            biochem_in.Type               = self.param.leafbio.Type
            biochem_in.p                  = self.p
            biochem_in.m                  = self.param.leafbio.m
            biochem_in.O                  = self.param.meteo.Oa
            biochem_in.Rdparam            = self.param.leafbio.Rdparam

            # Specific for the v.Caemmerer-Magnani model
            if self.param.options.Fluorescence_model == 2:

                biochem_in.Tyear        = self.param.leafbio.Tyear
                biochem_in.beta         = self.param.leafbio.beta
                biochem_in.qLs          = self.param.leafbio.qLs
                biochem_in.NPQs         = self.param.leafbio.kNPQs
                biochem_in.stressfactor = self.param.leafbio.stressfactor

            # Specific for Berry-v.d.Tol model
            else:

                biochem_in.tempcor      = self.param.options.apply_T_corr
                biochem_in.Tparams      = self.param.leafbio.Tparam
                biochem_in.stressfactor = self.SMCsf

            # Input parameters specific to shaded leaves
            biochem_in.T                  = self.Tch
            biochem_in.eb                 = self.ech
            biochem_in.Vcmo               = self.fVh * self.param.leafbio.Vcmo
            biochem_in.Cs                 = self.Cch
            biochem_in.Q                  = self.rad.Pnh * 1.0e6

            # If first iteration through energy balance, use dummy variable
            if (self.counter == 0):

                self.Ah = -999

            # If later iteration through energy balance, use output from
            # previous iteration (self.Ah will have value in that case)
            biochem_in.A = self.Ah

            # Compute biochemical parameters for shaded leaves
            if self.param.options.Fluorescence_model == 2:

                self.biochem_out        = bio.biochemical_MD12(biochem_in)

            else:

                self.biochem_out        = bio.biochemical(biochem_in)

            self.Ah   = self.biochem_out.A
            self.Cih  = self.biochem_out.Ci
            self.Fh   = self.biochem_out.eta
            self.rcwh = self.biochem_out.rcw
            # vCaemmerer- Magnani does not generate the qEh parameter
            # (dummy value)
            self.qEh  = self.biochem_out.qE

            # Input parameters specific to sunlit leaves
            biochem_in.T    = self.Tcu
            biochem_in.eb   = self.ecu
            biochem_in.Vcmo = self.fVu * self.param.leafbio.Vcmo
            biochem_in.Cs   = self.Ccu
            biochem_in.Q    = self.rad.Pnu * 1.0e6

            # If first iteration through energy balance, use dummy variable
            if self.counter == 0:

                self.Au = - 999

            # If later iteration through energy balance, use output from
            # previous iteration (self.Ah will have value in that case)
            biochem_in.A = self.Au

            # Compute biochemical parameters for sunlit leaves
            if self.param.options.Fluorescence_model == 2:

                self.biochem_out        = bio.biochemical_MD12(biochem_in)

            else:

                self.biochem_out        = bio.biochemical(biochem_in)

            self.Au       = self.biochem_out.A
            self.Ciu      = self.biochem_out.Ci
            self.Fu       = self.biochem_out.eta
            self.rcwu     = self.biochem_out.rcw
            self.qEu      = self.biochem_out.qE

            self.Pinh     = self.rad.Pnh
            self.Pinu     = self.rad.Pnu
            self.Pinh_Cab = self.rad.Pnh_Cab
            self.Pinu_Cab = self.rad.Pnu_Cab
            self.Rnh_PAR  = self.rad.Rnh_PAR
            self.Rnu_PAR  = self.rad.Rnu_PAR

            # Fluxes (latent heat flux (lE), sensible heat flux (H) and soil
            # heat flux G in analogy to Ohm's law, for canopy (c) and soil (s).
            # All in units of [W m-2]

            self.PSIs = 0   # soil.PSIs
            self.rss  = self.param.soil.rss

            self.lEch, self.Hch, self.ech, self.Cch = physics.heatfluxes( \
                                (self.LAI + 1.0) * (self.raa + self.rawc), \
                                self.rcwh, self.Tch, self.ea, self.Ta, \
                                self.e_to_q, 0.0, self.Ca, self.Cih)

            self.lEcu, self.Hcu, self.ecu, self.Ccu = physics.heatfluxes(\
                                (self.LAI + 1.0) * (self.raa + self.rawc), \
                                self.rcwu, self.Tcu, self.ea, self.Ta, \
                                self.e_to_q, 0.0, self.Ca, self.Ciu)

            self.lEs, self.Hs, dummy1, dummy2       = physics.heatfluxes( \
                                (self.LAI + 1.0) * (self.raa + self.raws), \
                                self.rss, self.Ts, self.ea, self.Ta, \
                                self.e_to_q, self.PSIs, self.Ca, self.Ca)

            # Integration over the layers and sunlit and shaded fractions
            self.Hstot = np.inner(self.Fs, self.Hs)
            self.Hctot = self.LAI * (np.inner(self.Fc, self.Hch) + \
                            physics.meanleaf(self.param.canopy, self.Hcu, \
                                             'angles_and_layers', self.Ps))

            self.Htot  = self.Hstot + self.Hctot

            # G = (t>0 && SoilHeatMethod<2)*(Rns-lEs-Hs) + (t==0 || \
            #       SoilHeatMethod==2)*(0.35*Rns);
            if (self.SoilHeatMethod == 2):

                self.G = 0.35 * np.asarray(self.Rns)

            else:

                # FIXME: where does 'x' come from? Not clear in Matlab code.
                self.G = self.GAM / sqrt(pi) * 2.0 * \
                    np.sum( ([[self.Ts.T], [self.Tsold[0:-1,:]]] - Tsold) / \
                            Deltat * (np.sqrt(x) - np.sqrt(x - Deltat)))
                #G=G.T

            # Monin-Obukhov length L (scalar)
            self.L                    = -const.rhoa * const.cp * \
                                        self.ustar ** 3.0 * \
                                        (self.Ta + 273.15) / \
                                        (const.kappa * const.g * self.Htot)

            # Cap length L if needed
            if (self.L < -1000.0):

                self.L = -1000.0

            elif (self.L > 100.0):

                self.L = 100.0

            elif (np.isnan(self.L)):

                self.L = -1.0

            # Energy balance errors, continue criterion and iteration counter
            self.EBerch = self.Rnch - self.lEch - self.Hch
            self.EBercu = self.Rncu - self.lEcu - self.Hcu
            self.EBers  = self.Rns - self.lEs - self.Hs - self.G

            # Number of iterations
            self.counter     = self.counter + 1

            self.maxEBercu   = np.abs(self.EBercu).max()
            self.maxEBerch   = np.max(np.abs(self.EBerch))
            self.maxEBers    = np.max(np.abs(self.EBers))

            # Continue iteration?
            self.loop_flag   = (self.maxEBercu > self.maxEBer or \
                                self.maxEBerch > self.maxEBer or \
                                self.maxEBers > self.maxEBer) and \
                                self.counter < self.maxit

            # New estimates of soil (s) and leaf (c) temperatures, shaded (h)
            # and sunlit (1)

            # Tch = Ta + update(Tch-Ta,Wc,(raa + rawc)/(rhoa*cp).* \
            #       (Rnch - lEch))
            # Tcu = Ta + update(Tcu-Ta,Wc,(raa + rawc)/(rhoa*cp).* \
            #       (Rncu - lEcu))
            # Ts  = Ta + update(Ts-Ta,Wc, (raa + raws)/(rhoa*cp).* \
            #       (Rns - lEs - G))

            self.Tch = self.Tch + self.Wc * \
                        (self.Rnch - self.lEch - self.Hch) / \
                        ((const.rhoa * const.cp) / ((self.LAI + 1.0) * \
                        (self.raa + self.rawc)) + \
                        4.0 * const.sigmaSB * (self.Tch + 273.15) ** 3)

            self.Tcu = self.Tcu + self.Wc * \
                        (self.Rncu - self.lEcu - self.Hcu) / \
                        ((const.rhoa * const.cp) / ((self.LAI + 1.0) * \
                        (self.raa + self.rawc)) + \
                        4.0 * const.sigmaSB * (self.Tcu + 273.15) ** 3)

            self.Ts[np.abs(self.Ts) > 100.0] = self.Ta

            self.Ts = self.Ts + self.Wc * \
                        (self.Rns - self.lEs - self.Hs - self.G) / \
                        ((const.rhoa * const.cp) / (self.raa + self.rawc) + \
                        (const.rhoa * const.cp) / (self.raa + self.rawc) + \
                        4.0 * const.sigmaSB * (self.Ts + 273.15) ** 3)

            if (self.counter > 50):

                self.Wc = 0.2

        # End of energy balance loop

        # Stored for logging purposes
        #iter.counter= self.counter
        self.param.xyt.iter_counter = self.counter

        # Untested
        if self.SoilHeatMethod < 2:

            self.Tsold[1:, :] = self.param.soil.Tsold[0:-1, :]
            self.Tsold[0, :]  = self.Ts[:]

            if np.isnan(self.Ts):

                self.Tsold[0, :] = self.Tsold[1, :]

            self.param.soil.Tsold = self.Tsold


        self.Tbr  = (self.rad.Eoutte / const.sigmaSB) ** 0.25
        self.Lot_ = physics.Planck(self.param.spectral.wlS.T, self.Tbr)

        self.rad.LotBB_ = self.Lot_

        # Print warnings whenever the energy balance could not be solved
        if (self.counter >= self.maxit):

            print( 'Warning: Maximum number of iteratations exceeded' )

        msg = 'Energy balance error sunlit vegetation = {:} W m-2'
        print( msg.format(self.maxEBercu) )
        msg = 'Energy balance error shaded vegetation = {:} W m-2'
        print( msg.format(self.maxEBerch) )
        msg = 'Energy balance error soil = {:} W m-2'
        print( msg.format(self.maxEBers) )

        print( 'Number of iterations = {:}'.format(self.counter) )


    def calculateLayers(self):
        """
        Calculate output per layer
        """

        self.profiles.etah = self.Fh
        self.profiles.etau = self.Fu

        # NOTE: The matlab equivalent of the code below misses arguments in
        # the calls to meanleaf, so perhaps this is not used typically?

        # Calculate the output per layer
        if (self.param.options.calc_vert_profiles):

            # [nli,nlo,nl] Means for sunlit leaves

            # Sens heat
            self.Hcu1d   = physics.meanleaf(self.param.canopy, self.Hcu, \
                                            'angles', self.gap.Ps)

            # Latent
            self.lEcu1d  = physics.meanleaf(self.param.canopy, self.lEcu, \
                                            'angles', self.gap.Ps)

            # Phots
            self.Au1d    = physics.meanleaf(self.param.canopy, self.Au, \
                                            'angles', self.gap.Ps)

            # Fluor
            self.Fu_Pn1d = physics.meanleaf(self.param.canopy, \
                                            self.Fu * self.Pinu_Cab, \
                                            'angles', self.gap.Ps)

            # Fluor
            self.qEuL    = physics.meanleaf(self.param.canopy, self.qEu, \
                                            'angles', self.gap.Ps)

            # Net rad
            # self.Pnu1d   = physics.meanleaf(self.param.canopy, self.Pinu, \
            #                                 'angles', self.gap.Ps)

            # Net rad
            # self.Pnu1d_Cab = physics.meanleaf(self.param.canopy, \
            #                                   self.Pinu_Cab, 'angles',\
            #                                   self.gap.Ps)

            # Net PAR
            self.Rnu1d   = physics.meanleaf(self.param.canopy, self.Rncu, \
                                            'angles', self.gap.Ps)

            # Temp
            self.Tcu1d   = physics.meanleaf(self.param.canopy, self.Tcu, \
                                            'angles', self.gap.Ps)

            # Mean temperature for shaded leaves
            self.profiles.Tchave = self.Tch.mean(axis = 0)        # [1]
            self.profiles.Tch    = self.Tch                       # [nl]
            self.profiles.Tcu1d  = self.Tcu1d                     # [nl]

            # [nl] Means for leaves per layer

            # Temp
            self.profiles.Tc1d   = (1.0 - self.Ps[0:self.nl]) * self.Tch + \
                                    self.Ps[0:self.nl] * self.Tcu1d

            # Sens heat
            self.profiles.Hc1d   = (1.0 - self.Ps[0:self.nl]) * self.Hch + \
                                    self.Ps[0:self.nl] * self.Hcu1d

            # Latent heat
            self.profiles.lEc1d  = (1.0 - self.Ps[0:self.nl]) * self.lEch + \
                                    self.Ps[0:self.nl] * self.lEcu1d

            # Photos
            self.profiles.A1d    = (1.0 - self.Ps[0:self.nl]) * self.Ah + \
                                    self.Ps[0:self.nl] * self.Au1d

            # Fluor
            self.profiles.F_Pn1d = (1.0 - self.Ps[0:self.nl]) * self.Fh * \
                                    self.Pinh_Cab + \
                                    self.Ps[0:self.nl] * self.Fu_Pn1d
            # Fluor
            self.profiles.qE     = (1.0 - self.Ps[0:self.nl]) * self.qEh + \
                                    self.Ps[0:self.nl] * self.qEuL

            # Photos
            # self.profiles.Pn1d   = (1.0 - self.Ps[0:self.nl]) * self.Pinh + \
            #                       self.Ps[0:self.nl] * self.Pnu1d

            # Photos
            # self.profiles.Pn1d_Cab = (1.0 - self.Ps[0:self.nl]) * \
            #                           self.Pinh_Cab + \
            #                           self.Ps[0:self.nl] * self.Pnu1d_Cab

            self.profiles.Rn1d   = (1.0 - self.Ps[0:self.nl]) * self.Rnch + \
                                    self.Ps[0:self.nl] * self.Rnu1d


    def calculateTotals(self):
        """
        Calculate spectrally integrated quantities, sums, and averages
        """

        # Calculate spectrally integrated energy, water and CO2 fluxes:

        # Sum of all leaves, and average leaf temperature
        # (note that averaging temperature is physically not correct...)

        # Net radiation leaves
        self.Rnctot    = self.LAI * (np.inner(self.Fc, self.Rnch) + \
                            physics.meanleaf(self.param.canopy, self.Rncu, \
                            'angles_and_layers', self.Ps))

        # Latent heat leaves
        self.lEctot    = self.LAI * (np.inner(self.Fc, self.lEch) + \
                            physics.meanleaf(self.param.canopy, self.lEcu, \
                            'angles_and_layers', self.Ps))

        # Sensible heat leaves
        self.Hctot     = self.LAI * (np.inner(self.Fc, self.Hch) + \
                            physics.meanleaf(self.param.canopy, self.Hcu, \
                            'angles_and_layers', self.Ps))

        # Photosynthesis leaves
        self.Actot     = self.LAI * (np.inner(self.Fc, self.Ah) + \
                            physics.meanleaf(self.param.canopy, self.Au, \
                            'angles_and_layers', self.Ps))

        # Mean leaf temperature
        self.Tcave     = (np.inner(self.Fc, self.Tch) + \
                            physics.meanleaf(self.param.canopy, self.Tcu, \
                            'angles_and_layers', self.Ps))

        # Net PAR leaves
        self.Pntot     = self.LAI * (np.inner(self.Fc, self.Pinh) + \
                            physics.meanleaf(self.param.canopy, self.Pinu, \
                            'angles_and_layers', self.Ps))

        # Net PAR leaves
        self.Pntot_Cab = self.LAI * (np.inner(self.Fc, self.Pinh_Cab) + \
                            physics.meanleaf(self.param.canopy, \
                            self.Pinu_Cab, 'angles_and_layers', self.Ps))

        # Net PAR leaves
        self.Rntot_PAR = self.LAI * (np.inner(self.Fc, self.Rnh_PAR) + \
                            physics.meanleaf(self.param.canopy, \
                            self.Rnu_PAR, 'angles_and_layers', self.Ps))

        # Sum of soil fluxes and average temperature
        # (note that averaging temperature is physically not correct...)
        self.Rnstot = np.inner(self.Fs, self.Rns)   # Net radiation soil
        self.lEstot = np.inner(self.Fs, self.lEs)   # Latent heat soil
        # self.Hstot  = np.inner(self.Fs, self.Hs)    # Sensible heat soil
        self.Gtot   = np.inner(self.Fs, self.G)     # Soil heat flux
        self.Tsave  = np.inner(self.Fs, self.Ts)    # Soil temperature

        # Soil respiration is defined in the matlab code as:
        # R = 0 + 0*Ts;    %umol m-2 s-1 (why zero?)
        #self.Resp   = self.Fs * physics.soil_respiration(self.Ts)
        self.Resp  = 0.0                            # Soil respiration

        # Total fluxes (except sensible heat), all leaves and soil
        self.Atot  = self.Actot                     # GPP
        self.Rntot = self.Rnctot + self.Rnstot      # Net radiation
        self.lEtot = self.lEctot + self.lEstot      # Latent heat
        # self.Htot  = self.Hctot + self.Hstot        # Sensible heat


    def createOutputStructures(self):
        """
        Fill Ebal output structures
        """

        # Initialize fluxes output structure
        self.fluxes     = emptyStruct()

        # Place results in fluxes output structure

        # [W m-2] Total net radiation (canopy + soil)
        self.fluxes.Rntot    = self.Rntot

        # [W m-2] Total latent heat flux (canopy + soil)
        self.fluxes.lEtot    = self.lEtot

        # [W m-2] Total sensible heat flux (canopy + soil)
        self.fluxes.Htot     = self.Htot

        # [umol m-2 s-1] Total net CO2 uptake (canopy + soil)
        self.fluxes.Atot     = self.Atot

        self.fluxes.Rnctot   = self.Rnctot  # [W m-2] Canopy net radiation
        self.fluxes.lEctot   = self.lEctot  # [W m-2] Canopy latent heat flux
        self.fluxes.Hctot    = self.Hctot   # [W m-2] Canopy sensible heat flux

        # [umol m-2 s-1] Canopy net CO2 uptake
        self.fluxes.Actot    = self.Actot

        self.fluxes.Rnstot   = self.Rnstot  # [W m-2] Soil net radiation
        self.fluxes.lEstot   = self.lEstot  # [W m-2] Soil latent heat flux
        self.fluxes.Hstot    = self.Hstot   # [W m-2] Soil sensible heat flux
        self.fluxes.Gtot     = self.Gtot    # [W m-2] Soil heat flux

        self.fluxes.Resp     = self.Resp    # [umol m-2 s-1] Soil respiration

        self.fluxes.aPAR     = self.Pntot       # [umol m-2 s-1] Absorbed PAR
        self.fluxes.aPAR_Cab = self.Pntot_Cab   # [umol m-2 s-1]  Absorbed PAR
        self.fluxes.aPAR_Wm2 = self.Rntot_PAR   # [W m-2] Absorbed PAR


        # Initialize thermal output structure
        self.thermal    = emptyStruct()

        # Place results in thermal output structure

        # [oC] Air temperature (as in input)
        self.thermal.Ta    = self.Ta

        # [oC] Soil temperature, sunlit and shaded [2x1]
        self.thermal.Ts    = self.Ts

        # [oC] Weighted average canopy temperature
        self.thermal.Tcave = self.Tcave

        # [oC] Weighted average soil temperature
        self.thermal.Tsave = self.Tsave

        # [s m-1] Total aerodynamic resistance above canopy
        self.thermal.raa   = self.raa

        # [s m-1] Aerodynamic resistance below canopy for canopy
        self.thermal.rawc  = self.rawc

        # [s m-1] Aerodynamic resistance below canopy for soil
        self.thermal.raws  = self.raws

        # [m s-1] Friction velocity
        self.thermal.ustar = self.ustar

        self.thermal.Tcu   = self.Tcu
        self.thermal.Tch   = self.Tch


    def writeOutput(self, param):
        """
        Write output from Ebal module to file.
        """

        # Specify output directories
        output_dir    = library.create_output_dir(param, 'ebal')

        # Specify time step
        step          = str(param.xyt.k)

        # Write output structures using pickle

        # fluxes structure
        fluxes_file   = output_dir + "/" + "fluxes" + step + ".pkl"
        library.write_pickle(fluxes_file, self.fluxes)

        # thermal structure
        thermal_file  = output_dir + "/" + "thermal" + step + ".pkl"
        library.write_pickle(thermal_file, self.thermal)

        # rad structure
        rad_file      = output_dir + "/" + "rad" + step + ".pkl"
        library.write_pickle(rad_file, self.rad)

        
        # biochem structure
        profiles_file = output_dir + "/" + "biochem" + step + ".pkl"
        library.write_pickle(profiles_file, self.biochem_out)


# EOF ebal.py
