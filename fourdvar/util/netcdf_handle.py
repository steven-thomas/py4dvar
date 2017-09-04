"""
extension: toolkit for interacting with netCDF files
"""

import numpy as np
import os
import shutil
import netCDF4 as ncf

import _get_root
import fourdvar.util.date_handle as dt
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

def create_from_template( source, dest, var_change={}, date=None ):
    """
    extension: create a new copy of a netCDF file, with new variable data
    input: string (path/to/old.ncf), string (path/to/new.ncf), dict, date obj
    output: None
    
    notes: var_change is a dict of variables to overwrite
        key = name of variable to change
        value = numpy.ndarray of new values (must match shape)
      date is the date to set the new file to (SDATE & TFLAG),
        if None date is left unmodified
    if dest already exists it is overwritten.
    """
    assert validate( source, var_change ), 'changes to template are invalid'
    logger.debug( 'copy {} to {}.'.format( source, dest ) )
    shutil.copyfile( source, dest )
    with ncf.Dataset( dest, 'a' ) as ncf_file:
        for var, data in var_change.items():
            ncf_file.variables[ var ][:] = data
        if date is not None:
            set_date( ncf_file, date )
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

def set_date( fileobj, start_date ):
    """
    extension: set the date in TFLAG variable & SDATE attribute
    input: string (path/file.ncf) OR netCDF file obj, datetime.date
    output: None
    
    notes: changes are made to file in place.
    """
    def _set_ncfobj_date( ncf_file, sdate ):
        yj = lambda date: np.int32( dt.replace_date('<YYYYDDD>', date) )
        tflag = ncf_file.variables[ 'TFLAG' ][:]
        tflag_date = tflag[ :, :, 0 ]
        base_date = tflag_date[ 0, 0 ]
        date_offset = tflag_date - base_date
        for i in range( date_offset.max() + 1 ):
            date = dt.add_days( sdate, i )
            tflag_date[ date_offset==i ] = yj( date )
        ncf_file.variables[ 'TFLAG' ][:] = tflag
        ncf_file.setncattr( 'SDATE', yj( sdate ) )
        return None
    
    if str( fileobj ) == fileobj:
        #provided with filepath
        with ncf.Dataset( fileobj, 'a' ) as ncf_file:
            _set_ncfobj_date( ncf_file, start_date )
    else:
        #provided with file object
        _set_ncfobj_date( fileobj, start_date )
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
        if bool( np.all( src1[ key ] == src2[ key ] ) ) is False:
            return False
    return True

def create( path=None, parent=None, name=None,
            attr={}, dim={}, var={}, is_root=True ):
    """
    extension: create a new netCDF group or file
    input: string, ncf obj, string, dict, dict, dict, bool
    output: ncf.Dataset obj
    
    notes: path = file path for ncf object, not required if is_root is False
           parent = ncf obj for parent group, not required if is_root is True
           name = name of group, not required if is_root is True
           attr = dict of attributes {attr_name: attr_value}
           dim = dict of dimensions {dim_name: dim_size}
           var = dict of variables {var_name: ( var_dtype, var_dimension, var_value)}
           is_root = is the group being create a root group (new file)
           
           If namespace clash this function will overwrite existing files!
    """
    if is_root is True:
        assert path is not None, 'root group must have a path'
        grp = ncf.Dataset( path, 'w' )
    elif is_root is False:
        assert parent is not None, 'child group must have a parent'
        assert name is not None, 'child group must have a name'
        grp = parent.createGroup( name )
    else:
        raise ValueError( 'is_root must be boolean' )
    for attr_name, attr_value in attr.items():
        grp.setncattr( attr_name, attr_value )
    for dim_name, dim_size in dim.items():
        grp.createDimension( dim_name, dim_size )
    for var_name, var_value in var.items():
        var_type, var_dim, var_arr = var_value
        v = grp.createVariable( var_name, var_type, var_dim )
        v[:] = var_arr
    return grp
