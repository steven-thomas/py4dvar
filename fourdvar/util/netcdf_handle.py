"""
extension: toolkit for interacting with netCDF files
"""

import numpy as np
import os
import shutil
import datetime as dt
import netCDF4 as ncf

import _get_root
import setup_logging

logger = setup_logging.get_logger( __file__ )

def validate( filepath, dataset ):
    """
    extension: test that dataset is compatible with a netCDF file.
    input: string (path/to/file.ncf), dict (see notes)
    output: Boolean, True == create_from_template will work
    
    notes: dataset is a dictionary structured:
      key = name of variable
      value = numpy.ndarray with shape matching netCDF variable
    'compatible' means that every variable in dataset exists in the file
    and is the same shape (including unlimited dimensions)
    """
    with ncf.Dataset( filepath, 'r' ) as ncf_file:
        ncf_var = ncf_file.variables
        for var, data in dataset.items():
            if var not in ncf_var.keys():
                return False
            if data.shape != ncf_var[ var ][:].shape:
                return False
    return True

def create_from_template( source, dest, change ):
    """
    extension: create a new copy of a netCDF file, with new variable data
    input: string (path/to/old.ncf), string (path/to/new.ncf), dict
    output: None
    
    notes: change is a dict of variables to overwrite
      key = name of variable to change
      value = numpy.ndarray of new values (must match shape)
    if dest already exists it is overwritten.
    """
    assert validate( source, change ), 'changes to template are invalid'
    logger.debug( 'copy {} to {}.'.format( source, dest ) )
    shutil.copyfile( source, dest )
    with ncf.Dataset( dest, 'a' ) as ncf_file:
        for var, data in change.items():
            ncf_file.variables[ var ][:] = data
    return None

def get_variable( filepath, varname ):
    """
    extension: get all the values of a single variable
    input: string (path/to/file.ncf), string
    output: numpy.ndarray
    """
    with ncf.Dataset( filepath, 'r' ) as ncf_file:
        assert varname in ncf_file.variables.keys(), '{} not in file'.format( varname )
        result = ncf_file.variables[varname][:]
    return result

def get_attr( filepath, attrname ):
    """
    extension: get the value of a single attribute
    input: string (path/to/file.ncf), string
    output: attr value (variable type)
    """
    with ncf.Dataset( filepath, 'r' ) as ncf_file:
        assert attrname in ncf_file.ncattrs(), '{} not in file'.format( attrname )
        result = ncf_file.getncattr( attrname )
    return result

def copy_compress( source, dest ):
    """
    extension: create a compressed copy of a netCDF file
    input: string (path/src.ncf), string (path/dst.ncf)
    output: None
    
    notes: if dst already exists it is overwritten.
    """
    #Current version does not compress.
    logger.debug( 'copy {} to {}.'.format( source, dest ) )
    shutil.copyfile( source, dest )
    return None

def set_date( filepath, date ):
    """
    extension: set the date in TFLAG variable & SDATE attribute
    input: string (path/file.ncf), datetime.date
    output: None
    
    notes: changes are made to file in place.
    """
    yj = np.int32( date.strftime( '%Y%j' ) )
    logger.debug( 'set {} to date {}.'.format( filepath, str(yj) ) )
    with ncf.Dataset( filepath, 'a' ) as ncf_file:
        tflag = ncf_file.variables['TFLAG'][:]
        tflag[:,:,0] = yj
        ncf_file.variables['TFLAG'][:] = tflag
        ncf_file.setncattr( 'SDATE', yj )
    return None
