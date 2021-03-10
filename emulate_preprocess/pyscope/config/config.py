#!/usr/bin/env python

###############################################################################
# Script config.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collect all parameter inputs for the pySCOPE simulation.
#
# Usage: python config.py
#
# Input: user specified input file.
#
# Output: structure with all input parameters.
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

# Imports
import  sys
import  datetime
import  os, os.path
import  pprint
import  types
import  numpy                           as np
from    scipy.interpolate               import interp1d

# Class to define empty structure
from    pyscope.common.structures       import emptyStruct

# Simulation options
import  pyscope.config.default_options  as options

# Get simulation parameter values
import  pyscope.config.default_values   as default_values

# Defs that compute input parameters
import  pyscope.common.compute_input    as compute_input

# Get library of various functions
import  pyscope.common.library_aux      as library

# Get library of physics functions
import  pyscope.common.library_physics  as physics

# Get output library
import  pyscope.common.library_output   as library_output

# Global constants
import  pyscope.common.global_constants as const


class Config():
    """
    Initializes pySCOPE simulation and parses default and user-provided input
    to the simulation.
    """

    def __init__(self):
        """
        Prepare for parameter initialization.
        """

        self.param = emptyStruct()


#    def initRun(self, sys_argv):
    def initRun(self, user_file):
        """
        Initialize pySCOPE simulation, print start time, and check for a
        user specified input file.
        """

        # No user input specified, defaults are used
        if (user_file is None):

            self.user_file = "None"
            print( "No user input specified. Default parameters used." )

        # User input file is specified on the commandline
        else:

            self.user_file = user_file

            # Test for file existence and access
            if os.path.isfile(self.user_file) and os.access(self.user_file, \
                                                            os.R_OK):

                print( "File", self.user_file, "exists and is readable." )

            else:

                print( "File", self.user_file, "is missing or is not readable." )
                self.user_file = "None"


    def parseDefaults(self):
        """
        Parse default parameters from default_values.py and
        simulation_options.py into a dictionary.
        """

        self.param.angles      = default_values.default_angles()
        self.param.atmo        = default_values.default_atmo()
        self.param.canopy      = default_values.default_canopy()
        self.param.directional = default_values.default_directional()
        self.param.leafbio     = default_values.default_leafbio()
        self.param.meteo       = default_values.default_meteo()
        self.param.numiter     = default_values.default_numiter()
        self.param.optipar     = default_values.default_optipar()
        self.param.paths       = default_values.default_paths()
        self.param.soil        = default_values.default_soil()
        self.param.spectral    = default_values.default_spectral()
        self.param.xyt         = default_values.default_xyt()
        self.param.options     = options


    def parseUserInput(self):
        """
        Parse a 'key = value' style input file provided by user, and create a
        dictionary of those settings
        """

        # Dictionary to hold user-defined input parameters
        self.settings = {}

        # Skip the rest of this function if no user file defined
        if (self.user_file == "None"):

            # Store user file "None" in data structure
            self.param.paths.user_file = self.user_file

        # If user file defined, go through parsing it
        else:

            param_file = open(self.user_file, "r")

            # Read file into a list of lines
            try:

                lines = param_file.read().splitlines()

            finally:

                param_file.close()

            # Process each line
            for line in lines:

                # Skip blank lines
                if line.strip() == '':

                    continue

                # Skip comment lines starting with '#'
                if line.startswith('#'):

                    continue

                # Skip lines that have no '='
                if not "=" in line:

                    continue

                # Cut off any comments preceded by '#' from the string,
                # a1 and a2 are ignored
                (opt, a1, a2) = line.partition('#')

                # Skip lines that have only blank spaces before '#'
                if opt.strip() == '':

                    continue

                # Isolate the key and value (which can be a list)
                opt = opt.split()
                key = opt[0]
                val = opt[2:len(opt)]

                # Store in dictionary with correct data type
                val = library.int_float_string(val)

                # Store as key val pair
                self.settings[key] = val


    def mergeInput(self):
        """
        Merge user provided input with default structure, by overwriting the
        default value if provided in the correct datatype.
        """

        # Loop over key/value pairs in the user settings dictionary
        for key in sorted(self.settings.keys()):

            # For each key, get value
            val = self.settings[key]

            # Check if the corresponding default value exists in self.param
            try:

                val_old = library.getattr_qualified(self.param, key)

                # Test if user defined value is different from default
                if not (val == val_old):

                    # If default value exists and is different from user value,
                    # overwrite value with user supplied value
                    library.setattr_qualified(self.param, key, val)

                    if (self.settings["options.log_level"] == 1):

                        msg = "User changed {:} from {:} (default) to {:}"
                        print( msg.format(key,val_old,val) )

                else:

                    if (self.settings["options.log_level"] == 1):

                        print( "Default: {:} = {:}".format(key,val) )

            # If default value does not exist, print message and continue
            except AttributeError:

                print( "User supplied parameter {:} does not exist!".format(key) )

        # Store user file in data structure
        self.param.paths.user_file = self.user_file


    def processTime(self):
        """
        Process time series data if simulation type = 1.
        """

        # TODO: Include debugging output for log option 1

        # Equivalent to the SCOPE script load_timeseries.m

        if (self.param.options.simulation == 1):

            # Process time series files
            print( "Processing time series data ..." )

            xyt      = self.param.xyt

            # Data direction location
            data_dir = self.param.paths.input + 'dataset ' + xyt.Dataset_dir

            # Data files
            t_file     = data_dir + '/' + xyt.t_file
            year_file  = data_dir + '/' + xyt.year_file
            Rin_file   = data_dir + '/' + xyt.Rin_file
            Rli_file   = data_dir + '/' + xyt.Rli_file
            p_file     = data_dir + '/' + xyt.p_file
            Ta_file    = data_dir + '/' + xyt.Ta_file
            ea_file    = data_dir + '/' + xyt.ea_file
            u_file     = data_dir + '/' + xyt.u_file
            CO2_file   = data_dir + '/' + xyt.CO2_file
            z_file     = data_dir + '/' + xyt.z_file
            tts_file   = data_dir + '/' + xyt.tts_file
            LAI_file   = data_dir + '/' + xyt.LAI_file
            hc_file    = data_dir + '/' + xyt.hc_file
            SMC_file   = data_dir + '/' + xyt.SMC_file
            Vcmax_file = data_dir + '/' + xyt.Vcmax_file
            Cab_file   = data_dir + '/' + xyt.Cab_file


            # Time and zenith angle
            self.param.xyt.t    = np.loadtxt(t_file)
            self.param.xyt.year = np.loadtxt(year_file)

            t_       = self.param.xyt.t
            DOY_     = np.floor(t_)
            time_    = 24.0 * (self.param.xyt.t - DOY_)

            if (xyt.tts_file == "None"):

                # Compute sun zenith angle in radians
                Omega_g = 0.0
                Fi_gm   = 0.0

                # Only use first returned variable
                ttsR, a1, a2, a3  = physics.calczenithangle(DOY_, \
                                        time_ - xyt.timezn, Omega_g, Fi_gm, \
                                        xyt.LON, xyt.LAT)

                # Convert to degrees
                self.param.xyt.tts  = np.minimum(85.0, ttsR / const.deg2rad)

            else:

                tts_file = data_dir + '/' + xyt.tts_file
                self.param.xyt.tts  = np.loadtxt(tts_file)


            # Radiation
            self.param.xyt.Rin    = np.loadtxt(Rin_file)
            self.param.xyt.Rli    = np.loadtxt(Rli_file)


            # Wind speed, air temperature, humidity and air pressure
            self.param.xyt.u      = np.loadtxt(u_file)         # Wind speed
            self.param.xyt.Ta     = np.loadtxt(Ta_file)
            self.param.xyt.ea     = np.loadtxt(ea_file)

            if (xyt.p_file == "None"):

                self.param.xyt.p  = 1.0e3 * np.ones((np.size(t_),))

            else:

                self.param.xyt.p  = np.loadtxt(p_file)


            # Vegetation structure (measurement height, vegetation height
            # and LAI)

            if (xyt.z_file == "None"):

                self.param.xyt.z  = self.param.meteo.z * \
                                        np.ones((np.size(t_),))

            else:

                ztable = np.loadtxt(z_file)
                self.param.xyt.z  = interp1d(ztable[:, 0], ztable[:, 1])(t_)


            if (xyt.LAI_file == "None"):

                self.param.xyt.LAI  = self.param.canopy.LAI * \
                                        np.ones((np.size(t_),))

            else:

                LAItable = np.loadtxt(LAI_file)
                self.param.xyt.LAI  = interp1d(LAItable[:, 0], \
                                               LAItable[:, 1])(t_)


            if (xyt.hc_file == "None"):

                self.param.xyt.hc  = self.param.canopy.hc * \
                                        np.ones((np.size(t_),))
                self.param.xyt.zo  = self.param.meteo.zo * \
                                        np.ones((np.size(t_),))
                self.param.xyt.d   = self.param.meteo.d * \
                                        np.ones((np.size(t_),))

            else:

                hctable = np.loadtxt(hc_file)
                self.param.xyt.hc  = interp1d(hctable[:, 0], \
                                        hctable[:, 1])(t_)

                # Is this ok to overwrite?
                self.param.canopy.hc = self.param.xyt.hc

                if (self.param.options.calc_zo):

                    self.param.xyt.zo, self.param.xyt.d = \
                                        physics.zo_and_d(self.param.soil, \
                                                         self.param.canopy)

                else:

                    self.param.xyt.zo = self.param.meteo.zo * \
                                            np.ones((np.size(t_),))
                    self.param.xyt.d  = self.param.meteo.d * \
                                            np.ones((np.size(t_),))


            # Gas concentrations

            if (xyt.CO2_file == "None"):

                self.param.xyt.Ca = 380.0 * np.ones((np.size(t_),))

            else:

                Ca_ =  np.loadtxt(CO2_file)

                # Conversion from mg m-3 to ppm:
                # mg(CO2)/m-3 * g(air)/mol(air) * mol(CO2)/g(CO2) *
                # m3(air)/kg(air) * 10^-3 g(CO2)/mg(CO2) *
                # 10^-3 kg(air)/g(air) * 10^6 ppm

                self.param.xyt.Ca  = Ca_ * const.Mair / const.MCO2 / const.rhoa

                # Overwrite NaN's with constant value
                jj  = np.isnan(Ca_)
                self.param.xyt.Ca[jj] = 380.0


            # Soil moisture content

            if (xyt.SMC_file == "None"):

                pass

            else:

                self.param.xyt.Tyear = np.loadtxt(SMC_file)


            # Leaf biochemical parameters

            if (xyt.Vcmax_file == "None"):

                self.param.xyt.Vcmo = self.param.leafbio.Vcmo * \
                                        np.ones((np.size(t_),))

            else:

                Vcmotable = np.loadtxt(Vcmax_file)
                self.param.xyt.Vcmo  = interp1d(Vcmotable[:, 0], \
                                                Vcmotable[:, 1])(t_)


            if (xyt.Cab_file == "None"):

                self.param.xyt.Cab   = self.param.leafbio.Cab * \
                                            np.ones((np.size(t_),))

            else:

                Cabtable  = np.loadtxt(Cab_file)
                self.param.xyt.Vcmo  = interp1d(Cabtable[:, 0], \
                                            Cabtable[:, 1])(t_)


            # Compute number of time steps
            self.param.xyt.telmax    = np.size(t_)

            print( "... Done." )

        else:

            # No time stepping, step counter is 1
            self.param.xyt.telmax    = 1

            # Dummy output
            self.param.xyt.k         = 0
            self.param.xyt.t         = [0.0]
            self.param.xyt.year      = [0]


    def computeParam(self):
        """
        Compute additional parameters that are inserted in the global param
        data structure.
        """

        # Spectral must be computed first, other structs depend on it
        self.param.spectral    = compute_input.define_spectral(self.param)

        # Soil is also used in a few other structs
        self.param.soil        = compute_input.define_soil(self.param)

        self.param.directional = compute_input.define_directional(self.param)
        self.param.atmo        = compute_input.define_atmo(self.param)
        self.param.canopy      = compute_input.define_canopy(self.param)
        self.param.leafbio     = compute_input.define_leafbio(self.param)
        self.param.optipar     = compute_input.define_optipar(self.param)

        # Compute additional parameters needed for time series
        if (self.param.options.simulation == 1):

            self.param.xyt         = compute_input.define_xyt(self.param)


    def createOutput(self):
        """
        Create output files in the old SCOPE format, for backwards
        compatibility. Equivalent to the SCOPE script create_output_files.m.
        """

        library_output.create_output_dat(self.param)


    def writeLog(self):
        """
        Output the merged input parameter structure to file.
        """

        # Log file
        output_base = self.param.paths.output_base
        logname     = self.param.paths.logname
        logfile     = output_base + "/" + logname

        # Test if output directory exists
        if not os.path.isdir(output_base):

            # If output directory does not exist, create it
            os.mkdir(output_base)

        # Collect all non-built-in 1st level attributes from parameter
        # structure
        library.print_input_struct(self.param, logfile)

        # Also store as pickle file
        # param_file = output_base + "/" + "param.pkl"

        # library.write_pickle(param_file, self.param)


# EOF config.py
