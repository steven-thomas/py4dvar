
import numpy as np
import datetime as dt
from ray_trace import Point, Ray
from obs_defn import ObsInstantRay

class ObsGEOCARB_XCO2( ObsInstantRay ):
    """Single observation (or sounding) of CO2 from GEOCARB satellite"""
    required = ['value','uncertainty','weight_grid','offset_term']
    
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in geocarb files.
        min. requirements for kwargs:
        - sounding_id : long_int
        - latitude : float (degrees)
        - longitude : float (degrees)
        - time : datetime object
        - xco2 : float (ppm)
        - xco2_uncertainty : float (ppm)
        - xco2_apriori : float (ppm)
        - co2_profile_apriori : array[ float ] (length=levels, units=ppm)
        - xco2_averaging_kernel : array[ float ] (length=levels)
        - pressure_levels : array[ float ] (length=levels, units=hPa)
        """
        newobs = cls( obstype='GEOCARB_xco2_sounding' )
        newobs.out_dict['value'] = kwargs['xco2']
        newobs.out_dict['uncertainty'] = kwargs['xco2_uncertainty']

        newobs.out_dict['sounding_id'] = kwargs['sounding_id']
        newobs.spcs = 'CO2'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def model_process( self, model_space ):
        ObsInstantRay.model_process( self, model_space )
        #set lite_coord to surface cell with largest weight
        if 'weight_grid' in self.out_dict.keys():
            surf = [ (v,k) for k,v in self.out_dict['weight_grid'].items()
                     if k[2]==0 ]
            self.out_dict[ 'lite_coord' ] = max(surf)[1]
        return None
    
    def add_visibility( self, proportion, model_space ):
        obs_pressure = np.array( self.src_data[ 'pressure_levels' ] )
        obs_kernel = np.array( self.src_data[ 'xco2_averaging_kernel' ] )
        obs_apriori = np.array( self.src_data[ 'co2_profile_apriori' ] )
        
        #get sample model coordinate at surface
        coord = [ c for c in proportion.keys() if c[2] == 0 ][0]
        
        model_pweight = model_space.get_pressure_weight( coord )
        model_kernel = model_space.pressure_interp( obs_pressure, obs_kernel, coord )
        model_apriori = model_space.pressure_interp( obs_pressure, obs_apriori, coord )
        
        model_vis = model_pweight * model_kernel
        column_xco2 = ( model_pweight * model_kernel * model_apriori )
        self.out_dict['offset_term'] = self.src_data['xco2_apriori'] - column_xco2.sum()
        
        weight_grid = {}
        for l, weight in enumerate( model_vis ):
            layer_slice = { c:v for c,v in proportion.items() if c[2] == l }
            layer_sum = sum( layer_slice.values() )
            weight_slice = { c: weight*v/layer_sum for c,v in layer_slice.items() }
            weight_grid.update( weight_slice )
        
        return weight_grid
    
    def map_location( self, model_space ):
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        #convert source location data into a pair of spacial points
        #GEOCARB assumes a vertical retrieval.
        lat = self.src_data[ 'latitude' ]
        lon = self.src_data[ 'longitude' ]
        
        x1,y1 = model_space.get_xy( lat, lon )
        p1 = ( x1, y1, 0, )
        p2 = ( x1, y1, model_space.max_height, )
        
        self.location = [ p1, p2 ]
        #use generalized function
        return ObsInstantRay.map_location( self, model_space )
    
    def map_time( self, model_space ):
        #convert source time into [ int(YYYYMMDD), int(HHMMSS) ]
        fulltime = self.src_data[ 'time' ]
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsInstantRay.map_time( self, model_space )


class ObsGEOCARB_XCO( ObsInstantRay ):
    """Single observation (or sounding) of CO from GEOCARB satellite"""
    required = ['value','uncertainty','weight_grid','offset_term']
    
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in geocarb files.
        min. requirements for kwargs:
        - sounding_id : long_int
        - latitude : float (degrees)
        - longitude : float (degrees)
        - time : datetime object
        - co_scale_factor : float (unitless)
        - co_scale_factor_uncert : float (unitless)
        - co_profile_apriori : array[ float ] (length=levels, units=ppm)
        - pressure_levels : array[ float ] (length=levels, units=hPa)
        """
        newobs = cls( obstype='GEOCARB_xco_sounding' )
        newobs.out_dict['sounding_id'] = kwargs['sounding_id']
        newobs.out_dict['offset_term'] = 0.
        newobs.spcs = 'CO'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def model_process( self, model_space ):
        ObsInstantRay.model_process( self, model_space )
        #set lite_coord to surface cell with largest weight
        if 'weight_grid' in self.out_dict.keys():
            surf = [ (v,k) for k,v in self.out_dict['weight_grid'].items()
                     if k[2]==0 ]
            self.out_dict[ 'lite_coord' ] = max(surf)[1]
        return None
    
    def add_visibility( self, proportion, model_space ):
        obs_pressure = np.array( self.src_data[ 'pressure_levels' ] )
        obs_apriori = np.array( self.src_data[ 'co_profile_apriori' ] )
        
        #get sample model coordinate at surface
        coord = [ c for c in proportion.keys() if c[2] == 0 ][0]
        
        model_pweight = model_space.get_pressure_weight( coord )
        model_apriori = model_space.pressure_interp( obs_pressure, obs_apriori, coord )
        model_profile = model_apriori * self.src_data[ 'co_scale_factor' ]
        model_unc = model_apriori * self.src_data[ 'co_scale_factor_uncert' ]
        self.out_dict['value'] = ( model_profile * model_pweight ).sum()
        self.out_dict['uncertainty'] = ( model_unc * model_pweight ).sum()
        
        weight_grid = {}
        for l, weight in enumerate( model_pweight ):
            layer_slice = { c:v for c,v in proportion.items() if c[2] == l }
            layer_sum = sum( layer_slice.values() )
            weight_slice = { c: weight*v/layer_sum for c,v in layer_slice.items() }
            weight_grid.update( weight_slice )
        
        return weight_grid
    
    def map_location( self, model_space ):
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        #convert source location data into a pair of spacial points
        #GEOCARB assumes a vertical retrieval.
        lat = self.src_data[ 'latitude' ]
        lon = self.src_data[ 'longitude' ]
        
        x1,y1 = model_space.get_xy( lat, lon )
        p1 = ( x1, y1, 0, )
        p2 = ( x1, y1, model_space.max_height, )
        
        self.location = [ p1, p2 ]
        #use generalized function
        return ObsInstantRay.map_location( self, model_space )
    
    def map_time( self, model_space ):
        #convert source time into [ int(YYYYMMDD), int(HHMMSS) ]
        fulltime = self.src_data[ 'time' ]
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsInstantRay.map_time( self, model_space )
