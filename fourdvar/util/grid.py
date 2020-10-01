"""
grid.py

Copyright 2020 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

"""
import numpy as np
from astropy.constants import R_earth
EPSILON = 1e-6 # small number


# class Grid(object):
class Grid():

    def __init__(self, minlat, maxlat, deltalat, minlon, maxlon, deltalon):
        """ contains all the dimensions of the grid for later use"""
        self.deltaLat = deltalat  # source?
        self.deltaLon = deltalon
        # now define grid edges that are multiples of deltalat and deltalon
        minLatEdge = (minlat // deltalat) * deltalat  # southern edge
        maxLatEdge = ((maxlat-EPSILON) // deltalat +1) * deltalat  # Center
        # others accordingly
        self.latEdges = np.arange(minLatEdge, maxLatEdge + EPSILON * deltalat, deltalat)  # make sure we get in last edge
        self.lats = 0.5 * (self.latEdges[0:-1] + self.latEdges[1:])
        # same for lons
        minLonEdge = (minlon // deltalon) * deltalon  # Center
        maxLonEdge = ((maxlon-EPSILON) // deltalon +1) * deltalon  # Center
        self.lonEdges = np.arange(minLonEdge, maxLonEdge + 0.01 * deltalon, deltalon)  # make sure we get in last edge
        self.lons = 0.5 * (self.lonEdges[0:-1] + self.lonEdges[1:])
        earth_rad = R_earth.value  # 6.371e6 # in metres, module as required
        self.area = earth_rad**2 *(np.sin(self.latEdges[1:]*np.pi/180.) -np.sin(self.latEdges[0:-1]*np.pi/180.))*2*np.pi*deltalon/360.
        return

