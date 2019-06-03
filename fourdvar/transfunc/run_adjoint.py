"""
application: run the adjoint model, construct SensitivityData from results
like all transform in transfunc this is referenced from the transform function
eg: transform( adjoint_forcing_instance, datadef.SensitivityData ) == run_adjoint( adjoint_forcing_instance )
"""

import numpy as np

from fourdvar.datadef import AdjointForcingData, SensitivityData
import fourdvar.util.cmaq_handle as cmaq

def run_adjoint( adjoint_forcing ):
    """
    application: run the adjoint model, construct SensitivityData from results
    input: AdjointForcingData
    output: SensitivityData
    """
    assert isinstance( adjoint_forcing, AdjointForcingData )
    #should ensure that checkpoints exist first.
    cmaq.wipeout_bwd()
    cmaq.run_bwd()
    return SensitivityData()

