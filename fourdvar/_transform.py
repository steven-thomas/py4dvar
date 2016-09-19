# NOT FOR USER MODIFICATION
# simple mapping function so that all the various transforms in the transfunc package
# can be referenced by the transform function.

import _get_root
from fourdvar import transfunc as t
from fourdvar import datadef as d

transmap = {
    ( d.PhysicalData, d.UnknownData ): t.condition,
    ( d.UnknownData, d.PhysicalData ): t.uncondition,
    ( d.PhysicalData, d.ModelInputData ): t.prepare_model,
    ( d.ModelInputData, d.ModelOutputData ): t.run_model,
    ( d.ModelOutputData, d.ObservationData ): t.obs_operator,
    ( d.ObservationData, d.AdjointForcingData ): t.calc_forcing,
    ( d.AdjointForcingData, d.SensitivityData ): t.run_adjoint,
    ( d.SensitivityData, d.UnknownData ): t.condition_adjoint
    }

def transform( input_instance, output_class ):
    
    key = (input_instance.__class__, output_class)
    function = transmap[ key ]
    return function( input_instance )

