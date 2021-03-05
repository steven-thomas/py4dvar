"""
file_handle.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
import sys
import gzip
import numpy as np
import pickle

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

def save_list( obj_list, filepath ):
    """
    extension: save a list of python objects to a zipped pickle file
    input: list, string (path/to/file.pickle)
    output: None
    """
    fpath = os.path.realpath( filepath )
    ensure_path( os.path.dirname( fpath ) )
    
    with gzip.GzipFile( fpath, 'wb' ) as f:
        for element in obj_list:
            pickle.dump( element, f )
    return None

def load_list( filepath ):
    """
    extension: load a list of python objects from a zipped pickle file
    input: string (path/to/file.pickle)
    output: list
    """
    fpath = os.path.realpath( filepath )
    obj_list = []
    eof = False
    
    with gzip.GzipFile( fpath, 'rb' ) as f:
        while eof is False:
            try:
                element = pickle.load( f )
                obj_list.append( element )
            except EOFError:
                eof = True
    return obj_list
