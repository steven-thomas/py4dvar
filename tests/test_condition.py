#test that the condition and uncondition transformations run
# and that uncondition( condition( x ) ) == x

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, UnknownData
from fourdvar._transform import transform

filename = 'background.csv'

bg0 = PhysicalData.from_file( filename )
un = transform( bg0, UnknownData )
bg1 = transform( un, PhysicalData )

assert bg0.data == bg1.data

