#!/usr/bin/env python

###############################################################################
# Script library_aux.py
#
# Part of the pySCOPE package:
# Python port of the SCOPE model by van der Tol et al.
#
# Purpose: collection of defs for various auxiliary code operations.
# All physics related functions are in library_physics.py
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
import  datetime
import  math
import  numpy               as np
import  pprint
import  types

try:

    import  cPickle         as pickle

except:

    import  pickle


def abc(a, b, c):
    """
    ABC formula.
    """

    if (a == 0):

        x1 = -c / b
        x2 = x1

    else:

        x1 = (-b + np.sqrt(b ** 2 - 4.0 * a * c)) / (2.0 * a)
        x2 = (-b - np.sqrt(b ** 2 - 4.0 * a * c)) / (2.0 * a)

    return x2, x1


def create_output_dir(param, module_dir):
    """
    Check for existence of module output subdirectory; create if it does not
    exist
    """

    # Specify output directories
    output_base   = param.paths.output_base
    output_dir    = output_base + "/" + module_dir

    # Test if output/fluspect directory exists
    if not os.path.isdir(output_dir):

        print( "Creating output directory" )

        if not os.path.isdir(output_base):

            # If output directory does not exist, create it
            os.mkdir(output_base)

        # If module directory does not exist, create it
        os.mkdir(output_dir)

    return output_dir


def getattr_qualified(obj, name):
    """
    Get value of attribute with fully qualified name (e.g. param.field).
    """

    for attr in name.split("."):

        obj = getattr(obj, attr)

    return obj


def setattr_qualified(obj, name, value):
    """
    Set value of attribute with fully qualified name (e.g. param.field).
    """

    parts = name.split(".")

    for attr in parts[:-1]:

        obj = getattr(obj, attr)

    setattr(obj, parts[-1], value)


def int_float_string(val):
    """
    Convert string values to correct type if int or float. Parse list of
    strings if needed.
    """

    # TODO: Can this be done more efficiently?

    # Check if val is list of values
    for i in range(len(val)):

        # Strip characters: [,]
        val_new = val[i].replace("[","")
        val_new = val_new.replace(",","")
        val_new = val_new.replace("]","")

        # Integer?
        if val_new.isdigit():

           val_new = int(val_new)

        else:
            # Float?
            try:

                val_new = float(val_new)

            # Else assume string and do nothing
            except ValueError:

                pass

        # If val has single value, don't make list
        if (len(val) == 1):

            val_out = val_new

        # If val has more values, return list
        else:

            if (i == 0):

                # If first item in list, make new list
                val_out = [val_new]

            else:

                # If later item, append to existing list
                val_out.append(val_new)

    return val_out


def print_input_struct(struct, outname):
    """
    Print the contents of the input data structure struct to output file with
    name outname.
    """

    outfile = open(outname, "w")

    attributes = [attr for attr in dir(struct) \
                if not attr.startswith('__')]

    for i in attributes:

        # Get names of 2nd level attributes in each 1st level attribute
        varname = getattr_qualified(struct, i)

        # Collect all non-built-in 2nd level attributes from structure
        sub_attributes = [subattr for subattr in dir(varname) \
                          if not subattr.startswith('__')]

        data = []

        # Make list for printing of all parameters
        for j in sub_attributes:

            # Get corresponding value of parameter
            val = getattr_qualified(varname, j)

            # Leave out all built-in methods
            if not isinstance(val, types.BuiltinMethodType):

                data.append([j, val])

        # Output data
        pp = pprint.PrettyPrinter(indent = 4)
        outfile.write("\n%s\n" % (i))
        outfile.write(pp.pformat(data))
        outfile.write("\n")

    return


def print_struct(struct, outname):
    """
    Print the contents of a data structure struct to output file with name
    outname.
    """

    # Prevent longer arrays to get truncated with '...' in the output
    # np.set_printoptions(threshold=np.nan)

    outfile = open(outname, "w")

    attributes = [attr for attr in dir(struct) \
                if not attr.startswith('__')]

    data = []

    for varname in attributes:

        # Get names of 2nd level attributes in each 1st level attribute
        val = getattr_qualified(struct, varname)

        data.append([varname, val])

    # Output data
    pp = pprint.PrettyPrinter(indent = 4)
    outfile.write(pp.pformat(data))

    return


def print_screen_struct(struct):
    """
    Print the contents of a data structure struct to screen. Useful in
    interactive mode using iPython.
    """

    # Prevent longer arrays to get truncated with '...' in the output
    # np.set_printoptions(threshold=np.nan)

    attributes = [attr for attr in dir(struct) \
                if not attr.startswith('__')]

    data = []

    for varname in attributes:

        # Get names of 2nd level attributes in each 1st level attribute
        val = getattr_qualified(struct, varname)

        data.append([varname, val])

    # Output data to screen
    pprint.pprint(data)

    return


def Sint(y, x):
    """
    Simpson integration.
    x and y can be any vectors (rows, columns), but of the same length;
    x must be a monotonically increasing series
    """

    nx = np.shape(x)[0]

    step     = x[1:nx] - x[0:nx-1]
    mean     = 0.5 * (y[0:nx-1] + y[1:nx])

    integral = np.inner(mean, step)

    return integral


def start_timestamp(script):
    """
    Print message at beginning of a module with a timestamp
    """

    now = datetime.datetime.now()

    print ("\n======== Running module: %s" % (script))
    print ("Starting module %s on %s" \
            % (script, now.strftime("%Y/%m/%d %H:%M:%S")))


def end_timestamp(script):
    """
    Print message at end of a module with a timestamp
    """

    now = datetime.datetime.now()

    print ("Finishing module %s on %s" \
            % (script, now.strftime("%Y/%m/%d %H:%M:%S")))


def timestepVariables(param, step):
    """
    Function that at the beginning of each time step pulls the required values
    out of xyt time series and overwrites the appropriate constants in the
    param structure.
    """

    param.angles.tts    = param.xyt.tts[step]

    param.meteo.Rin     = param.xyt.Rin[step]
    param.meteo.Rli     = param.xyt.Rli[step]
    param.meteo.u       = param.xyt.u[step]
    param.meteo.Ta      = param.xyt.Ta[step]
    param.meteo.ea      = param.xyt.ea[step]
    param.meteo.p       = param.xyt.p[step]
    param.meteo.z       = param.xyt.z[step]
    param.meteo.zo      = param.xyt.zo[step]
    param.meteo.d       = param.xyt.d[step]
    param.meteo.Ca      = param.xyt.Ca[step]

    param.canopy.LAI    = param.xyt.LAI[step]
    param.canopy.hc     = param.xyt.hc[step]

    if (param.xyt.SMC_file != "None"):

        param.leafbio.Tyear = param.xyt.Tyear[step]

    param.leafbio.Vcmo  = param.xyt.Vcmo[step]
    param.leafbio.Cab   = param.xyt.Cab[step]

    # Store time step in param for logging purposes
    param.xyt.k         = step

    # Calculate data quality flag
    data_quality_flag   = 1 - np.isnan(param.meteo.p * param.meteo.Ta * \
                                       param.meteo.ea * param.meteo.u * \
                                       param.meteo.Rin * param.meteo.Rli)

    # Only set compute flag to 1 if data quality is sufficient and dates are
    # within range
    compute_flag = 0

    if ((step >= param.xyt.I_tmin) & (step <= param.xyt.I_tmax)):

        compute_flag = data_quality_flag

    return param, compute_flag


def write_pickle(file, obj):
    """
    Write obj to file using pickle
    """

    with open(file, "wb") as f:

        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


# EOF library_aux.py
