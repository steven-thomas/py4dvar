"""
framework: API for easy access to all the transform functions
"""

from fourdvar import transfunc as t
from fourdvar import datadef as d

#map of input/output classes to functions used
transmap = {
    ( d.PhysicalData, d.UnknownData ): t.condition,
    ( d.UnknownData, d.PhysicalData ): t.uncondition,
    ( d.PhysicalData, d.ModelInputData ): t.prepare_model,
    ( d.ModelInputData, d.ModelOutputData ): t.run_model,
    ( d.ModelOutputData, d.ObservationData ): t.obs_operator,
    ( d.ObservationData, d.AdjointForcingData ): t.calc_forcing,
    ( d.AdjointForcingData, d.SensitivityData ): t.run_adjoint,
    ( d.SensitivityData, d.PhysicalAdjointData ): t.map_sense,
    ( d.PhysicalAdjointData, d.UnknownData ): t.condition_adjoint
    }

def transform( input_instance, output_class ):
    """
    framework: mapping of every transform to its input & output class
    input: instance of transform input, class of transform output
    output: result of mapped transformation (instance of output_class)
    
    eg:
    from datadef._transform import transform
    model_output = transform( model_input, datadef.ModelOutputData )
    """
    
    key = (input_instance.__class__, output_class)
    function = transmap[ key ]
    return function( input_instance )

