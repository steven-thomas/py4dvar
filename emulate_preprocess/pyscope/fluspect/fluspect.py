#!/usr/bin/env python

###############################################################################
# Script fluspect.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: equivalent of Fluspect module in SCOPE
# Note: this script corresponds to fluspect.m in SCOPE.
#
# Authors:
# * Christian Frankenberg <cfranken@caltech.edu>
#   California Institute of Technology
# * Laura Alisic Jewell <Laura.A.Jewell@jpl.nasa.gov>
#   Jet Propulsion Laboratory
#
# Copyright (c) 2015-2016, California Institute of Technology.
# ALL RIGHTS RESERVED. This work is supported in part by the W.M. Keck 
# Institute for Space Studies.
#
# Last modified: Jan 06, 2016 by Laura Alisic Jewell
###############################################################################

# NOTE: Variable name changes proposed by Christian:
# Cs          -> Cbrown
# Cca         -> Car
# Cdm         -> Cm
# optipar.nr  -> optipar.n
# optipar.Kab -> optipar.absChl
# optipar.Kca -> optipar.absCar
# optipar.Ks  -> optipar.absBro
# optipar.Kw  -> optipar.absH2O
# optipar.Kdm -> optipar.absDry

from    math                            import *
import  numpy                           as np
import  scipy
import  os

# Class to define empty structure
from    pyscope.common.structures       import emptyStruct

# Global constants
import  pyscope.common.global_constants as const

# Get library of various functions
import  pyscope.common.library_aux      as library
import  pyscope.common.library_physics  as physics


class Fluspect():
    """
    Empty docstring!
    """

    def __init__(self, param):
        """
        Collect input to Fluspect module.
        """

        # Load leafbio
        leafbio       = param.leafbio

        self.N        = leafbio.N
        self.Cab      = leafbio.Cab
        self.Cca      = leafbio.Cca
        self.Cs       = leafbio.Cs
        self.Cw       = leafbio.Cw
        self.Cdm      = leafbio.Cdm
        self.fqe      = leafbio.fqe

        # Load spectral bands
        spectral      = param.spectral

        self.wlP      = spectral.wlP
        self.wlE      = spectral.wlE
        self.wlF      = spectral.wlF

        # So far, this is fixed but can be modified to test impact (not sure
        # how important)
        self.ndub     = 15

        # Load optipar
        self.optipar  = param.optipar

        # Create output structure
        self.leafopt  = emptyStruct()


    def setWavelength(self):
        """
        Define the wavelength vectors.
        """

        # NOTE: The optipar reading function had already switched the variable
        # names, but I recently retracted them here to make debugging vs SCOPE
        # easier. Can change back later.
        self.nr     = self.optipar.n       # nr
        self.Kab    = self.optipar.absChl  # Kab
        self.Kca    = self.optipar.absCar  # Kca
        self.Ks     = self.optipar.absBro  # Ks
        self.Kw     = self.optipar.absH2O  # Kw
        self.Kdm    = self.optipar.absDry  # Kdm
        self.phiI   = self.optipar.phiI
        self.phiII  = self.optipar.phiII

        # Christian: One feature I didn't like about Prospect before was the
        # hard-coding of the wavelength range, tried to change that here

        # NOTE: Not used at the moment.
        # wl          = self.wlP
        # self.n      = np.interp(wl, self.data[:,0], self.data[:,1])
        # self.Kab    = np.interp(wl, self.data[:,0], self.data[:,3])
        # # self.Kca  = np.interp(wl, self.data[:,0], self.data[:,3])
        # self.Ks     = np.interp(wl, self.data[:,0], self.data[:,5])
        # self.Kw     = np.interp(wl, self.data[:,0], self.data[:,4])
        # self.Kdm = np.interp(wl, self.data[:,0], self.data[:,2])
        # self.phiI   = np.interp(wl, self.data[:,0], self.data[:,6])
        # self.phiII  = np.interp(wl, self.data[:,0], self.data[:,7])


    def getLRT_original(self):
        """
        Compute LRT, according to original SCOPE algorithm.
        """

        # PROSPECT calculations
        # Compact leaf layer
        Kall       = (self.Cab * self.Kab + self.Cca * self.Kca + \
                      self.Cdm * self.Kdm + self.Cw * self.Kw + \
                      self.Cs * self.Ks) / self.N

        self.Kall = Kall

        # Non-conservative scattering (normal case)
        j          = np.where(Kall > 0)
        t1         = (1.0 - Kall) * np.exp(-Kall)
        t2         = Kall ** 2.0 * scipy.special.expn(1, Kall)
        tau        = np.ones((np.shape(t1)))
        tau[j]     = t1[j] + t2[j]

        kChlrel    = np.zeros((np.shape(t1)))
        kChlrel[j] = self.Cab * self.Kab[j] / (Kall[j] * self.N)

        talf       = physics.calctav(59.0, self.nr)
        ralf       = 1.0 - talf

        t12        = physics.calctav(90.0, self.nr)
        r12        = 1.0 - t12
        t21        = t12 / (self.nr ** 2)
        r21        = 1.0 - t21

        # Top surface side
        denom      = 1.0 - r21 * r21 * tau ** 2
        Ta         = talf * tau * t21 / denom
        Ra         = ralf + r21 * tau * Ta

        # Bottom surface side
        t          = t12 * tau * t21 / denom
        r          = r12 + r21 * tau * t

        # Stokes equations to compute properties of next N-1 layers (N real)

        # Normal case
        D          = np.sqrt((1.0 + r + t) * (1.0 + r - t) * (1.0 - r + t) * \
                             (1.0 - r - t))
        rq         = r ** 2
        tq         = t ** 2
        a          = (1.0 + rq - tq + D) / (2.0 * r)
        b          = (1.0 - rq + tq + D) / (2.0 * t)

        bNm1       = b ** (self.N - 1.0)
        bN2        = bNm1 ** 2
        a2         = a ** 2
        denom      = a2 * bN2 - 1.0
        Rsub       = a * (bN2 - 1.0) / denom
        Tsub       = bNm1 * (a2 - 1.0) / denom

        # Case of zero absorption
        j          = np.where(r + t >= 1.0)
        Tsub[j]    = t[j] / (t[j] + (1.0 - t[j]) * (self.N - 1.0))
        Rsub[j]    = 1.0 - Tsub[j]

        # Reflectance and transmittance of the leaf: combine top layer with
        # next N-1 layers
        denom      = 1.0 - Rsub * r
        tran       = Ta * Tsub / denom
        refl       = Ra + Ta * Rsub * t / denom

        self.leafopt.refl    = refl
        self.leafopt.trans   = tran
        self.leafopt.kChlrel = kChlrel

        # From here a new path is taken: The doubling method used to calculate
        # fluoresence is now only applied to the part of the leaf where
        # absorption takes place, that is, the part exclusive of the leaf-air
        # interfaces. The reflectance (rho) and transmittance (tau) of this
        # part of the leaf are now determined by "subtracting" the interfaces.

        # Remove the top interface
        Rb  = (refl - ralf) / (talf * t21 + (refl - ralf) * r21)

        # Derive Z from the transmittance
        Z   = tran * (1.0 - Rb * r21) / (talf * t21)

        # Reflectance and transmittance of the leaf mesophyll layer
        rho = (Rb - r21 * (Z ** 2)) / (1.0 - (r21 * Z) ** 2)
        tau = (1.0 - Rb * r21) / (1.0 - (r21 * Z) ** 2) * Z

        t   = tau
        r   = rho
        r[r < 0.0] = 0.0           # Avoid negative r

        # Derive Kubelka-Munk s and k
        I_rt        = np.where((r + t) < 1.0)
        D[I_rt]     = np.sqrt((1.0 + r[I_rt] + t[I_rt]) * \
                              (1.0 + r[I_rt] - t[I_rt]) * \
                              (1.0 - r[I_rt] + t[I_rt]) * \
                              (1.0 - r[I_rt] - t[I_rt]))

        a[I_rt]     = (1.0 + r[I_rt] ** 2 - t[I_rt] ** 2 + D[I_rt]) / \
                        (2.0 * r[I_rt])
        b[I_rt]     = (1.0 - r[I_rt] ** 2 + t[I_rt] ** 2 + D[I_rt]) / \
                        (2.0 * t[I_rt])

        # FIXME: Had to comment this out to make a[0] and b[0] correct.
        #a[not I_rt] = 1.0
        #b[not I_rt] = 1.0

        s      = r / t
        I_a    = np.where((a > 1.0) & (a != np.inf))
        s[I_a] = 2.0 * a[I_a] / (a[I_a] ** 2 - 1.0) * np.log(b[I_a])

        k      = np.log(b)
        k[I_a] = (a[I_a] - 1.0) / (a[I_a] + 1.0) * np.log(b[I_a])
        kChl   = kChlrel * k

        # Fluorescence of the leaf mesophyll layer
        if (self.fqe[0] > 0):

            # Excitation wavelengths, transpose to column
            wle     = self.wlE.T

            # Fluorescence wavelengths, transpose to column
            wlf     = self.wlF.T

            # PROSPECT wavelengths, kept as a row vector
            wlp     = self.wlP

            minwle  = np.min(wle)
            maxwle  = np.max(wle)
            minwlf  = np.min(wlf)
            maxwlf  = np.max(wlf)

            # Indices of wle and wlf within wlp
            Iwle    = np.where((wlp >= minwle) & (wlp <= maxwle))
            Iwlf    = np.where((wlp >= minwlf) & (wlp <= maxwlf))

            eps     = 2.0 ** (-self.ndub)

            # Initializations
            te      = 1.0 - (k[Iwle] + s[Iwle]) * eps
            tf      = 1.0 - (k[Iwlf] + s[Iwlf]) * eps
            re      = s[Iwle] * eps
            rf      = s[Iwlf] * eps

            # Matrix computed as an outproduct
            sigmoid = 1.0 / (1.0 + np.outer(np.exp(- wlf / 10.0), \
                                            np.exp(wle.T / 10.0)))

            # Other factor .5 deleted, since these are the complete
            # efficiencies for either PSI or PSII, not a linear combination

            MfI     = self.fqe[0] * np.outer((0.5 * self.phiI[Iwlf]) * eps, \
                                             kChl[Iwle].T) * sigmoid
            MbI     = self.fqe[0] * np.outer((0.5 * self.phiI[Iwlf]) * eps, \
                                             kChl[Iwle].T) * sigmoid

            MfII    = self.fqe[1] * np.outer((0.5 * self.phiII[Iwlf]) * eps, \
                                             kChl[Iwle].T) * sigmoid
            MbII    = self.fqe[1] * np.outer((0.5 * self.phiII[Iwlf]) * eps, \
                                             kChl[Iwle].T) * sigmoid

            # Row of ones
            Ih      = np.ones((len(te),))

            # Column of ones
            Iv      = np.ones((len(tf),))

            # Doubling routine

            for i in np.arange(0, self.ndub):

                xe    = te / (1.0 - re * re)
                ten   = te * xe
                ren   = re * (1.0 + ten)

                xf    = tf / (1.0 - rf * rf)
                tfn   = tf * xf
                rfn   = rf * (1.0 + tfn)

                A11   = np.outer(xf, Ih) + np.outer(Iv, xe.T)
                A12   = np.outer(xf, xe.T) * (np.outer(rf, Ih) + \
                                              np.outer(Iv, re.T))

                A21   = 1.0 + np.outer(xf, xe.T) * (1.0 + np.outer(rf, re.T))
                A22   = np.outer((xf * rf), Ih) + np.outer(Iv, (xe * re))

                MfnI  = MfI * A11 + MbI * A12
                MbnI  = MbI * A21 + MfI * A22
                MfnII = MfII * A11 + MbII * A12
                MbnII = MbII * A21 + MfII * A22

                te    = ten
                re    = ren
                tf    = tfn
                rf    = rfn

                MfI   = MfnI
                MbI   = MbnI
                MfII  = MfnII
                MbII  = MbnII

            # Here we add the leaf-air interfaces again for obtaining the
            # final leaf level fluorescences.

            g1  = MbI
            g2  = MbII
            f1  = MfI
            f2  = MfII

            Rb  = rho + tau ** 2.0 * r21 / (1.0 - rho * r21)

            Xe  = np.outer(Iv, (talf[Iwle] / (1.0 - r21[Iwle] * Rb[Iwle])))
            Xf  = np.outer(t21[Iwlf] / (1.0 - r21[Iwlf] * Rb[Iwlf]), Ih)
            Ye  = np.outer(Iv, (tau[Iwle] * r21[Iwle] / \
                                (1.0 - rho[Iwle] * r21[Iwle])))
            Yf  = np.outer(tau[Iwlf] * r21[Iwlf] / (1.0 - rho[Iwlf] * \
                            r21[Iwlf]), Ih)

            A   = Xe * (1.0 + Ye * Yf) * Xf
            B   = Xe * (Ye + Yf) * Xf

            g1n = A * g1 + B * f1
            f1n = A * f1 + B * g1
            g2n = A * g2 + B * f2
            f2n = A * f2 + B * g2

            self.leafopt.MbI  = g1n
            self.leafopt.MbII = g2n
            self.leafopt.MfI  = f1n
            self.leafopt.MfII = f2n


    def getLRT(self):
        """
        Compute LRT; algorithm modified by Christian Frankenberg.
        """

        # Sum cross sections

        # Equation by Christian
        # k = (self.Cab*self.Kab + self.Cs * self.Ks +
        #    self.Cw * self.Kw + self.Cdm * self.Kdm)/self.N

        # Use exact same as in Matlab:
        k = (self.Cab*self.Kab + self.Cca*self.Kca + \
            self.Cw*self.Kw + self.Cs*self.Ks + \
            self.Cdm*self.Kdm) / self.N

        self.leafopt.kChlrel = self.Cab*self.Kab / (k*self.N)

        tau = np.zeros((len(k),))
        tau[k == 0] = 1

        wo = np.where((k > 0.0) & (k <= 4))[0]

        xx =0.5*k[wo] - 1.0
        yy = (((((((((((((((-3.60311230482612224e-13*xx +
            3.46348526554087424e-12)*xx - 2.99627399604128973e-11)*xx +
            2.57747807106988589e-10)*xx - 2.09330568435488303e-9)*xx +
            1.59501329936987818e-8)*xx - 1.13717900285428895e-7)*xx +
            7.55292885309152956e-7)*xx - 4.64980751480619431e-6)*xx +
            2.63830365675408129e-5)*xx - 1.37089870978830576e-4)*xx +
            6.47686503728103400e-4)*xx - 2.76060141343627983e-3)*xx +
            1.05306034687449505e-2)*xx - 3.57191348753631956e-2)*xx +
            1.07774527938978692e-1)*xx - 2.96997075145080963e-1
        yy = (yy*xx + 8.64664716763387311e-1)*xx + 7.42047691268006429e-1
        yy = yy - np.log(k[wo])

        tau[wo] = (1.0-k[wo]) * np.exp(-k[wo]) + k[wo]**2*yy

        del xx, yy

        wo = np.where((k > 4.0) & (k <= 85))[0]

        xx = 14.5 / (k[wo] + 3.25) - 1.0
        yy = (((((((((((((((-1.62806570868460749e-12*xx -
            8.95400579318284288e-13)*xx - 4.08352702838151578e-12)*xx -
            1.45132988248537498e-11)*xx - 8.35086918940757852e-11)*xx -
            2.13638678953766289e-10)*xx - 1.10302431467069770e-9)*xx -
            3.67128915633455484e-9)*xx - 1.66980544304104726e-8)*xx -
            6.11774386401295125e-8)*xx - 2.70306163610271497e-7)*xx -
            1.05565006992891261e-6)*xx - 4.72090467203711484e-6)*xx -
            1.95076375089955937e-5)*xx - 9.16450482931221453e-5)*xx -
            4.05892130452128677e-4)*xx - 2.14213055000334718e-3
        yy = (((yy*xx - 1.06374875116569657e-2)*xx -
            8.50699154984571871e-2)*xx + 9.23755307807784058e-1)
        yy = np.exp(-k[wo])*yy / k[wo]

        tau[wo] = (1.0 - k[wo]) * np.exp(-k[wo]) + k[wo]**2*yy
        tau[k > 85] = 0

        # Transmissivity of the layer
        t1 = physics.tav(90., self.n)
        t2 = physics.tav(59., self.n)

        x1 = 1 - t1
        x2 = t1**2 * tau**2 * (self.n**2 - t1)
        x3 = t1**2 * tau*self.n**2
        x4 = self.n**4 - tau**2 * (self.n**2 - t1)**2
        x5 = t2/t1
        x6 = x5*(t1 - 1) + 1 - t2

        r  = x1 + x2/x4
        t  = x3/x4
        ra = x5*r + x6
        ta = x5*t

        # Reflectance and transmittance of N layers
        #
        # Source:
        # Stokes G.G. (1862), On the intensity of the light reflected from or
        # transmitted through a pile of plates, Proceedings of the Royal
        # Society of London, 11:545-556.

        delta = (t**2 - r**2 - 1)**2 - 4*r**2
        beta  = (1 + r**2 - t**2 - np.sqrt(delta)) / (2*r)
        va    = (1 + r**2 - t**2 + np.sqrt(delta)) / (2*r)
        vb    = np.sqrt(beta*(va - r) / (va*(beta - r)))

        s1    = ra * (va*vb**(self.N - 1) - \
                va**(-1) * vb**(-(self.N - 1))) + \
                (ta*t - ra*r) * (vb**(self.N - 1) - \
                vb**(-(self.N - 1)))
        s2    = ta*(va - va**(-1))
        s3    = va*vb**(self.N - 1) - \
                va**(-1) * vb**(-(self.N - 1)) - \
                r*(vb**(self.N - 1) - vb**(-(self.N - 1)))

        refl  = s1/s3
        tran  = s2/s3

        self.leafopt.refl  = refl
        self.leafopt.trans = tran

        # Fluorescence stuff, beginning is still a black box in the doubling
        # method, need to comment on this and read more
        D    = np.sqrt((1 + refl + tran)
                * (1 + refl - tran)
                * (1 - refl + tran)
                * (1 - refl - tran))
        a    = (1 + refl**2. - tran**2. + D) / (2*refl)
        b    = (1 - refl**2. + tran**2 + D) / (2*tran)
        s    = 2*a / (a**2. - 1) * np.log(b)
        k    = (a-1) / (a+1) * np.log(b)
        kChl = self.leafopt.kChlrel * k

        # Interpolate k and s to absorption and emission wavelength (done as
        # indices in Matlab version, tried to make this more flexible as to
        # not having to keep the grid identical)
        ke  = np.interp(self.wlE, self._wl, k)
        kf  = np.interp(self.wlF, self._wl, k)
        se  = np.interp(self.wlE, self._wl, s)
        sf  = np.interp(self.wlF, self._wl, s)

        eps = 2**(-self.ndub)

        # Initializations
        te  = 1 - (ke + se) * eps
        tf  = 1 - (kf + sf) * eps
        re  = se * eps
        rf  = sf * eps

        # Matrix computed as an outproduct
        sigmoid = 1 / (1 + np.outer(np.exp(-self.wlF/10), np.exp(self.wlE/10)))

        # Other factor .5 deleted, since these are the complete efficiencies
        # for either PSI or PSII. not a linear combination

        # PSI matrices
        MfI  = self.fqe[0] * np.outer((0.5* \
                np.interp(self.wlF, self._wl, self.phiI)*eps), \
                np.interp(self.wlE, self._wl, kChl)) * sigmoid
        MbI  = MfI
        MfII = self.fqe[1] * np.outer((0.5* \
                np.interp(self.wlF, self._wl, self.phiII)*eps), \
                np.interp(self.wlE, self._wl, kChl)) * sigmoid
        MbII = MfII

        Ih   = np.ones((len(te),))     # Row of ones
        Iv   = np.ones((len(tf),))     # Column of ones

        # Doubling
        for i in range(self.ndub + 1):
            xe    = te / (1 - re*re)
            ten   = te*xe
            ren   = re*(1 + ten)

            xf    = tf / (1 - rf*rf)
            tfn   = tf*xf
            rfn   = rf*(1 + tfn)

            A11   = np.outer(xf,Ih) + np.outer(Iv,xe)
            A12   = np.outer(xf,xe) * (np.outer(rf,Ih) + np.outer(Iv,re))
            A21   = 1 + np.outer(xf,xe) * (1 + np.outer(rf,re))
            A22   = np.outer(xf*rf,Ih) + np.outer(Iv,xe*re)

            MfnI  = MfI  * A11 + MbI  * A12
            MbnI  = MbI  * A21 + MfI  * A22
            MfnII = MfII * A11 + MbII * A12
            MbnII = MbII * A21 + MfII * A22

            te    = ten
            re    = ren
            tf    = tfn
            rf    = rfn

            MfI   = MfnI
            MbI   = MbnI
            MfII  = MfnII
            MbII  = MbnII

        self.leafopt.MbI  = MbI
        self.leafopt.MbII = MbII
        self.leafopt.MfI  = MfI
        self.leafopt.MfII = MfII


    def writeOutput(self, param):
        """
        Write output from Fluspect module to file.
        """

        # Specify output directory
        output_dir   = library.create_output_dir(param, 'fluspect')

        # Specify time step
        step         = str(param.xyt.k)

        # Output computed quantities to file
        np.savetxt((output_dir + "/refl" + step + ".txt"), self.leafopt.refl)
        np.savetxt((output_dir + "/tran" + step + ".txt"), self.leafopt.trans)
        np.savetxt((output_dir + "/kChlrel" + step + ".txt"), \
                                                        self.leafopt.kChlrel)
        np.savetxt((output_dir + "/MbI" + step + ".txt"), self.leafopt.MbI)
        np.savetxt((output_dir + "/MbII" + step + ".txt"), self.leafopt.MbII)
        np.savetxt((output_dir + "/MfI" + step + ".txt"), self.leafopt.MfI)
        np.savetxt((output_dir + "/MfII" + step + ".txt"), self.leafopt.MfII)

        # Also write to file using pickle
        leafopt_file = output_dir + "/" + "leafopt" + step + ".pkl"
        library.write_pickle(leafopt_file, self.leafopt)


# EOF fluspect.py