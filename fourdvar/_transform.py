"""
_transform.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
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

