"""
uncondition.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import UnknownData, PhysicalData

def uncondition( unknown ):
    """
    application: undo pre-conditioning of PhysicalData, add back any lost metadata
    input: UnknownData
    output: PhysicalData
    
    notes: this function must apply the prior error covariance
    """
    full_vector = unknown.get_vector()
    weighted = []
    start = 0
    for unc_arr in PhysicalData.uncertainty:
        size = unc_arr.size
        val = full_vector[start:start+size]
        weighted.append( val*unc_arr )
        start += size
    return PhysicalData( weighted )
