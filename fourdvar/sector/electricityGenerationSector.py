"""
electricityGenerationSector.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.


"""

import numpy as np

from foudvar.params import config
import baseSector
class ElectricityGenerationSector( baseSector.BaseSector):
    def __init__( self, initval):
        baseSector.BaseSector.__init__( self)
        self.val = initval
        return
    def readCarma():
        """ reads Carma database and creates instance variables for relevant fields from the file"""
        # read csv from config.carmaFileName
        # self.lats = ...
        # likewise for other fields
        return
