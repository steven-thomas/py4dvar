
#!/usr/bin/env python

###############################################################################
# Script pySCOPE.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: calls individual pySCOPE modules via run scripts.
# Note: this script corresponds to SCOPE_mac_linux.m in SCOPE.
#
# Usage: python pySCOPE.py user_input.cfg
#
# Input (optional): user parameter file (user_input.cfg or subset of it)
#
# Author:
# Laura Alisic Jewell <Laura.A.Jewell@jpl.nasa.gov>, Jet Propulsion Laboratory
#
# Copyright (c) 2015-2016, California Institute of Technology.
# ALL RIGHTS RESERVED. This work is supported in part by the W.M. Keck 
# Institute for Space Studies.
#
###############################################################################
# SPT modification: only accepts single time step (param.options.simulation == 0)

# Imports
import  sys
#SPT add to path to allow 'import pyscope....'
sys.path.append('..')
from    pyscope.config                          import run_config
from    pyscope.fluspect                        import run_fluspect
from    pyscope.rtmo                            import run_rtmo
from    pyscope.ebal                            import run_ebal
from    pyscope.rtmf                            import run_rtmf
from    pyscope.rtmt                            import run_rtmt_planck
from    pyscope.brdf                            import run_brdf
from    pyscope.io_wrapper.output_controller    import OutputController

import  pyscope.common.library_aux      as library
import  pyscope.common.library_output   as library_output
import  pyscope.common.library_physics  as physics


###############################################################################
# MODULES
###############################################################################

def run_scope( param ):

    # Run Fluspect
    library.start_timestamp("Fluspect")
    leafopt = run_fluspect.runFluspect(param)
    library.end_timestamp("Fluspect")


    # Run RTMo
    library.start_timestamp("RTMo")
    leafopt, gap, rad, profiles = run_rtmo.runRTMo(param, leafopt)
    library.end_timestamp("RTMo")


    # Run Ebal
    if (param.options.calc_ebal):

        library.start_timestamp("Ebal")
        fluxes, rad, profiles, thermal, biochem_out = run_ebal.runEbal(param, leafopt, \
                                                                       gap, rad, profiles)
        library.end_timestamp("Ebal")

    else:

        library.start_timestamp("Fluxes without Ebal")
        fluxes, thermal = physics.compute_fluxes(param, gap, rad)
        library.end_timestamp("Fluxes without Ebal")


    # Run RTMf
    if (param.options.calc_fluor):

        library.start_timestamp("RTMf")
        rad, profiles = run_rtmf.runRTMf(param, leafopt, gap, rad, profiles)
        library.end_timestamp("RTMf")


    # Run RTMt_Planck only with ebal
    if (param.options.calc_ebal & param.options.calc_planck):

        library.start_timestamp("RTMt_Planck")
        rad = run_rtmt_planck.runRTMt_planck(param, leafopt, gap, rad, thermal)
        library.end_timestamp("RTMt_Planck")


    # Run BRDF only with ebal
    if (param.options.calc_ebal & param.options.calc_directional):

        library.start_timestamp("BRDF")
        directional = run_brdf.runBRDF(param, leafopt, gap, rad, thermal, \
                                       profiles)
        library.end_timestamp("BRDF")

    else:

        directional = None

    ## Write output in SCOPE file formats for backward compatibility
    #library.start_timestamp("Output")
    #library_output.write_output_dat(param, leafopt, gap, rad, profiles, \
    #                                thermal, fluxes, directional)
    #library.end_timestamp("Output")
    # Write output_lists in single files
    library.start_timestamp("Output")
    output = OutputController( leafopt, gap, rad, profiles, thermal, fluxes, \
                               directional)
    library.end_timestamp("Output")


    ###############################################################################
    # FINISH
    ###############################################################################

    # TODO: any need for diagnostics here?

    return output

# EOF pySCOPE.py
