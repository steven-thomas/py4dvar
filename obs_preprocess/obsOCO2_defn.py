
import numpy as np
import datetime as dt
from obs_defn import ObsMultiRay

class ObsOCO2( ObsMultiRay ):
    """Single observation (or sounding) from OCO2 satellite
    This observation class only works for 1 species.
    """
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in oco2 file.
        min. requirements for kwargs:
        - latitude : float (degrees)
        - longitude : float (degrees)
        - time : float (unix timestamp)
        - solar_zenith_angle : float (degrees)
        - sensor_zenith_angle : float (degrees)
        - solar_azimuth_angle : float (degrees)
        - sensor_azimuth_angle : float (degrees)
        - xco2 : float (ppm)
        - xco2_uncertainty : float (ppm)
        - xco2_averaging_kernel : array[ float ] (length=levels)
        - pressure_levels : array[ float ] (length=levels, units=hPa)
        """
        newobs = cls( obstype='OCO2_sounding' )
        newobs.out_dict['value'] = kwargs['xco2']
        newobs.out_dict['uncertainty'] = kwargs['xco2_uncertainty']
        #OCO2 Lite-files only record CO2 values
        newobs.spcs = 'CO2'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def model_process( self, model_space ):
        ObsMultiRay.model_process( self, model_space )
        #now created self.out_dict[ 'weight_grid' ]
        #need to rescale weight_grid so that values sum to 1
        if self.valid is True:
            tmp = self.out_dict[ 'weight_grid' ].copy()
            total = sum( tmp.values() )
            self.out_dict[ 'weight_grid' ] = { k:(v/total) for k,v in tmp.items() }
        return None
    
    def get_visibility( self, coord_list, model_space ):
        obs_pressure = self.src_data[ 'pressure_levels' ]
        #obs pressure is TOA to surface in hPa, convert to model units
        obs_pressure = [ 100.*p for p in obs_pressure[::-1] ]
        #kernel is also TOA to surface, remember to flip!
        obs_kernel = self.src_data[ 'xco2_averaging_kernel' ][::-1]
        model_kernel = model_space.pressure_interp( obs_pressure, obs_kernel )
        
        model_pressure = np.array( [ p for p in model_space.pressure ] )
        #model ends before TOA, extend top layer to include TOA
        model_pressure[-1] = 0.0
        model_p_diff = np.diff( model_pressure )
        def vis( coord ):
            lay = coord[2]
            return model_p_diff[ lay ] * model_kernel[ lay ]
        #visibility = interpolated averaging kernel * layer pressure thickness
        return { coord: vis(coord) for coord in coord_list }
    
    def map_location( self, model_space ):
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
        self.location = [ p0, p1, p2 ]
        #use generalized function
        return ObsMultiRay.map_location( self, model_space )
    
    def map_time( self, model_space ):
        #convert source time into [ int(YYYYMMDD), int(HHMMSS) ]
        fulltime = dt.datetime.utcfromtimestamp( self.src_data[ 'time' ] )
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsMultiRay.map_time( self, model_space )
