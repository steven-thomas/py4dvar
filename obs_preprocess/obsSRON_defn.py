"""
obsSRON_defn.py

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

#physical constants
grav = 9.807
mwair = 28.9628
avo = 6.022e23
kg_scale = 1000.
cm_scale = 100.*100.
ppm_scale = 1000000.

class ObsSRON( ObsMultiRay ):
    """Single observation of CO from TROPOMI satellite, processed by SRON
    This observation class only works for 1 species.
    """
    required = ['value','uncertainty','weight_grid','alpha_scale']
    #remove offset_term from default dict for obs.
    default = {'lite_coord':None}
    
    @classmethod
    def create( cls, **kwargs ):
        """kwargs comes from variables in oco2 file.
        min. requirements for kwargs:
        - time : datetime-obj (datetime)
        - latitude_center : float (degrees)
        - longitude_center : float (degrees)
        - latitude_corners : array[ float ] (length=4, units=degrees)
        - longitude_corners : array[ float ] (length=4, units=degrees)
        - solar_zenith_angle : float (degrees)
        - viewing_zenith_angle : float (degrees)
        - solar_azimuth_angle : float (degrees)
        - viewing_azimuth_angle : float (degrees)
        - pressure_levels : array[ float ] (length=levels, units=Pa)
        - co_column : float (molec. cm-2)
        - co_column_precision : float (molec. cm-2)
        - co_column_apriori : float (molec. cm-2)
        - co_profile_apriori : array[ float ] (length=levels, units=molec. cm-2)
        - qa_value : float (unitless)
        """
        newobs = cls( obstype='SRON_co_obs' )
        
        # alpha is change to scaled profile.
        sron_alpha = kwargs['co_column'] / kwargs['co_column_apriori']
        newobs.out_dict['value'] = sron_alpha
        #newobs.out_dict['uncertainty'] = co_mol_unc * convert
        newobs.out_dict['qa_value'] = kwargs['qa_value']
        newobs.spcs = 'CO'
        newobs.src_data = kwargs.copy()
        return newobs
    
    def _convert_ppm( self, value, pressure_interval ):
        """convert molec. cm-2 to ppm"""
        ppm_value = ( ppm_scale * (value * cm_scale / avo) /
                      ( pressure_interval * kg_scale / (grav * mwair) ) )
        return ppm_value
    
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
        obs_pressure_bounds = np.array( self.src_data[ 'pressure_levels' ] )
        obs_pressure_center = 0.5 * ( obs_pressure_bounds[1:] + obs_pressure_bounds[:-1] )
        obs_pressure_interval = ( obs_pressure_bounds[1:] - obs_pressure_bounds[:-1] )
        sron_unc_molec = self.src_data['co_column_precision']
        sron_unc_ppm = self._convert_ppm( sron_unc_molec, obs_pressure_interval.sum() )
        
        #get sample model coordinate at surface
        coord = [ c for c in proportion.keys() if c[2] == 0 ][0]

        #need to save the ref. profile concentration & obs. uncertainty.
        model_pweight = model_space.get_pressure_weight( coord )
        ref_profile_molec = self.src_data['co_profile_apriori']
        ref_profile_ppm = self._convert_ppm( ref_profile_molec, obs_pressure_interval )
        model_ref_profile = model_space.pressure_interp( obs_pressure_center,
                                                         ref_profile_ppm, coord )
        model_unc = sron_unc_ppm / ((model_pweight*model_ref_profile)).sum()
        self.out_dict['uncertainty'] = model_unc
        self.out_dict['ref_profile'] = model_ref_profile
        self.out_dict['alpha_scale'] = ((model_pweight*model_ref_profile)**2).sum()
        
        model_vis = model_pweight * model_ref_profile
        
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
        lat_list = self.src_data[ 'latitude_corners' ]
        lon_list = self.src_data[ 'longitude_corners' ]
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
        fulltime = self.src_data[ 'time' ]
        day = int( fulltime.strftime( '%Y%m%d' ) )
        time = int( fulltime.strftime( '%H%M%S' ) )
        self.time = [ day, time ]
        #use generalized function
        return ObsMultiRay.map_time( self, model_space )
