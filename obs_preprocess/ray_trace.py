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
       # p1 = -24
       # p2 = -25
        ind1 = self.get_cell_1d( p1, dim ) + 1
        ind2 = self.get_cell_1d( p2, dim ) + 1
       # [ind1,ind2] = sorted([ind1,ind2])
       
       
        [ind1,ind2] = sorted([ind1,ind2])
       
        return self.edges[ dim ][ ind1:ind2 ]
    
    def get_ray_cell_dist( self, ray ):
       # print('being called')
        if ray.ndim != self.ndim:
           
            assert ray.ndim == self.ndim, 'dimension mis-match'
        ray_par_list = []
        for dim in range( self.ndim ):
            edge_collision = self.get_collision_1d( ray, dim )
            ray_par_list.extend( [ ray.get_par( edge, dim ) for edge in edge_collision ] )
        ray_par_list.sort()
        if ray_par_list[0] < 0:
           
            assert ray_par_list[0] >= 0, 'collision outside ray path'
        if ray_par_list[-1] > 1:
           
            assert ray_par_list[-1] <= 1, 'collision outside ray path'
        ray_par_list.insert( 0, 0 )
        ray_par_list.append( 1 )
        point_list = [ ray.get_point( par ) for par in ray_par_list ]
        
        result = {}
       # print(len(point_list))
       # print("result",result)
        for prev, point in zip( point_list[:-1], point_list[1:] ):
           # print(point)


            mid_point = Point.mid_point( prev, point )
    
            co_ord = self.get_cell( mid_point )
            #weight = point.dist( prev ) / ray.length
            result[ co_ord ] = result.get( co_ord, 0 ) + point.dist( prev )
    
        return result
    
    def get_weight( self, ray ):
        dist_dict = self.get_ray_cell_dist( ray )
        result = {}
        for k,v in list(dist_dict.items()):
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
       # if not (isinstance( p1, Point ) and isinstance( p2, Point )):
        assert isinstance( p1, Point ) and isinstance( p2, Point ), 'mid_point only between 2 points'
       # if not (p1.ndim == p2.ndim): 
           
        assert p1.ndim == p2.ndim, "dimension mis-match"
        return cls( [ 0.5*(p1[d] + p2[d]) for d in range( p1.ndim ) ] )

demo_point = Point([3,3])
if __name__ == "__main__":

    p1 = Point([1,1])
    p2 = Point([2,2])
    p3 = Point.mid_point(p1,p2)
    
    """
    offset = (0,0,0,)
    spacing = (np.ones(4),np.ones(4),np.ones(4),)
    start = (0.5,0.75,0.25,)
    end = (3.75,3.25,3.5,)
    my_grid = Grid( offset, spacing )
    my_ray = Ray( start, end )
    weight = my_grid.get_weight( my_ray )
    for k,v in list(weight.items()):
        print('{:}: {:.3}'.format( k, v ))
    """
