
import numpy as np
import pyproj
from bisect import bisect

import context
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt

# name of each category (must be less than 16 characters)
CAT_NAME_LIST = ['MORNING','DAYTIME','EVENING','NIGHTTIME']
# start of category time, HHMMSS (in approx. local time)
CAT_START_TIME = [ 30000, 90000, 150000, 210000 ]

# list of attributes from emis file to copy
ATTR_LIST = [ 'STIME', 'TSTEP', 'NCOLS', 'NROWS', 'NLAYS', 'GDTYP', 'P_ALP',
              'P_BET', 'P_GAM', 'XCENT', 'YCENT', 'XORIG', 'YORIG', 'XCELL',
              'YCELL', 'VGTYP', 'VGTOP', 'VGLVLS', 'VAR-LIST' ]

# No. seconds in a day
DAYSEC = 24*60*60

#radius of the Earth, in meters
EARTH_RAD = 6370000

def hms2sec( hms ):
    hms = int(hms)
    return (hms//10000)*3600 + (((hms//100)%100)*60) + (hms%100)

def get_time_offset( attr_dict ):
    """get No. seconds to convert cat_start_time to UTC (approx)"""
    xorig = float( attr_dict[ 'XORIG' ] )
    xsize = float( attr_dict[ 'XCELL' ] ) * float( attr_dict[ 'NCOLS' ] )
    yorig = float( attr_dict[ 'YORIG' ] )
    ysize = float( attr_dict[ 'YCELL' ] ) * float( attr_dict[ 'NROWS' ] )
    x_mid = xorig + .5*xsize
    y_mid = yorig + .5*ysize
    alp = float( attr_dict[ 'P_ALP' ] )
    bet = float( attr_dict[ 'P_BET' ] )
    gam = float( attr_dict[ 'P_GAM' ] )
    ycent = float( attr_dict[ 'YCENT' ] )
    proj_str = '+proj=lcc +lat_1={0} +lat_2={1} +lat_0={2} +lon_0={3} +a={4} +b={4}'
    proj = pyproj.Proj( proj_str.format( alp, bet, ycent, gam, EARTH_RAD ) )
    lon,lat = proj( x_mid, y_mid, inverse=True )
    return (lon % 360.) * 240.

def get_1d_step_cat( attr_dict, nstep ):
    start_sec = hms2sec( attr_dict['STIME'] )
    step_len = hms2sec( attr_dict['TSTEP'] )
    step_sec = np.cumsum( np.zeros(nstep)+step_len )
    step_sec = step_sec + start_sec - step_len
    step_sec = step_sec % DAYSEC
    
    cat_off = get_time_offset( attr_dict )
    cat_sec = [ (hms2sec(ct)-cat_off)%DAYSEC for ct in CAT_START_TIME ]
    cat_ind = range(len(CAT_NAME_LIST))
    cat_sec,cat_ind = zip(*sorted(zip(cat_sec,cat_ind)))
    
    step_ind = [ bisect( cat_sec, t ) - 1 for t in step_sec ]
    step_cat = np.array( [ cat_ind[ i ] for i in step_ind ] )
    return np.array( step_cat ).astype( int )

def make_diurnal_file():
    efile = dt.replace_date( template.emis, dt.start_date )
    efile_attr_dict = ncf.get_all_attr( efile )
    attr_dict = { attr: efile_attr_dict[attr] for attr in ATTR_LIST }
    #add CAT-LIST to diurnal attributes
    attr_dict['CAT-LIST'] = ''.join([ '{:<16}'.format(c) for c in CAT_NAME_LIST ])

    spc_list = attr_dict['VAR-LIST'].strip().split()
    arr_shape = ncf.get_variable( efile, spc_list[0] ).shape
    (tstep,lay,row,col) = arr_shape
    
    step_cat_1d = get_1d_step_cat( attr_dict, tstep )
    cat_arr = np.zeros(arr_shape).astype(int) + step_cat_1d.reshape( (tstep,1,1,1) )
    
    dim_dict = { 'TSTEP':tstep, 'LAY':lay, 'ROW':row, 'COL':col }
    var_dict = { spc: ('u1', ('TSTEP','LAY','ROW','COL',), cat_arr.copy(), )
                 for spc in spc_list }
    
    ncf_file = ncf.create( path=template.diurnal, attr=attr_dict,
                           dim=dim_dict, var=var_dict, is_root=True )
    ncf_file.close()
    return None

if __name__ == "__main__":
    make_diurnal_file()
