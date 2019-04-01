"""
application: stores data on physical space of interest
used to store prior/background, construct model input and minimizer input
"""

from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.params.input_defn import inc_icon

class PhysicalAdjointData( PhysicalAbstractData ):
    """Starting point of background, link between model and unknowns.
    most code found in parent class.
    """
    archive_name = 'physical_sensitivity.ncf'
    emis_units = 'CF/(mol/(s*m^2))'
    if inc_icon is True:
        icon_units = 'CF/ppm'

    @classmethod
    def create_new( cls, *args ):
        new_inst = cls( *args )
        return new_inst
