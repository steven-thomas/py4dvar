#!/usr/bin/env python

###############################################################################
# Script library_output.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collection of defs for various data output operations.
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
import  os
import  math
import  numpy                           as np

import  pyscope.common.library_aux      as library

try:
    import cPickle as pickle
except:
    import pickle


def create_output_dat(param):
    """
    Create output files in the old SCOPE format, for backwards compatibility.
    Equivalent to the SCOPE script create_output_files.m.
    """

    # Specify output directory
    output_dir = library.create_output_dir(param, 'dat')

    # Create subdirectory for directional results
    if (param.options.calc_directional):

        brdf_subdir  = "Directional"
        brdf_fulldir = output_dir + "/" + brdf_subdir

        if not os.path.isdir(brdf_fulldir):

            print( "Creating directional output directory" )
            os.mkdir(brdf_fulldir)


    # Fluxes

    fidf = open(output_dir + '/fluxes.dat', 'w')

    if (param.options.save_headers):

        # Write header with variable names
        fidf.write('timestep counter year t Rntot lEtot Htot Rnctot lEctot ')
        fidf.write('Hctot Actot Rnstot lEstot Hstot Gtot Resp aPAR aPAR_Cab ')
        fidf.write('faPAR aPAR_energyunits')

        if (param.options.calc_fluor):

            fidf.write(' fluortot fluor_yield')

        fidf.write('\n')

        # Write header with units
        fidf.write('""        ""      ""  JulianDay  Wm-2   Wm-2 Wm-2 Wm-2 ')
        fidf.write('Wm-2   Wm-2 umolm-2s-1 Wm-2 Wm-2 Wm-2 Wm-2 umolm-2s-1 ')
        fidf.write('umolm-2s-1 umolumol-1 Wm-2 ')

        if (param.options.calc_fluor):

            fidf.write('W m-2 WW^{-1}')

        fidf.write('\n')

    fidf.close()

    # Surftemp

    fidt = open(output_dir + '/surftemp.dat', 'w')

    if (param.options.save_headers):

        fidt.write('timestep year t Ta Tss(1) Tss(2) Tcave Tsave \n')
        fidt.write('""        ""  JulianDay  ^oC ^oC ^oC ^oC ^oC \n')

    fidt.close()

    # Aerodyn

    fidra = open(output_dir + '/aerodyn.dat', 'w')

    if (param.options.save_headers):

        fidra.write('raa rawc raws ustar \n')
        fidra.write('sm-1 sm-1 sm-1 ms-1 \n')

    fidra.close()

    # Radiation

    fidr = open(output_dir + '/radiation.dat', 'w')

    if (param.options.save_headers):

        fidr.write('timestep year t HemisOutShort HemisOutLong HemisOutTot \n')
        fidr.write('""  ""  JulianDay  Wm-2 Wm-2 Wm-2 \n')

    fidr.close()

    # Wavelength

    # fidwl = open(output_dir + '/wl.dat', 'w')

    # if (param.options.save_headers):

    #     fidwl.write('wavelengths of the spectral output files \n')
    #     fidwl.write('um \n')

    # fidwl.close()

    # Fluorescence

    fidsi = open(output_dir + '/irradiance_spectra.dat', 'w')

    if (param.options.save_headers):

        fidsi.write('irradiance \n')
        fidsi.write('W m-2 um-1\n')

    fidsi.close()

    # Spectrum hemispherical

    fidfho = open(output_dir + '/spectrum_hemis_optical.dat', 'w')

    if (param.options.save_headers):

        fidfho.write('hemispherically integrated radiation spectrum \n')
        fidfho.write('W m-2 um-1 \n')

    fidfho.close()

    # Spectrum observation direction

    fidfoo = open(output_dir + '/spectrum_obsdir_optical.dat', 'w')

    if (param.options.save_headers):

        fidfoo.write('reflectance spectrum in observation direction \n')
        fidfoo.write('W m-2 sr-1 um-1 \n')

    fidfoo.close()

    # Reflectance spectrum

    fidref = open(output_dir + '/reflectance.dat', 'w')

    if (param.options.save_headers):

        fidref.write('reflectance \n')
        fidref.write('fraction of radiation in observation direction *pi / ')
        fidref.write('irradiance \n')

    fidref.close()

    # Spectrum observation direction (black body)

    if (param.options.calc_ebal):

        fidto = open(output_dir + '/spectrum_obsdir_BlackBody.dat', 'w')

        if (param.options.save_headers):

            fidto.write('thermal BlackBody emission spectrum in observation ')
            fidto.write('direction \n')
            fidto.write('W m-2 sr-1 um-1 \n')

        fidto.close()

        # Planck

        if (param.options.calc_planck):

            # Spectrum observation direction
            fidplancko = open(output_dir + '/spectrum_obsdir_thermal.dat', 'w')

            if (param.options.save_headers):

                fidplancko.write('thermal emission spectrum in observation ')
                fidplancko.write('direction \n')
                fidplancko.write('W m-2 sr-1 um-1 \n')

            fidplancko.close()

            # Sectrum hemispherically integrated
            fidplanckh = open(output_dir + '/spectrum_hemis_thermal.dat', 'w')

            if (param.options.save_headers):

                fidplanckh.write('thermal emission spectrum in hemispherical ')
                fidplanckh.write('direction \n')
                fidplanckh.write('W m-2 sr-1 um-1 \n')

            fidplanckh.close()

    # Profiles

    if (param.options.calc_vert_profiles):

        fidgp  = open(output_dir + '/gap.dat', 'w')

        if (param.options.save_headers):

            fidgp.write('Fraction leaves in the sun, fraction of observed, ')
            fidgp.write('fraction of observed & visible per layer \n')
            fidgp.write('rows: simulations or time steps, columns: layer ')
            fidgp.write('numbers \n')

        fidgp.close()

        fidtc  = open(output_dir + '/leaftemp.dat', 'w')

        if (param.options.save_headers):

            fidtc.write('leaf temperature of sunlit leaves, shaded leaves, ')
            fidtc.write('and weighted average leaf temperature per layer \n')
            fidtc.write('^oC ^oC ^oC \n')

        fidtc.close()

        fidhl  = open(output_dir + '/layer_H.dat', 'w')

        if (param.options.save_headers):

            fidhl.write('sensible heat flux per layer \n')
            fidhl.write('Wm-2 \n')

        fidhl.close()

        fidlel = open(output_dir + '/layer_lE.dat', 'w')

        if (param.options.save_headers):

            fidlel.write('latent heat flux per layer \n')
            fidlel.write('Wm-2 \n')

        fidlel.close()

        fidal  = open(output_dir + '/layer_A.dat', 'w')

        if (param.options.save_headers):

            fidal.write('photosynthesis per layer \n')
            fidal.write('umol-2s-1 \n')

        fidal.close()

        fidpl  = open(output_dir + '/layer_aPAR.dat', 'w')

        if (param.options.save_headers):

            fidpl.write('aPAR per leaf layer \n')
            fidpl.write('umol-2s-1 \n')

        fidpl.close()

        fidplC = open(output_dir + '/layer_aPAR_Cab.dat', 'w')

        if (param.options.save_headers):

            fidplC.write('aPAR by Cab per leaf layer \n')
            fidplC.write('umol-2s-1 \n')

        fidplC.close()

        fidrn  = open(output_dir + '/layer_Rn.dat', 'w')

        if (param.options.save_headers):

            fidrn.write('net radiation per leaf layer \n')
            fidrn.write('Wm-2 \n')

        fidrn.close()

        if (param.options.calc_fluor):

            fidfll   = open(output_dir + '/layer_fluorescence.dat', 'w')

            if (param.options.save_headers):

                fidfll.write('upward fluorescence per layer \n')
                fidfll.write('W m^{-2} \n')

            fidfll.close()

            fidfllem = open(output_dir + '/layer_fluorescenceEm.dat', 'w')

            fidfllem.close()

            fidNPQ   = open(output_dir + '/layer_NPQ.dat', 'w')

            if (param.options.save_headers):

                fidNPQ.write('average NPQ = 1-(fm-fo)/(fm0-fo0), ')
                fidNPQ.write('per layer \n')
                fidNPQ.write('\n')

            fidNPQ.close()

    # Fluorescence

    if (param.options.calc_fluor):

        fidfl  = open(output_dir + '/fluorescence.dat', 'w')

        if (param.options.save_headers):

            fidfl.write('fluorescence per simulation for wavelengths of ')
            fidfl.write('640 to 850 nm, with 1 nm resolution \n')
            fidfl.write('W m-2 um-1 sr-1 \n')

        fidfl.close()

        fidfl1 = open(output_dir + '/fluorescencePSI.dat', 'w')

        if (param.options.save_headers):

            fidfl1.write('fluorescence per simulation for wavelengths of ')
            fidfl1.write('640 to 850 nm, with 1 nm resolution, ')
            fidfl1.write('for PSI only \n')
            fidfl1.write('W m-2 um-1 sr-1 \n')

        fidfl1.close()

        fidfl2 = open(output_dir + '/fluorescencePSII.dat', 'w')

        if (param.options.save_headers):

            fidfl2.write('fluorescence per simulation for wavelengths of ')
            fidfl2.write('640 to 850 nm, with 1 nm resolution, ')
            fidfl2.write('for PSII only \n')
            fidfl2.write('W m-2 um-1 sr-1 \n')

        fidfl2.close()

        fidflh = open(output_dir + '/fluorescence_hemis.dat', 'w')

        if (param.options.save_headers):

            fidflh.write('hemispherically integrated fluorescence per ')
            fidflh.write('simulation for wavelengths of 640 to 850 nm, ')
            fidflh.write('with 1 nm resolution \n')
            fidflh.write('W m-2 um-1 \n')

        fidflh.close()


def write_output_dat(param, leafopt, gap, rad, profiles, thermal, fluxes, \
                     directional):
    """
    Write output to file in the old SCOPE file formats, for backwards
    compatibility. Equivalent to the SCOPE script output_data.m.
    """

    # Specify output directory
    output_base   = param.paths.output_base
    subdir  = "dat"
    output_dir    = output_base + "/" + subdir

    # Create output according to old SCOPE formatting and file names

    # Time dependence
    k             = param.xyt.k
    _iter_counter = param.xyt.iter_counter
    xyt_year_k    = param.xyt.year[k]
    xyt_t_k       = param.xyt.t[k]

    # Fluxes

    fidf = open(output_dir + '/fluxes.dat', 'a')

    fidf.write('%9.0f %9.0f %9.0f %9.4f %9.2f ' % \
              (k, _iter_counter, xyt_year_k, xyt_t_k, fluxes.Rntot))
    fidf.write('%9.2f %9.2f %9.2f %9.2f ' % \
              (fluxes.lEtot, fluxes.Htot, fluxes.Rnctot, fluxes.lEctot))
    fidf.write('%9.2f %9.2f %9.2f %9.2f ' % \
              (fluxes.Hctot, fluxes.Actot, fluxes.Rnstot, fluxes.lEstot))
    fidf.write('%9.2f %9.2f %9.2f %9.2f ' % \
              (fluxes.Hstot, fluxes.Gtot, fluxes.Resp, 1.0e6 * fluxes.aPAR))
    fidf.write('%9.2f %9.2f %9.2f ' % \
              (1.0e6 * fluxes.aPAR_Cab, fluxes.aPAR / rad.inPAR, \
               fluxes.aPAR_Wm2))

    if (param.options.calc_fluor):

        fidf.write('%9.4f %9.6f ' % (rad.Eoutf, rad.Eoutf / fluxes.aPAR_Wm2))

    fidf.write('\n')
    fidf.close()

    # Surftemp

    fidt = open(output_dir + '/surftemp.dat', 'a')
    fidt.write('%9.0f  %9.0f %9.4f % 9.2f %9.2f ' % \
              (k, xyt_year_k, xyt_t_k, thermal.Ta, thermal.Ts[0]))
    fidt.write('%9.2f %9.2f  %9.2f \n' % \
              (thermal.Ts[1], thermal.Tcave, thermal.Tsave))
    fidt.close()

    # Aerodyn

    fidra = open(output_dir + '/aerodyn.dat', 'a')
    fidra.write('%15.4f %15.4f %15.4f %15.4f \n' % \
               (thermal.raa, thermal.rawc, thermal.raws, thermal.ustar))
    fidra.close()

    # Radiation

    fidr = open(output_dir + '/radiation.dat', 'a')
    fidr.write('%9.0f  %9.0f %9.4f % 9.2f ' % \
              (k, xyt_year_k, xyt_t_k, rad.Eouto))
    fidr.write('%9.2f  %9.2f \n' % \
              (rad.Eoutt + rad.Eoutte, rad.Etoto))
    fidr.close()

    # Spectrum

    fidfho = open(output_dir + '/spectrum_hemis_optical.dat', 'a')
    rad.Eout_.tofile(fidfho, sep=' ', format='%9.5f')
    fidfho.write('\n')
    fidfho.close()

    fidfoo = open(output_dir + '/spectrum_obsdir_optical.dat', 'a')
    rad.Lo_.tofile(fidfoo, sep=' ', format='%9.5f')
    fidfoo.write('\n')
    fidfoo.close()

    if (param.options.calc_ebal):

        fidto = open(output_dir + '/spectrum_obsdir_BlackBody.dat', 'a')
        rad.LotBB_.tofile(fidto, sep=' ', format='%9.2f')
        fidto.write('\n')
        fidto.close()

        if (param.options.calc_planck):

            fidplanckh = open(output_dir + '/spectrum_hemis_thermal.dat', \
                              'a')
            rad.Eoutte_.tofile(fidplanckh, sep=' ', format='%9.2f')
            fidplanckh.write('\n')
            fidplanckh.close()


            fidplancko = open(output_dir + '/spectrum_obsdir_thermal.dat', \
                              'a')
            rad.Lot_.tofile(fidplancko, sep=' ', format='%9.2f')
            fidplancko.write('\n')
            fidplancko.close()

    # Reflectance

    fidsi = open(output_dir + '/irradiance_spectra.dat', 'a')

    irrad = param.meteo.Rin * (rad.fEsuno + rad.fEskyo).T

    irrad.tofile(fidsi, sep=' ', format='%10.2f')
    fidsi.write('\n')
    fidsi.close()

    fidref = open(output_dir + '/reflectance.dat', 'a')

    reflectance = math.pi * rad.Lo_ / (rad.Esun_ + rad.Esky_)
    reflectance[param.spectral.wlS > 3000] = np.nan

    reflectance.tofile(fidref, sep=' ', format='%9.5f')
    fidref.write('\n')
    fidref.close()

    # Profiles

    if (param.options.calc_vert_profiles):

        fidgp = open(output_dir + '/gap.dat', 'a')
        gap_var = np.asarray([gap.Ps, gap.Po, gap.Pso])
        gap_var.tofile(fidgp, sep=' ', format='%9.2f')
        fidgp.write('\n')
        fidgp.close()

        fidpl = open(output_dir + '/layer_aPAR.dat', 'a')
        pl_var = 1.0e6 * profiles.Pn1d
        pl_var.tofile(fidpl, sep=' ', format='%9.2f')
        fidpl.write('\n')
        fidpl.close()

        fidplC = open(output_dir + '/layer_aPAR_Cab.dat', 'a')
        plC_var = 1.0e6 * profiles.Pn1d_Cab
        plC_var.tofile(fidplC, sep=' ', format='%9.2f')
        fidplC.write('\n')
        fidplC.close()

        if (param.options.calc_ebal):

            fidtc = open(output_dir + '/leaftemp.dat', 'a')
            tc_var = np.asarray([profiles.Tcu1d, profiles.Tch, profiles.Tc1d])
            tc_var.tofile(fidtc, sep=' ', format='%9.2f')
            fidtc.write('\n')
            fidtc.close()

            fidhl = open(output_dir + '/layer_h.dat', 'a')
            profiles.Hc1d.tofile(fidhl, sep=' ', format='%9.2f')
            fidhl.write('%9.2f \n' % (fluxes.Hstot))
            fidhl.close()

            fidlel = open(output_dir + '/layer_le.dat', 'a')
            profiles.lEc1d.tofile(fidlel, sep=' ', format='%9.2f')
            fidlel.write('%9.2f \n' % (fluxes.lEstot))
            fidlel.close()

            fidal = open(output_dir + '/layer_a.dat', 'a')
            profiles.A1d.tofile(fidal, sep=' ', format='%9.2f')
            fidal.write('%9.2f \n' % (fluxes.Resp))
            fidal.close()

            fidNPQ = open(output_dir + '/layer_NPQ.dat', 'a')
            profiles.qE.tofile(fidNPQ, sep=' ', format='%9.2f')
            fidNPQ.write('\n')
            fidNPQ.close()

            fidrn = open(output_dir + '/layer_rn.dat', 'a')
            profiles.Rn1d.tofile(fidrn, sep=' ', format='%9.2f')
            fidrn.write('%9.2f \n' % (fluxes.Rnstot))
            fidrn.close()

        if (param.options.calc_fluor):

            fidfll = open(output_dir + '/layer_fluorescence.dat', 'a')
            profiles.fluorescence.tofile(fidfll, sep=' ', format='%9.2f')
            fidfll.write('\n')
            fidfll.close()


    # Fluorescence

    if (param.options.calc_fluor):

        fidfl  = open(output_dir + '/fluorescence.dat', 'a')
        fidfl1 = open(output_dir + '/fluorescencePSI.dat', 'a')
        fidfl2 = open(output_dir + '/fluorescencePSII.dat', 'a')
        fidflh = open(output_dir + '/fluorescence_hemis.dat', 'a')

        # Only valid for non-standard conditions where wlF is not a 1-D vector?
        # for j in np.arange(0, np.shape(param.spectral.wlF)[1]):

        rad.LoF_.tofile(fidfl, sep=' ', format='%10.4f')
        rad.LoF1_.tofile(fidfl1, sep=' ', format='%10.4f')
        rad.LoF2_.tofile(fidfl2, sep=' ', format='%10.4f')
        rad.Fhem_.tofile(fidflh, sep=' ', format='%10.4f')

        fidfl.write('\n')
        fidfl1.write('\n')
        fidfl2.write('\n')
        fidflh.write('\n')

        fidfl.close()
        fidfl1.close()
        fidfl2.close()
        fidflh.close()


    # Directional
    if (param.options.calc_directional & param.options.calc_ebal):

        Output_angle = np.asarray([ [directional.tto.T], [directional.psi.T], \
                         [param.angles.tts * \
                          np.ones(np.size(directional.psi.T))] ])

        Output_brdf = np.column_stack((param.spectral.wlS.T, \
                                       directional.brdf_))

        if (param.options.calc_planck):

            Output_temp  = np.column_stack((param.spectral.wlT.T, \
                                            directional.Lot_))

        else:

            Output_temp  = np.asarray([directional.BrightnessT])

        if (param.options.calc_fluor):

            Output_fluor = np.column_stack((param.spectral.wlF.T, \
                                            directional.LoF_))

        brdf_file = output_dir + '/Directional' + \
                    '/BRDF (SunAngle %2.2f degrees).dat' % (param.angles.tts)
        fbrdf = open(brdf_file, 'w')
        Output_brdf.tofile(fbrdf, sep=' ', format='%9.4f')
        fbrdf.close()

        angle_file = output_dir + '/Directional' + \
                    '/Angles (SunAngle %2.2f degrees).dat' % (param.angles.tts)
        fangle = open(angle_file, 'w')
        Output_angle.tofile(fangle, sep=' ', format='%9.4f')
        fangle.close()

        temp_file = output_dir + '/Directional' + \
                    '/Temperatures (SunAngle %2.2f degrees).dat' % \
                    (param.angles.tts)
        ftemp = open(temp_file, 'w')
        Output_temp.tofile(ftemp, sep=' ', format='%9.4f')
        ftemp.close()


        if (param.options.calc_fluor):

            fluor_file = output_dir + '/Directional' + \
                         '/Fluorescence (SunAngle %2.2f degrees).dat' % \
                         (param.angles.tts)
            ffluor = open(fluor_file, 'w')
            Output_fluor.tofile(ffluor, sep=' ', format='%9.4f')
            ffluor.close()


        fiddirtir = open(output_dir + '/Directional' + '/readme.txt', 'w')

        fiddirtir.write('The Directional data is written in three files: \n')

        fiddirtir.write('\n- Angles: contains the directions. \n')
        fiddirtir.write('   * The 1st row gives the observation zenith  ')
        fiddirtir.write('angles \n')
        fiddirtir.write('   * The 2nd row gives the observation azimuth ')
        fiddirtir.write('angles \n')
        fiddirtir.write('   * The 3rd row gives the solar       zenith  ')
        fiddirtir.write('angles \n')

        fiddirtir.write('\n- Temperatures: contains the directional ')
        fiddirtir.write('brightness temperature. \n')
        fiddirtir.write('   * The 1st column gives the wl values ')
        fiddirtir.write('corresponding to the brightness temperature ')
        fiddirtir.write('values (except for broadband) \n')
        fiddirtir.write('   * The 2nd column gives the Tb values ')
        fiddirtir.write('corresponding to the directions given by first ')
        fiddirtir.write('column in the Angles file \n')

        fiddirtir.write('\n- BRDF: contains the bidirectional distribution ')
        fiddirtir.write('functions values. \n')
        fiddirtir.write('   * The 1st column gives the wl values ')
        fiddirtir.write('corresponding to the BRDF values \n')
        fiddirtir.write('   * The 2nd column gives the BRDF values ')
        fiddirtir.write('corresponding to the directions given by first ')
        fiddirtir.write('column in the Angles file \n')

        fiddirtir.close()


def write_output_list(output_dir, leafopt, gap, rad, profiles, thermal, fluxes, \
                      directional):
    """
    Write output lists to single files
    """

    # Ensure output directory exists
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Leafopt
    leafopt_file = output_dir + "/leafopt.pkl"
    library.write_pickle(leafopt_file, leafopt)

    # Gap
    gap_file   = output_dir + "/gap.pkl"
    library.write_pickle(gap_file, gap)

    # Fluxes
    fluxes_file = output_dir + '/fluxes.pkl'
    library.write_pickle(fluxes_file, fluxes)

    # Thermal
    thermal_file = output_dir + '/thermal.pkl'
    library.write_pickle(thermal_file, thermal)

    # Rad
    rad_file = output_dir + "/rad.pkl"
    library.write_pickle(rad_file, rad)

    # Profiles
    profiles_file = output_dir + "/profiles.pkl"
    library.write_pickle(profiles_file, profiles)
    
    # Directional
    directional_file = output_dir + "/directional.pkl"
    library.write_pickle(directional_file, directional)


# EOF library_output.py
