#test that the fwd_model preparation and transformation run

from __future__ import print_function
import numpy as np

import _get_root
from fourdvar.datadef import PhysicalData, ModelInputData, ModelOutputData
from fourdvar._transform import transform
from fourdvar.util.dim_label import label_x, label_t, deltat

test_case = {}
for k in label_x:
    test_case[ k ] = (1, 1)

phys = PhysicalData( test_case )
m_in = transform( phys, ModelInputData )
m_out = transform( m_in, ModelOutputData )

p_icon = np.array( [ phys.data[x][0] for x in label_x ] )
p_emis = np.array( [ phys.data[x][1] for x in label_x ] )
m_icon = m_in.icon
m_emis = m_in.emis
conc = m_out.conc
print( conc )

#trivial has no transfer between cells, therefore conservation of concentration is conservation of mass.

phys_sum = np.sum( p_icon ) + np.sum( p_emis ) * deltat * len( label_t )
in_sum = np.sum( m_icon ) + np.sum( m_emis ) * deltat
out_sum = np.sum( conc )
assert (phys_sum - in_sum) < 1e-8
assert (in_sum - out_sum) < 1e-8

