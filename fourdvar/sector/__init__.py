"""
__init__.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import config # should come from parent
from utility.general import classFromModule
import baseSector
import importlib
# now extract the sector classes we need, taken from the config{'sectors'} variable
classList = [classFromModule(name, baseclass=baseSector.BaseSector, postfix='Sector', anchor='sector') for name in config.config['sectors']]
