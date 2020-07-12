"""
_get_root.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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

