"""
application: stores data on physical space of interest
used to store prior/background, construct model input and minimizer input
"""

import _get_root
from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData

class PhysicalAdjointData( PhysicalAbstractData ):
    """Starting point of background, link between model and unknowns.
    most code found in parent class.
    """
    archive_name = 'physical_sensitivity.ncf'
    icon_units = 'CF/ppm'
    emis_units = 'CF/(mol/(s*m^2))'
