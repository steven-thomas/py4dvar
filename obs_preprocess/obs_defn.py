
import numpy as np
from copy import deepcopy

from obs_preprocess.ray_trace import Point, Ray

class ObsGeneral( object ):
    """base class for observations."""
    count = 0
    #required attributes must be defined in out_dict
    required = ['value','uncertainty','weight_grid']
    #default attributes will be added to out_dict if not already present
    default = {'offset_term': 0., 'lite_coord':None}
    
    def __init__( self, obstype='Unknown' ):
        self.id = ObsGeneral.count
        ObsGeneral.count += 1
        self.out_dict = { 'type': obstype }
        self.ready = False
        self.valid = True
        return None
    
    def get_obsdict( self ):
        if self.ready is False:
            raise AttributeError( 'obs No. {} is not ready'.format(self.id) )
        if self.valid is False:
            raise AttributeError( 'obs No. {} is invalid'.format(self.id) )
        keys = self.out_dict.keys()
        for attr in self.required:
            if attr not in keys:
                raise AttributeError('obs No. {} is missing {}'.format(self.id,attr))
        for attr,val in self.default.items():
            if attr not in keys:
                print '{:} not defined, setting to {:}'.format(attr,val)
                self.out_dict[ attr ] = val
        return deepcopy( self.out_dict )
    
    def model_process( self, model_space ):
        msg = 'class {} must overload construct method'
        raise AttributeError( msg.format( self.__class__.__name__) )
        return None

class ObsSimple( ObsGeneral ):
    """Simple observation for testing.
    Instant point measurement
    Provided with co-ordinate already mapped into model grid."""
    @classmethod
    def create( cls, cell, value, uncertainty ):
        newobs = cls( obstype='Simple' )
        newobs.out_dict['value'] = float( value )
        newobs.out_dict['uncertainty'] = float( uncertainty )
        newobs.cell = cell
        return newobs
    
    def model_process( self, model_space ):
        if model_space.valid_coord( self.cell ) is True:
            self.valid = True
            self.out_dict['weight_grid'] = { tuple(self.cell): 1.0 }
            self.ready = True
        else:
            self.valid = False
            self.ready = True
        return None
    
    def coord_fail( self, fail_reason='unknown' ):
        self.valid = False
        self.ready = True
        self.fail_reason = fail_reason
        return None

class ObsStationary( ObsSimple ):
    """Simple example for time-averaged stationary observations
    eg: rooftop equipment.
    See map_time & map_location methods for input assumptions
    """
    @classmethod
    def create( cls, time, loc, spcs, value, uncertainty ):
        newobs = cls( obstype='Stationary' )
        newobs.out_dict['value'] = float( value )
        newobs.out_dict['uncertainty'] = float( uncertainty )
        newobs.time = time
        newobs.location = loc
        newobs.spcs = spcs
        return newobs
    
    def model_process( self, model_space ):
        """Process the observation with the models parameters"""
        
        if self.spcs not in model_space.spcs:
            self.coord_fail( 'invalid spcs' )
            return None
        
        loc_dict = self.map_location( model_space )
        if self.valid is False: return None
        
        time_dict = self.map_time( model_space )
        if self.valid is False: return None
        
        proportion = {}
        for time_k, time_v in time_dict.items():
            for loc_k, loc_v in loc_dict.items():
                coord = time_k + loc_k + (self.spcs,)
                proportion[ coord ] = time_v * loc_v
        
        weight_grid = self.add_visibility( proportion, model_space )
        if self.valid is False: return None
        
        #dicts must have identical keys
        assert set( weight_grid ) == set( proportion )
        self.out_dict['weight_grid'] = weight_grid
        self.ready = True
        return None
    
    def map_time( self, model_space ):
        """Map self.time into dictionary where
        key   = model_space time co-ordinate,
        value = proportion of observation."""
        #assume self.time = [ start_time, end_time ]
        #assume time recorded as [ int(YYYYMMDD), int(HHMMSS) ]
        if self.time[1][0] < self.time[0][0]:
            self.coord_fail( 'invalid time interval' )
            return None
        start = model_space.get_step( self.time[0] )
        end = model_space.get_step( self.time[1] )
        result = {}
        spos = model_space.get_step_pos( self.time[0][1] )
        epos = model_space.get_step_pos( self.time[1][1] )
        if start == end:
            #special case, handled seperatly
            if epos <= spos:
                self.coord_fail( 'invalid time interval' )
                return None
            final = model_space.next_step( end )
            sval = min(epos, 0.5) - min(spos, 0.5)
            fval = max(epos-0.5, 0) - max(spos-0.5, 0)
            result[ start ] = float(sval) / (sval+fval)
            result[ final ] = float(fval) / (sval+fval)
            return result
        if spos < 0.5:
            result[ start ] = 0.5 - spos
        cur = model_space.next_step( start )
        result[ cur ] = 0.5 - max( 0, spos - 0.5 )
        while cur != end:
            result[ cur ] += 0.5
            cur = model_space.next_step( cur )
            result[ cur ] = 0.5
        result[ cur ] += min( 0.5, epos )
        if epos > 0.5:
            final = model_space.next_step( cur )
            result[ final ] = 0.5 - epos
        
        #check obs falls within date range
        date_set = set( k[0] for k in result.keys() )
        sdate = model_space.sdate
        edate = model_space.edate
        if not all( sdate <= d <= edate for d in date_set ):
            self.coord_fail( 'outside date range' )
            return None
        
        total = sum( result.values() )
        return { k: float(v)/total for k,v in result.items() }
    
    def map_location( self, model_space ):
        """Map self.location into dictionary where
        key   = model_space lay/col/row co-ordinate,
        value = proportion of observation."""
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        #Assume location provided in x,y,z co-ordinates.
        stationary_point = Point( self.location )
        try:
            coord = model_space.grid.get_cell( stationary_point )
        except AssertionError:
            self.coord_fail( 'outside grid position' )
            return None
        col,row,lay = coord
        #stationary obs only has one location
        return { (lay,row,col,) : 1.0 }
    
    def add_visibility( self, proportion, model_space ):
        assert model_space.gridmeta['VGTYP'] == 7, 'invalid VGTYP'
        return { k:v for k,v in proportion.items() }
    

class ObsInstantRay( ObsSimple ):
    """Simple example for instant straight-path observations
    eg: Satelite measurement.
    See map_time & map_location methods for input assumptions
    Only works for 1 species
    """
    @classmethod
    def create( cls, time, loc, spcs, value, uncertainty ):
        newobs = cls( obstype='InstantRay' )
        newobs.out_dict['value'] = float( value )
        newobs.out_dict['uncertainty'] = float( uncertainty )
        newobs.time = time
        newobs.location = loc
        newobs.spcs = spcs
        return newobs
    
    def model_process( self, model_space ):
        """Process the observation with the models parameters"""
        
        if self.spcs not in model_space.spcs:
            self.coord_fail( 'invalid spcs' )
            return None
        
        loc_dict = self.map_location( model_space )
        if self.valid is False: return None
        
        time_dict = self.map_time( model_space )
        if self.valid is False: return None
        
        proportion = {}
        for time_k, time_v in time_dict.items():
            for loc_k, loc_v in loc_dict.items():
                coord = time_k + loc_k + (self.spcs,)
                proportion[ coord ] = time_v * loc_v
        
        weight_grid = self.add_visibility( proportion, model_space )
        if self.valid is False: return None
        
        #dicts must have identical keys
        assert set( weight_grid ) == set( proportion )
        for key in weight_grid.keys():
            if model_space.valid_coord( key ) is False:
                self.coord_fail()
                return None
        self.out_dict['weight_grid'] = weight_grid
        self.ready = True
        return None
    
    def map_time( self, model_space ):
        """Map self.time into dictionary where
        key   = model_space time co-ordinate,
        value = proportion of observation."""
        #assume self.time = [ int(YYYYMMDD), int(HHMMSS) ]
        #interpolate time between 2 closest timesteps
        # unless interp_time exists and is False
        start = model_space.get_step( self.time )
        end = model_space.next_step( start )
        end_val = model_space.get_step_pos( self.time[1] )
        start_val = 1 - end_val

        if hasattr( self, 'interp_time' ) and self.interp_time is False:
            # assign obs to closest timestep
            if start_val >= end_val:
                result = { start : 1. }
            else:
                result = { end : 1. }
        else:
            result = { start : start_val }
            if end_val > 0.:
                result[ end ] = end_val
        
        #check obs falls within date range
        date_set = set( k[0] for k in result.keys() )
        sdate = model_space.sdate
        edate = model_space.edate
        if not all( sdate <= d <= edate for d in date_set ):
            self.coord_fail( 'outside date range' )
            return None
        
        return result
    
    def map_location( self, model_space ):
        """Map self.location into dictionary where
        key   = model_space lay/col/row co-ordinate,
        value = proportion of observation."""
        #assume self.location = [ loc_start, loc_end ]
        #assume loc recorded in (x,y,z) co-ordinates.
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        loc_start,loc_end = self.location
        ray_path = Ray( loc_start, loc_end )
        try:
            xyz_dict = model_space.grid.get_weight( ray_path )
        except AssertionError:
            self.coord_fail( 'outside grid area' )
            return None
        #convert x-y-z into lay-row-col
        result = { (lay,row,col):val
                   for [(col,row,lay,),val]
                   in xyz_dict.items() 
                   if val > 0.0}
        return result
    
    def add_visibility( self, proportion, model_space ):
        assert model_space.gridmeta['VGTYP'] == 7, 'invalid VGTYP'
        return { k:v for k,v in proportion.items() }

class ObsMultiRay( ObsInstantRay ):
    """Simple example for instant piecewise-straight path observations
    eg: Satelite measurement.
    Uses model_process, map_time & add_visibility from obsInstantRay
    only works for 1 species
    """
    @classmethod
    def create( cls, time, loc, spcs, value, uncertainty ):
        newobs = cls( obstype='MultiRay' )
        newobs.out_dict['value'] = float( value )
        newobs.out_dict['uncertainty'] = float( uncertainty )
        newobs.time = time
        newobs.location = loc
        newobs.spcs = spcs
        return newobs
    
    def map_location( self, model_space ):
        """Map self.location into dictionary where
        key   = model_space lay/col/row co-ordinate,
        value = proportion of observation."""
        #assume self.location = [ point_0, point_1, ..., point_n ]
        #assume point recorded in (x,y,z) co-ordinates.
        assert model_space.gridmeta['GDTYP'] == 2, 'invalid GDTYP'
        ray_list = []
        for start, end in zip( self.location[:-1], self.location[1:] ):
            ray_list.append( Ray( start, end ) )
        total = sum( r.length for r in ray_list )
        frac_list = [ float(r.length)/total for r in ray_list ]
        
        #add up each component ray
        total_dict = {}
        for ray_path, frac in zip( ray_list, frac_list ):
            try:
                r_dict = model_space.grid.get_weight( ray_path )
            except AssertionError:
                self.coord_fail( 'outside grid area' )
                return None
            for k,v in r_dict.items():
                prev = total_dict.get( k, 0 )
                total_dict[ k ] = prev + v*frac
            
        #convert x-y-z into lay-row-col
        result = { (lay,row,col):val for [(col,row,lay,),val]
                   in total_dict.items() if val > 0.0 }
        return result
