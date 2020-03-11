"""
application: produce model input from physical data (prior/background format)
like all transform in transfunc this is referenced from the transform function
eg: transform( physical_instance, datadef.ModelInputData ) == prepare_model( physical_instance )
"""

import numpy as np

from fourdvar.datadef import PhysicalData, ModelInputData

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """
    p_list = list(physical_data.params) + [ physical_data.s0 ]
    p = np.array( p_list )
    x = np.array( physical_data.x0 )
    return ModelInputData.create_new( p, x )
