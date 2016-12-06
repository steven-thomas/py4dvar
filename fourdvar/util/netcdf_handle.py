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

def get_variable( filepath, varname, group=None ):
    """
    extension: get all the values of a single variable
    input: string (path/to/file.ncf), string <OR> list, string (optional)
    output: numpy.ndarray OR dict
    
    notes: group allows chosing netCDF4 groups, leave as None to use root
    if varname is a string an array is returned, otherwise a dict is.
    """
    with ncf.Dataset( filepath, 'r' ) as ncf_file:
        source = ncf_file
        if group is not None:
            for g in group.split( '/' ):
                source = source.groups[ g ]
        if str(varname) == varname:
            result = source.variables[ varname ][:]
        else:
            result = { k:v[:] for k,v in source.variables.items() if k in varname }
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

def get_all_attr( filepath ):
    """
    extension: get a dict of all global attributes
    input: string (path/to/file.ncf)
    output: dict { str(attr_name) : attr_val }
    """
    with ncf.Dataset( filepath, 'r' ) as f:
        attr_dict = { name : f.getncattr( name ) for name in f.ncattrs() }
    return attr_dict

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

def match_attr( src1, src2, attrlist=None ):
    """
    extension: check that attributes listed are the same for each src
    input: string <OR> dict, string <OR> dict, list
    output: bool
    
    notes: input sources can be either paths to netcdf files
    or dicts {attr_name : attr_val}.
    if attrlist is None the intersection of src attr_names is used
    """
    if str(src1) == src1:
        src1 = get_all_attr( src1 )
    if str(src2) == src2:
        src2 = get_all_attr( src2 )
    if attrlist is None:
        attrlist = set( src1.keys() ) & set( src2.keys() )
    elif str( attrlist ) == attrlist:
        attrlist = [ attrlist ]
    for key in attrlist:
        match = ( src1[ key ] == src2[ key ] )
        if ( isinstance( match, np.ndarray ) ):
            match = match.all()
        if match is False:
            return False
    return True
