"""
application: stores data on physical space of interest
used to store prior/background, construct model input and minimizer input
"""
from __future__ import absolute_import

from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.params.input_defn import inc_icon

class PhysicalData( PhysicalAbstractData ):
    """Starting point of background, link between model and unknowns.
    most code found in parent class.
    """
    archive_name = 'physical_data.ncf'
    emis_units = 'mol/(s*m^2)'
    if inc_icon is True:
        icon_units = '<unitless>'
