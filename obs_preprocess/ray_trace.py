"""
ray_trace.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

class Grid( object ):
    def __init__( self, offset, spacing ):
        assert len( offset ) == len( spacing ), 'dimension mis-match'
        for s in spacing:
            msg = 'all spacings in a dimension must have the same sign'
            assert (np.sign(s[0]) == np.sign(s[1:])).all(), msg
        self.ndim = len( offset )
        self.shape = tuple( len(s) for s in spacing )
        tmp = [ np.insert( spacing[ dim ], 0, offset[ dim ] ) for dim in range( self.ndim ) ]
        self.edges = [ np.cumsum( arr ) for arr in tmp ]
        return None
    
    def get_cell_1d( self, value, dim ):
        assert 0 <= dim < self.ndim, 'invalid dimension'
        sign = np.sign(self.edges[dim][-1] - self.edges[dim][0])
        edge_arr = self.edges[dim]
        if sign < 0:
            edge_arr = edge_arr[::-1]
        assert edge_arr[0] <= value <= edge_arr[-1], 'value outside grid'
        result = np.searchsorted( edge_arr, value ) - 1
        result = np.clip( result, 0, self.shape[ dim ] - 1 )
        if sign < 0:
            result = self.shape[dim]-1 - result
        return result
    
    def get_cell( self, point ):
        assert point.ndim == self.ndim, 'dimension mis-match'
        return tuple( self.get_cell_1d( point[dim], dim ) for dim in range( self.ndim ) )
    
    def get_collision_1d( self, ray, dim ):
        assert ray.ndim == self.ndim, 'dimension mis-match'
        assert 0 <= dim < self.ndim, 'invalid dimension'
        p1, p2 = ray.get_minmax_1d( dim )
        ind1 = self.get_cell_1d( p1, dim ) + 1
        ind2 = self.get_cell_1d( p2, dim ) + 1
        [ind1,ind2] = sorted([ind1,ind2])
        return self.edges[ dim ][ ind1:ind2 ]
    
    def get_ray_cell_dist( self, ray ):
        assert ray.ndim == self.ndim, 'dimension mis-match'
        ray_par_list = []
        for dim in range( self.ndim ):
            edge_collision = self.get_collision_1d( ray, dim )
            ray_par_list.extend( [ ray.get_par( edge, dim ) for edge in edge_collision ] )
        ray_par_list.sort()
        assert ray_par_list[0] >= 0, 'collision outside ray path'
        assert ray_par_list[-1] <= 1, 'collision outside ray path'
        ray_par_list.insert( 0, 0 )
        ray_par_list.append( 1 )
        point_list = [ ray.get_point( par ) for par in ray_par_list ]
        
        result = {}
        for prev, point in zip( point_list[:-1], point_list[1:] ):
            mid_point = Point.mid_point( prev, point )
            co_ord = self.get_cell( mid_point )
            #weight = point.dist( prev ) / ray.length
            result[ co_ord ] = result.get( co_ord, 0 ) + point.dist( prev )
        return result
    
    def get_ray_cell_area( self, ray_list ):
        assert self.ndim == 3
        xdim, ydim, zdim = 0,1,2
        assert all([r.ndim == self.ndim for r in ray_list]),'dimension mis-match'
        area_dict = {}
        #find footprint of the vertical ray paths for each layer
        ray_collision = []
        for ray in ray_list:
            if ray.start[zdim] > ray.end[zdim]:
                ray = Ray( ray.end, ray.start )
            edge_collision = self.get_collision_1d( ray, zdim )
            ray_par_list = [ ray.get_par( edge, zdim ) for edge in edge_collision ]
            ray_par_list.sort()
            assert ray_par_list[0] >= 0, 'collision outside ray path'
            assert ray_par_list[-1] <= 1, 'collision outside ray path'
            if ray_par_list[0] > 0: ray_par_list.insert( 0, 0 )
            if ray_par_list[-1] == 1: ray_par_list.pop[-1]
            point_list = [ ray.get_point( par ) for par in ray_par_list ]
            ray_collision.append( point_list )
        assert len(zip(*ray_collision)) == self.shape[zdim]

        #utility function, returns True if point inside polygon/footprint
        def in_poly( pnt, poly_list ):
            """
            Copyright 2000 softSurfer, 2012 Dan Sunday
            This code may be freely used and modified for any purpose
            providing that this copyright notice is included with it.
            SoftSurfer makes no warranty for this code, and cannot be held
            liable for any real or imagined damage resulting from its use.
            Users of this code must verify correctness for their application.
            """
            is_left = lambda p0,p1,p2: ((p1[xdim]-p0[xdim])*(p2[ydim]-p0[ydim])
                                       -(p2[xdim]-p0[xdim])*(p1[ydim]-p0[ydim]))
            wn = 0
            for ps, pe in zip( poly_list, poly_list[1:]+[poly_list[0]] ):
                if ps[ydim] <= pnt[ydim]:
                    if pe[ydim] > pnt[ydim] and is_left(ps,pe,pnt) > 0:
                        wn += 1
                else:
                    if pe[ydim] <= pnt[ydim] and is_left(ps,pe,pnt) < 0:
                        wn -= 1
            return (wn != 0)
        
        #construct a dict, key=gridcell-coord, value=points of footprint polygon inside gridcell
        for zind,p_list in enumerate(zip(*ray_collision)):
            p_list = list(p_list)
            xmin = self.get_cell_1d( min([ p[ xdim ] for p in p_list ]), xdim )
            xmax = self.get_cell_1d( max([ p[ xdim ] for p in p_list ]), xdim )
            ymin = self.get_cell_1d( min([ p[ ydim ] for p in p_list ]), ydim )
            ymax = self.get_cell_1d( max([ p[ ydim ] for p in p_list ]), ydim )
            #dict of all possible footprint coords for this layer
            coord_dict = { (x,y,zind):[] for x in range(xmin,xmax+1)
                           for y in range(ymin,ymax+1) }
            #add each corner inside footprint to its 4 coords
            for coord in coord_dict.keys():
                cpnt = ( self.edges[xdim][coord[0]],
                         self.edges[ydim][coord[1]],
                         self.edges[zdim][coord[2]] )
                if in_poly( cpnt, p_list ) is True:
                    coord_dict[ (coord[0],coord[1],coord[2],) ].append( cpnt )
                    coord_dict[ (coord[0]-1,coord[1],coord[2],) ].append( cpnt )
                    coord_dict[ (coord[0],coord[1]-1,coord[2],) ].append( cpnt )
                    coord_dict[ (coord[0]-1,coord[1]-1,coord[2],) ].append( cpnt )
            #add each edge collision of footprint to its 2 coords
            p_rays = [ Ray(p0,p1) for p0,p1 in zip(p_list,p_list[1:]+[p_list[0]]) ]
            for ray in p_rays:
                ray_par_list = []
                for dim in [xdim,ydim]:
                    edge_collision = self.get_collision_1d( ray, dim )
                    ray_par_list.extend( [ ray.get_par( edge, dim )
                                           for edge in edge_collision ] )
                if len(ray_par_list) == 0:
                    continue #skip if no collision found
                ray_par_list.sort()
                assert ray_par_list[0] >= 0, 'collision outside ray path'
                assert ray_par_list[-1] <= 1, 'collision outside ray path'
                coll_pnt_list = [ ray.get_point( par ) for par in ray_par_list ]
                loc_list = [0] + ray_par_list + [1]
                loc_list = [.5*(i+j) for i,j in zip(loc_list[:-1],loc_list[1:])]
                loc_list = [ ray.get_point( par ) for par in loc_list ]
                loc_list = [ self.get_cell( pnt ) for pnt in loc_list ]
                loc_list = [ (pnt[xdim],pnt[ydim],zind,) for pnt in loc_list ]
                for i,pnt in enumerate(coll_pnt_list):
                    coord_dict[ loc_list[i] ].append( pnt )
                    coord_dict[ loc_list[i+1] ].append( pnt )
            
            #add each point of footprint to its coord
            for pnt in p_list:
                coord = self.get_cell( pnt )
                coord = ( coord[xdim], coord[ydim], zind, )
                coord_dict[ coord ].append( pnt )
            
            #strip out any empty coords
            #sort poly points into counter-clockwise order, use first pnt as origin
            for coord, pnt_list in coord_dict.items():
                if pnt_list == []:
                    coord_dict.pop(coord)
                    continue
                assert len(pnt_list) >= 3, 'cannot form polygon'
                ccw_list = []
                ox,oy,_ = pnt_list[0]
                for p in pnt_list[1:]:
                    x = p[xdim] - ox
                    y = p[ydim] - oy
                    ccw_list.append( (np.arctan2(y,x),p,) )
                ccw_list.sort()
                poly_list = [ c[1] for c in ccw_list ]
                poly_list = [pnt_list[0]] + poly_list

                #calc area of coord polygon
                xarr = np.array( [ p[xdim] for p in poly_list ] )
                yarr = np.array( [ p[ydim] for p in poly_list ] )
                #"shoelace formula"
                area = 0.5 * np.abs( np.dot( xarr, np.roll(yarr,1) )
                                     - np.dot( yarr, np.roll(xarr,1) ) )
                area_dict[ coord ] = area
        return area_dict
    
    def get_weight( self, ray ):
        dist_dict = self.get_ray_cell_dist( ray )
        result = {}
        for k,v in dist_dict.items():
            result[ k ] = v / ray.length
        return result

class Ray( object ):
    def __init__( self, start_point, end_point ):
        self.start = Point( start_point )
        self.end = Point( end_point )
        assert self.start.ndim == self.end.ndim, 'dimension mis-match'
        self.ndim = self.start.ndim
        self.length = self.start.dist( self.end )
        return None
    
    def get_minmax_1d( self, dim ):
        assert 0 <= dim < self.ndim, 'invalid dimension'
        start = self.start[ dim ]
        end = self.end[ dim ]
        return sorted( [start, end] )
    
    def get_par( self, value, dim ):
        assert 0 <= dim < self.ndim, 'invalid dimension'
        vmin, vmax = self.get_minmax_1d( dim )
        assert vmin <= value <= vmax, 'value outside ray path'
        assert vmin < vmax, 'invalid collision for ray'
        return float(value - self.start[dim]) / float(self.end[dim] - self.start[dim])
    
    def get_point( self, par ):
        assert 0 <= par <= 1, 'par outside ray path'
        co_ord = [ self.start[d] + par*(self.end[d] - self.start[d]) for d in range( self.ndim ) ]
        return Point( co_ord )

class Point( object ):
    def __init__( self, co_ord ):
        if isinstance( co_ord, Point ):
            co_ord = co_ord.co_ord
        self.co_ord = co_ord
        self.ndim = len( co_ord )
        return None
    
    def __getitem__( self, dim ):
        return self.co_ord[ dim ]
    
    def dist( self, other ):
        assert isinstance( other, Point ), 'dist only between 2 points'
        assert self.ndim == other.ndim, 'dimension mis-match'
        gen = ( (self.co_ord[i] - other.co_ord[i])**2 for i in range( self.ndim ) )
        return np.sqrt( np.sum( gen ) )
    
    @classmethod
    def mid_point( cls, p1, p2 ):
        assert isinstance( p1, Point ) and isinstance( p2, Point ), 'mid_point only between 2 points'
        assert p1.ndim == p2.ndim, "dimension mis-match"
        return cls( [ 0.5*(p1[d] + p2[d]) for d in range( p1.ndim ) ] )


if __name__ == "__main__":
    offset = (0,0,0,)
    spacing = (np.ones(4),np.ones(4),np.ones(4),)
    start = (0.5,0.75,0.25,)
    end = (3.75,3.25,3.5,)
    my_grid = Grid( offset, spacing )
    my_ray = Ray( start, end )
    weight = my_grid.get_weight( my_ray )
    for k,v in weight.items():
        print '{:}: {:.3}'.format( k, v )

