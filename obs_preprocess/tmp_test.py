
import numpy as np
import context

from obs_preprocess.ray_trace import Grid, demo_point, Ray

#p1 = Point([1,1])
#p2 = Point([2,2])
#p3 = Point.mid_point(p1,p2)

#print(p3)

offset = [0,0]
spacing = [np.ones(5),np.ones(5)]
grid = Grid(offset,spacing)

ray = Ray([1,1],[2,2])
output= grid.get_ray_cell_dist(ray)

print(output)

