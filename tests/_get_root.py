# NOT FOR USER MODIFICATION
# this ensures that the root file of the project (marked by the _init_root.py file)
# is in the import path regards of where the project is called from

import sys
import os

root_file = '_init_root.py'
backstep = '..'
loc = os.path.dirname( os.path.realpath( __file__ ) )

while not os.path.isfile( os.path.join( loc, root_file ) ):
    new_loc = os.path.realpath( os.path.join( loc, backstep ) )
    if new_loc == loc:
        raise ImportError( 'unable to find __init__root.py in package' )
    else:
        loc = new_loc

root_path = os.path.abspath( loc )

if root_path not in sys.path:
    sys.path.append( root_path )

