"""
obsTropomi_defn.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
import datetime as dt
from ray_trace import Point, Ray
from obs_defn import ObsMultiRay

class ObsTropomi( ObsMultiRay ):
    """Single observation (or sounding) from OCO2 satellite
    This observation class only works for 1 species.
    """
    required = ['value','uncertainty','weight_grid','offset_term']
    
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in oco2 file.
        min. requirements for kwargs:
        - orbit : int (index)
        - latitude_mid_point : float (degrees)
        - longitude_mid_point : float (degrees)
        - latitude_bound : array[ float ] (length=4, units=degrees)
        - longitude_bound : array[ float ] (length=4, units=degrees)
        - time : double (seconds since 2010-1-1 00:00:00)
        - solar_zenith : float (degrees)
        - sensor_zenith : float (degrees)
        - solar_azimuth : float (degrees)
        - sensor_azimuth : float (degrees)
        - qa : ubyte (unitless[0:1])
        - methane_mixing_ratio : float (ppb)
        - methane_uncertainty : float (ppb)
        - profile_apriori : array[ float ] (length=layers, units=mol m^-2)
        - pressure_interval : float (Pa)
        - averaging_kernel : array[ float ] (length=layers, units=unitless)
        - surface_pressure : float (Pa)
        """
        newobs = cls( obstype='tropomi_sounding' )
        #convert ppb to ppm
        newobs.out_dict['value'] = kwargs['methane_mixing_ratio'] * 1e-3
        #convert ppb to ppm
        newobs.out_dict['uncertainty'] = kwargs['methane_uncertainty'] * 1e-3

        newobs.out_dict['tropomi_id'] = kwargs['orbit']

        #do something with qa?
        
        newobs.spcs = 'CH4'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def model_process( self, model_space ):
        ObsMultiRay.model_process( self, model_space )
        #now created self.out_dict[ 'weight_grid' ]
        return None
    
    def add_visibility( self, proportion, model_space ):
        #obs apriori is in mol/m^2, convert to ppm
        p_int = float( self.src_data['pressure_interval'] )
        grav = 9.807
        mwair = 28.9628
        kg_scale = 1000.
        ppm_scale = 1000000.
        obs_apriori = ( ppm_scale * np.array(self.src_data['profile_apriori']) /
                        ( p_int * kg_scale / (grav * mwair) ) )
        
        nlay = obs_apriori.size
        p_surf = float( self.src_data[ 'surface_pressure' ] )
        p_edge = np.array( [ (p_surf - i*p_int) for i in range(nlay+1) ] )
        assert p_edge[-1] >= 0., 'cannot have negative pressure!'
        obs_pressure = ( .5 * (p_edge[:-1]+p_edge[1:]) )[::-1]
        obs_kernel = np.array( self.src_data[ 'averaging_kernel' ] )
        
        #all layers are uniform pressure thickness,
        #therefore XCH4 prior is mean of profile
        xch4_apriori = obs_apriori.mean()
        
        #get sample model coordinate at surface
        coord = [ c for c in proportion.keys() if c[2] == 0 ][0]
        
        model_pweight = model_space.get_pressure_weight( coord )
        model_kernel = model_space.pressure_interp( obs_pressure, obs_kernel, coord )
        model_apriori = model_space.pressure_interp( obs_pressure, obs_apriori, coord )
        
        model_vis = model_pweight * model_kernel
        column_xch4 = ( model_pweight * model_kernel * model_apriori )
        self.out_dict['offset_term'] = xch4_apriori - column_xch4.sum()
        
        weight_grid = {}
        for l, weight in enumerate( model_vis ):
            layer_slice = { c:v for c,v in proportion.items() if c[2] == l }
            layer_sum = sum( layer_slice.values() )
            weight_slice = { c: weight*v/layer_sum for c,v in layer_slice.items() }
            weight_grid.update( weight_slice )
        
        return weight_grid
    
    def map_location( self, model_space ):
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        #convert source location data into a list of spacial points
        lat_list = self.src_data[ 'latitude_bound' ]
        lon_list = self.src_data[ 'longitude_bound' ]
        p0_zenith = np.radians( self.src_data[ 'solar_zenith' ] )
        p0_azimuth = np.radians( self.src_data[ 'solar_azimuth' ] )
        if p0_azimuth < 0.: p0_azimuth += 2*np.pi
        p2_zenith = np.radians( self.src_data[ 'sensor_zenith' ] )
        p2_azimuth = np.radians( self.src_data[ 'sensor_azimuth' ] )
        if p2_azimuth < 0.: p2_azimuth += 2*np.pi
        
        rays_in = []
        rays_out = []
        for lat,lon in zip( lat_list, lon_list ):
            x1,y1 = model_space.get_xy( lat, lon )
            p1 = (x1,y1,0)
            p0 = model_space.get_ray_top( p1, p0_zenith, p0_azimuth )
            p2 = model_space.get_ray_top( p1, p2_zenith, p2_azimuth )
            rays_in.append( Ray( p1, p0 ) )
            rays_out.append( Ray( p1, p2 ) )
            
        try:
            in_dict = model_space.grid.get_ray_cell_area( rays_in )
            out_dict = model_space.grid.get_ray_cell_area( rays_out )
        except AssertionError:
            self.coord_fail( 'outside grid area' )
            return None
        
        area_dict = in_dict.copy()
        for coord, val in out_dict.items():
            area_dict[ coord ] = area_dict.get( coord, 0 ) + val
        tarea = sum( area_dict.values() )
            
        #convert x-y-z into lay-row-col and scale values so they sum to 1
        result = { (lay,row,col):val/tarea for [(col,row,lay,),val]
                   in area_dict.items() if val > 0.0 }
        return result
    
    def map_time( self, model_space ):
        #convert source time into [ int(YYYYMMDD), int(HHMMSS) ]
        tstart = dt.datetime( 2010, 1, 1 )
        tdelta = int( self.src_data[ 'time' ] )
        fulltime = tstart + dt.timedelta( seconds=tdelta )
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsMultiRay.map_time( self, model_space )
