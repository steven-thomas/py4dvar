from netCDF4 import Dataset
import numpy
from datetime import datetime
nc = Dataset('/scratch/w22/cm5310/store_share_p4d/obs_TROPOMI_data/s5p_l2_co_0007_03699.nc')


t = nc.groups['instrument'].variables['time']
dates = []
for i in range(10):
    t_list = t[i].tolist()
    date = datetime(year = t_list[0], month = t_list[1], day = t_list[2], hour = t_list[3], minute = t_list[4], second = t_list[5])
    seconds = date.timestamp()
    dates.append(seconds)
    

#t_list = t[0].tolist))
#date = (datetime(year = t_list[0], month = t_list[1], day = t_list[2], hour = t_list[3], minute = t_list[4], second = t_list[5]))

print(seconds)


