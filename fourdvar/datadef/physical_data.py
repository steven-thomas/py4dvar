"""
application: stores data on physical space of interest
used to store prior/background, construct model input and minimizer input
"""

from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData

class PhysicalData( PhysicalAbstractData ):
    """Starting point of background, link between model and unknowns.
    most code found in parent class.
    """
    archive_name = 'physical_data.pic.gz'
