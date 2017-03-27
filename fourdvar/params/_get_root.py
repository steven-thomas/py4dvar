"""
framework: add project root to import path
project root is defined as where the _init_root.py file is located
running >> import _get_root will allow importing from the root regardless of current location
eg:
>>> import _get_root
>>> import fourdvar.datadef as d        (must be after import _get_root)
"""

import sys
import os

root_file = '_init_root.py'
backstep = '..'
loc = os.path.dirname( os.path.realpath( __file__ ) )

while not os.path.isfile( os.path.join( loc, root_file ) ):
    new_loc = os.path.realpath( os.path.join( loc, backstep ) )
    if new_loc == loc:
        raise ImportError( 'unable to find _init_root.py in package' )
    else:
        loc = new_loc

root_path = os.path.abspath( loc )

if root_path not in sys.path:
    sys.path.append( root_path )

