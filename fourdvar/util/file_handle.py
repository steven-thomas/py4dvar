"""
extension: all the file IO functions needed for the program
in this example all files are saved to and read from the fourdvar/data directory
"""

import os
import numpy as np
import cPickle as pickle
import sys

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

def save_obj( obj, filepath, txt_extn='.txt', pickle_extn='.pickle', default='pickle' ):
    """
    extension: save a python object to a file, use internal flags for file-type
    input: Object, string (path/to/file.extension)
    output: None
    
    notes: if namespace clash old file is overwritten.
    use file extension to find type, else use default.
    default must be either 'txt' or 'pickle'.
    if saving as txt, str(obj) is saved and some information may be lost.
    """
    assert default in ['txt', 'pickle']
    ensure_path( os.path.dirname( filepath ) )
    option = default
    if filepath.endswith( txt_extn ):
        option = 'txt'
    elif filepath.endswith( pickle_extn ):
        option = 'pickle'
    if option == 'txt':
        with open( filepath, 'w' ) as f:
            f.write( str( obj ) )
            f.write( '\n' )
    elif option == 'pickle':
        with open( filepath, 'w' ) as f:
            pickle.dump( obj, f )
    else:
        raise ValueError( 'unable to save {}. reason unknown.'.format( filepath ) )
    return None
