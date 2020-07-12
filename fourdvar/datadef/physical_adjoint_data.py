"""
physical_adjoint_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
from __future__ import absolute_import

from fourdvar.datadef.abstract._physical_abstract_data import PhysicalAbstractData
from fourdvar.params.input_defn import inc_icon

class PhysicalAdjointData( PhysicalAbstractData ):
    """Starting point of background, link between model and unknowns.
    most code found in parent class.
    """
    archive_name = 'physical_sensitivity.ncf'
    emis_units = 'CF/(mol/(s*m^2))'
    bcon_units = 'CF/(ppm/s)'
    if inc_icon is True:
        icon_units = '<unitless>'
