"""
grid.py

Copyright 2020 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

"""
import numpy as np
from math import radians, sin
from astropy.constants import R_earth


# class Grid(object):
class Grid():

    def __init__(self, minlat, maxlat, deltalat, minlon, maxlon, deltalon):
        """ contains all the dimensions of the grid for later use"""
        self.deltaLat = deltalat  # source?
        self.deltaLon = deltalon
        # now define grid edges that are multiples of deltalat and deltalon
        minLatEdge = (minlat // deltalat) * deltalat  # Center
        maxLatEdge = (maxlat // deltalat) * deltalat  # Center
        # others accordingly
        #      Start 0    ,   Stop 50                   ,Interval 5
        self.latEdges = np.arange(minLatEdge, maxLatEdge + 0.01 * deltalat, deltalat)  # make sure we get in last edge
        self.lats = 0.5 * (self.latEdges[0:-1] + self.latEdges[1:])
        # same for lons
        minLonEdge = (minlon // deltalon) * deltalon  # Center
        maxLonEdge = (maxlon // deltalon) * deltalon  # Center
        self.lonEdges = np.arange(minLonEdge, maxLonEdge + 0.01 * deltalon, deltalon)  # make sure we get in last edge
        self.lons = 0.5 * (self.lonEdges[0:-1] + self.lonEdges[1:])
        earth_rad = R_earth.value  # 6.371e6 # in metres, module as required
        self.area = [] * len(self.lats) # Adopted from IDL version
        for lat in self.lats:
            area = np.square(earth_rad) * (sin(radians(maxlat)) - sin(radians(minlat))) * radians(deltalon) #Formula taken from IDL version of FFDAS
            self.area.append(area)

        print(earth_rad)
        print(len(self.area))
        print(self.area)

        # now define self.area with the same size as lats and the value the area of a gridbox, should import a constants module that contains radius of earth
        return

Grid(18.923882000000106,83.62359600000008,0.01,4-179.99999999999997,180.0,0.01)