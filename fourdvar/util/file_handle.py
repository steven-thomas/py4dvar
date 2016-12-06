"""
extension: all the file IO functions needed for the program
in this example all files are saved to and read from the fourdvar/data directory
"""

import os
import sys
import numpy as np
import cPickle as pickle

import _get_root
import setup_logging

logger = setup_logging.get_logger( __file__ )

def ensure_path( path, inc_file=False ):
    """
    extension: ensures that the input path exists, creating directories as needed
    input: string (path/to/file), Boolean (see notes)
    output: None
    
    notes: if inc_file is True the last element of path is assumed to be a file
    this file is created if it does not exist and is unaltered otherwise
    """
    path_list = path.split( os.path.sep )
    #if path starts '/', do so for curpath
    curpath = '' if path_list[0] != '' else os.path.sep
    for folder in path_list[:-1]:
        curpath = os.path.join( curpath, folder )
        if not os.path.isdir( curpath ):
            os.mkdir( curpath )
    curpath = os.path.join( curpath, path_list[-1] )
    if inc_file is False:
        if not os.path.isdir( curpath ):
            os.mkdir( curpath )
    else:
        if not os.path.isfile( curpath ):
            with open( curpath, 'a' ):
                pass
    return None

def empty_dir( path ):
    """
    extension: delete every file and subdirectory in path
    input: string (path to directory to empty)
    output: None
    
    notes: if path does not exist, create it.
    """
    ensure_path( path, inc_file=False )
    all_dirs = []
    for (root, dirs, files) in os.walk( path ):
        for f in files:
            os.remove( os.path.join( root, f ) )
        for d in dirs:
            all_dirs.append( os.path.join( root, d ) )
    for d in all_dirs:
        os.rmdir( d )
    return None

open_files = {}

def save_obj( obj, filepath, overwrite=True ):
    """
    extension: save a python object to a pickle file
    input: Object, string (path/to/file.pickle), bool
    output: None
    
    notes: if overwrite is False obj is appended to end of file
    """
    global open_files
    fpath = os.path.realpath( filepath )
    if fpath in open_files.keys() and overwrite is True:
        msg = 'cannot overwrite {}. file already open for reading.'.format( fpath )
        raise IOError( msg )
    ensure_path( os.path.dirname( filepath ) )
    if overwrite is True:
        mode = 'wb'
    else:
        mode = 'ab'
    with open( filepath, mode ) as f:
        pickle.dump( obj, f )
    return None

def load_obj( filepath, close=True ):
    """
    extension: load a python object from a pickle file
    input: string (path/to/file.pickle), bool (close file afterwards)
    output: Object
    
    notes: if EOF is found then None is returned and file is automatically closed
    but an error is NOT raised.
    """
    global open_files
    fpath = os.path.realpath( filepath )
    if fpath in open_files.keys():
        f = open_files[ fpath ]
    else:
        f = open( fpath, 'rb' )
    try:
        obj = pickle.load( f )
    except EOFError:
        obj = None
        close = True
        logger.info( 'EOF of {} reached. closing file.'.format( fpath ) )
    if close is True:
        if fpath in open_files.keys():
            del open_files[ fpath ]
        f.close()
    else:
        open_files[ fpath ] = f
    return obj

