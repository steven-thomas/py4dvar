
from __future__ import absolute_import

import datetime as dt
import numpy as np

from .ray_trace import Point, Ray
from .obs_defn import ObsMultiRay

class ObsOCO2( ObsMultiRay ):
    """Single observation (or sounding) from OCO2 satellite
    This observation class only works for 1 species.
    """
    required = ['value','uncertainty','weight_grid','offset_term']
    
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in oco2 file.
        min. requirements for kwargs:
        - sounding_id : long_int
        - latitude : float (degrees)
        - longitude : float (degrees)
        - time : float (unix timestamp)
        - solar_zenith_angle : float (degrees)
        - sensor_zenith_angle : float (degrees)
        - solar_azimuth_angle : float (degrees)
        - sensor_azimuth_angle : float (degrees)
        - warn_level : byte_int
        - xco2 : float (ppm)
        - xco2_uncertainty : float (ppm)
        - xco2_apriori : float (ppm)
        - co2_profile_apriori : array[ float ] (length=levels, units=ppm)
        - xco2_averaging_kernel : array[ float ] (length=levels)
        - pressure_levels : array[ float ] (length=levels, units=hPa)
        - pressure_weight : array[ float ] (length=levels)
        """
        newobs = cls( obstype='OCO2_sounding' )
        newobs.out_dict['value'] = kwargs['xco2']
        newobs.out_dict['uncertainty'] = kwargs['xco2_uncertainty']

        column_xco2 = ( kwargs['pressure_weight'] *
                        kwargs['xco2_averaging_kernel'] *
                        kwargs['co2_profile_apriori'] )
        newobs.out_dict['offset_term'] = kwargs['xco2_apriori'] - column_xco2.sum()
        # newobs.out_dict['OCO2_id'] = kwargs['sounding_id']
        newobs.out_dict['surface_type'] = kwargs['surface_type']
        newobs.out_dict['operation_mode'] = kwargs['operation_mode']
        #OCO2 Lite-files only record CO2 values
        newobs.spcs = 'CO2'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def model_process( self, model_space ):
        ObsMultiRay.model_process( self, model_space )
        #now created self.out_dict[ 'weight_grid' ]
        return None
    
    def add_visibility( self, proportion, model_space ):
        #obs pressure is in hPa, convert to model units (Pa)
        obs_pressure = 100. * np.array( self.src_data[ 'pressure_levels' ] )
        obs_kernel = np.array( self.src_data[ 'xco2_averaging_kernel' ] )
        obs_pweight = np.array( self.src_data[ 'pressure_weight' ] )
        obs_vis = obs_kernel * obs_pweight
        
        #get sample model coordinate at surface
        coord = [ c for c in proportion.keys() if c[2] == 0 ][0]
        
        model_vis = model_space.pressure_convert( obs_pressure, obs_vis, coord )
        
        weight_grid = {}
        for l, weight in enumerate( model_vis ):
            layer_slice = { c:v for c,v in proportion.items() if c[2] == l }
            layer_sum = sum( layer_slice.values() )
            weight_slice = { c: weight*v/layer_sum for c,v in layer_slice.items() }
            weight_grid.update( weight_slice )
        
        m_vis_sum = sum(model_vis)
        w_sum = sum(weight_grid.values())
        w_len = len(weight_grid.values())
        if abs(m_vis_sum-w_sum) > 1e6:
            print '{:.4}\t{:.4}\t{:}'.format( m_vis_sum, w_sum, w_len )

        return weight_grid
    
    def map_location( self, model_space ):
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        #convert source location data into a list of spacial points
        lat = self.src_data[ 'latitude' ]
        lon = self.src_data[ 'longitude' ]
        p0_zenith = np.radians( self.src_data[ 'solar_zenith_angle' ] )
        p0_azimuth = np.radians( self.src_data[ 'solar_azimuth_angle' ] )
        p2_zenith = np.radians( self.src_data[ 'sensor_zenith_angle' ] )
        p2_azimuth = np.radians( self.src_data[ 'sensor_azimuth_angle' ] )
        
        x1,y1 = model_space.get_xy( lat, lon )
        p1 = (x1,y1,0)
        p0 = model_space.get_ray_top( p1, p0_zenith, p0_azimuth )
        p2 = model_space.get_ray_top( p1, p2_zenith, p2_azimuth )
        
        ray_in = Ray( p0, p1 )
        ray_out = Ray( p1, p2 )
        try:
            in_dict = model_space.grid.get_ray_cell_dist( ray_in )
            out_dict = model_space.grid.get_ray_cell_dist( ray_out )
        except AssertionError:
            self.coord_fail( 'outside grid area' )
            return None
        
        dist_dict = in_dict.copy()
        for coord, val in out_dict.items():
            dist_dict[ coord ] = dist_dict.get( coord, 0 ) + val
        tdist = sum( dist_dict.values() )
            
        #convert x-y-z into lay-row-col and scale values so they sum to 1
        result = { (lay,row,col):val/tdist for [(col,row,lay,),val]
                   in dist_dict.items() if val > 0.0 }
        return result
    
    def map_time( self, model_space ):
        #convert source time into [ int(YYYYMMDD), int(HHMMSS) ]
        fulltime = dt.datetime.utcfromtimestamp( self.src_data[ 'time' ] )
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsMultiRay.map_time( self, model_space )
