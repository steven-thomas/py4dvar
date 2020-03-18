
import numpy as np
import datetime as dt
from ray_trace import Point, Ray
from obs_defn import ObsMultiRay

#physical constants
grav = 9.807
mwair = 28.9628
kg_scale = 1000.
ppm_scale = 1000000.

class ObsTropomi( ObsMultiRay ):
    """Single observation of CO from TROPOMI satellite
    This observation class only works for 1 species.
    """
    required = ['value','uncertainty','weight_grid','offset_term']
    
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in oco2 file.
        min. requirements for kwargs:
        - latitude_center : float (degrees)
        - longitude_center : float (degrees)
        - latitude_bounds : array[ float ] (length=4, units=degrees)
        - longitude_bounds : array[ float ] (length=4, units=degrees)
        - time : string, UTC timestamp
        - solar_zenith_angle : float (degrees)
        - solar_azimuth_angle : float (degrees)
        - viewing_zenith_angle : float (degrees)
        - viewing_azimuth_angle : float (degrees)
        - qa_value : float
        - co_total_column : float (mol m^-2)
        - co_total_column_precision : float (mol m^-2)
        - averaging_kernel : array[ float ] (length=levels)
        - pressure_levels : array[ float ] (length=levels, units=Pa)
        """
        newobs = cls( obstype='TROPOMI_co_obs' )
        #convert mol/m^2 to ppm
        co_mol = kwargs['co_total_column']
        co_mol_unc = kwargs['co_total_column_precision']
        pres = kwargs['pressure_levels'].max()-kwargs['pressure_levels'].min()
        convert = ( ppm_scale * grav * mwair ) / ( pres * kg_scale )
        newobs.out_dict['value'] = co_mol * convert
        newobs.out_dict['uncertainty'] = co_mol_unc * convert

        newobs.out_dict['qa_value'] = kwargs['qa_value']
        newobs.spcs = 'CO'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def model_process( self, model_space ):
        ObsMultiRay.model_process( self, model_space )
        #set lite_coord to surface cell containing lat/lon center
        if 'weight_grid' in self.out_dict.keys():
            day,time,_,_,_,spc = self.out_dict['weight_grid'].keys()[0]
            x,y = model_space.get_xy( self.src_data['latitude_center'],
                                      self.src_data['longitude_center'] )
            col,row,lay = model_space.grid.get_cell( Point((x,y,0)) )
            self.out_dict[ 'lite_coord' ] = (day,time,lay,row,col,spc,)
        return None
    
    def add_visibility( self, proportion, model_space ):
        obs_pressure = np.array( self.src_data[ 'pressure_levels' ] )
        obs_kernel = np.array( self.src_data[ 'averaging_kernel' ] )
        #can't find TROPOMI CO apriori.
        #obs_apriori = np.array( self.src_data[ 'profile_apriori' ] )
        
        #get sample model coordinate at surface
        coord = [ c for c in proportion.keys() if c[2] == 0 ][0]
        
        model_pweight = model_space.get_pressure_weight( coord )
        model_kernel = model_space.pressure_interp( obs_pressure, obs_kernel, coord )
        #model_apriori = model_space.pressure_interp( obs_pressure, obs_apriori, coord )
        
        model_vis = model_pweight * model_kernel
        #column_xco2 = ( model_pweight * model_kernel * model_apriori )
        #self.out_dict['offset_term'] = self.src_data['xco2_apriori'] - column_xco2.sum()
        #NOT SURE ABOUT THIS, need to check what to replace apriori with.
        self.out_dict['offset_term'] = 0.
        
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
        lat_list = self.src_data[ 'latitude_bounds' ]
        lon_list = self.src_data[ 'longitude_bounds' ]
        p0_zenith = np.radians( self.src_data[ 'solar_zenith_angle' ] )
        p0_azimuth = np.radians( self.src_data[ 'solar_azimuth_angle' ] )
        if p0_azimuth < 0.: p0_azimuth += 2*np.pi
        p2_zenith = np.radians( self.src_data[ 'viewing_zenith_angle' ] )
        p2_azimuth = np.radians( self.src_data[ 'viewing_azimuth_angle' ] )
        if p2_azimuth < 0.: p2_azimuth += 2*np.pi

        rays_in = []
        rays_out = []
        for lat,lon in zip( lat_list, lon_list ):
            x1,y1 = model_space.get_xy( lat, lon )
            p1 = (x1,y1,0,)
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
                   in area_dict.items() if val > 0. }
        return result
    
    def map_time( self, model_space ):
        #convert source time into [ int(YYYYMMDD), int(HHMMSS) ]
        str_time = self.src_data[ 'time' ].split('.')[0]
        fulltime = dt.datetime.strptime( str_time, '%Y-%m-%dT%H:%M:%S' )
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsMultiRay.map_time( self, model_space )
