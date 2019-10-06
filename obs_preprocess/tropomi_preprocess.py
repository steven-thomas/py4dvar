
import os
import glob
import numpy as np
from netCDF4 import Dataset

import context
from obs_preprocess.obsTropomi_defn import ObsTropomi
from obs_preprocess.model_space import ModelSpace
import fourdvar.util.file_handle as fh
from fourdvar.params.root_path_defn import store_path

#-CONFIG-SETTINGS---------------------------------------------------------

#'filelist': source = list of OCO2-Lite files
#'directory': source = directory, use all files in source
#'pattern': source = file_pattern_string, use all files that match pattern
#source_type = 'directory'
source_type = 'pattern'

source = os.path.join( store_path, 'obs_src_data', 'obs_sample.nc' )

#output_file = './methane_month_obs.pic.gz'
output_file = './methane_day_obs.pic.gz'

#--------------------------------------------------------------------------

model_grid = ModelSpace.create_from_fourdvar()

if source_type.lower() == 'filelist':
    filelist = [ os.path.realpath( f ) for f in source ]
elif source_type.lower() == 'pattern':
    filelist = [ os.path.realpath( f ) for f in glob.glob( source ) ]
elif source_type.lower() == 'directory':
    dirname = os.path.realpath( source )
    filelist = [ os.path.join( dirname, f )
                 for f in os.listdir( dirname )
                 if os.path.isfile( os.path.join( dirname, f ) ) ]
else:
    raise TypeError( "source_type '{}' not supported".format(source_type) )

root_var = [ 'orbit',
             'latitude_mid_point',
             'longitude_mid_point',
             'latitude_bound',
             'longitude_bound',
             'time',
             'solar_zenith',
             'sensor_zenith',
             'solar_azimuth',
             'sensor_azimuth',
             'qa',
             'methane_mixing_ratio',
             'methane_uncertainty',
             'profile_apriori',
             'pressure_interval',
             'averaging_kernel',
             'surface_pressure' ]
methane_uncertainty_floor = 10. #ppb
obslist = []
for fname in filelist:
    print 'read {}'.format( fname )
    var_dict = {}
    with Dataset( fname, 'r' ) as f:
#        #only grab obs for 2018-06-01
#        d1_start = 265500000
#        d1_end = 265600000
#        time_arr = f.variables[ 'time' ][:]
#        day_filter = np.logical_and( time_arr>=d1_start, time_arr<=d1_end )
#        size = day_filter.sum()
        size = f.dimensions[ 'time' ].size
        for var in root_var:
            var_dict[ var ] = f.variables[ var ][:]
#            var_dict[ var ] = f.variables[ var ][day_filter]
    print 'found {} soundings'.format( size )
    
    for i in range( size ):
        src_dict = { k: v[i] for k,v in var_dict.items() }
        if src_dict['methane_uncertainty'] < methane_uncertainty_floor:
            src_dict['methane_uncertainty'] = methane_uncertainty_floor
        obs = ObsTropomi.create( **src_dict )
        obs.interp_time = False
        obs.model_process( model_grid )
        if obs.valid is True:
            obslist.append( obs.get_obsdict() )

if len( obslist ) > 0:
    domain = model_grid.get_domain()
    datalist = [ domain ] + obslist
    fh.save_list( datalist, output_file )
    print 'recorded observations to {}'.format( output_file )
else:
    print 'No valid observations found, no output file generated.'
