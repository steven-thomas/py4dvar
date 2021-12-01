"""
oco2lite_preprocess.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""



import glob
from netCDF4 import Dataset
import os

import context
from fourdvar.params.root_path_defn import store_path
import fourdvar.util.file_handle as fh
from model_space import ModelSpace
from obsTROPOMI_defn import ObsTROPOMI
import super_obs_util as so_util

#-CONFIG-SETTINGS---------------------------------------------------------

#'filelist': source = list of OCO2-Lite files
#'directory': source = directory, use all files in source
#'pattern': source = file_pattern_string, use all files that match pattern
source_type = 'directory'

source = os.path.join( store_path, 'obs_TROPOMI_data' )
#source = os.path.join( store_path, 'obs_1day' )

output_file = './TROPOMI_observed.pic.gz'

#if true interpolate between 2 closest time-steps, else assign to closet time-step
interp_time = False

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
#organise variables by group 
root_var = [ 'pixel_id',
             'latitude_center',
             'longitude_center',
             'time',
             'solar_zenith_angle',
             'viewing_zenith_angle',
             'solar_azimuth_angle',
             'viewing_azimuth_angle']
             #'co_column',
             #'co_column_precision',
             #'co_profile_aprior',
             #'pressure_levels',
             #'co_profile_apriori',
             #'co_column_averaging_kernal',
             #'pressure_weight' ]
target_var = ['co_column',
             'co_column_precision',
             'co_profile_apriori',
             #'pressure_levels',
             'co_profile_apriori',
             'co_column_averaging_kernel']
#sounding_var = [ 'solar_azimuth_angle', 'sensor_azimuth_angle', 'operation_mode' ]
meteo_var = ['landflag', 'pressure_levels']
diagnostics_var = ['processing_quality_flags']


obslist = []
for fname in filelist:
    print('read {}'.format( fname ))
    var_dict = {}
    with Dataset( fname, 'r' ) as f:
        size = f.dimensions[ 'nobs' ].size
        for var in root_var:
            var_dict[ var ] = f.groups['instrument'].variables[ var ][:]
        for var in target_var:
            var_dict[ var ] = f.groups['target_product'].variables[ var ][:]
        #for var in sounding_var:
        #    var_dict[ var ] = f.groups[ 'Sounding' ].variables[ var ][:]
        for var in meteo_var:
            var_dict[ var ] = f.groups[ 'meteo' ].variables[ var ][:]
        for var in diagnostics_var:
            var_dict[ var ] = f.groups[ 'diagnostics' ].variables[ var ][:]

    print('found {} soundings'.format( size ))
    
    sounding_list = []
    for i in range( size ):
        src_dict = { k: v.squeeze()[i] for k,v in list(var_dict.items()) }
        lat = src_dict['latitude_center']
        lon = src_dict['longitude_center']
        if so_util.max_quality_only is True: # and src_dict['processing_quality_flags'] != 0:
            pass
        elif so_util.surface_type != -1 and src_dict['landflag'] != so_util.surface_type:
            pass
        elif so_util.operation_mode != -1 and src_dict['operation_mode'] != so_util.operation_mode:
            pass
        elif model_grid.lat_lon_inside( lat=lat, lon=lon ):
            if so_util.group_by_second is True:
                src_dict['sec'] = int( src_dict['time'][0])
            sounding_list.append( src_dict )
           # print(src_dict['time'][0])
   # del var_dict

    if so_util.group_by_second is True:
        sec_list = list( set( [ s['sec'] for s in sounding_list ] ) )
        merge_list = []
        for sec in sec_list:
            sounding = so_util.merge_second( [ s
                       for s in sounding_list if s['sec'] == sec ] )
            merge_list.append( sounding )
        sounding_list = merge_list
         

   # print(ObsTROPOMI.__dict__)
   # print(len(sounding_list))
    for sounding in sounding_list:
        obs = ObsTROPOMI.create( **sounding )
        print(sounding)
        obs.interp_time = interp_time
        obs.model_process( model_grid )
        if obs.valid is True:
            obslist.append( obs.get_obsdict() )
    
    
if so_util.group_by_column is True:
    obslist = [ o for o in obslist if so_util.is_single_column(o) ]
    col_list = list( set( [ so_util.get_col_id(o) for o in obslist ] ) )
    merge_list = []
    for col in col_list:
        obs = so_util.merge_column( [ o for o in obslist
                                      if so_util.get_col_id(o) == col ] )
        merge_list.append( obs )
    obslist = merge_list
    print(obslist, "<-obs list")
    print(col_list, "<- col list")
    print(merge_list, "<- merge list")
if len( obslist ) > 0:
    domain = model_grid.get_domain()
    datalist = [ domain ] + obslist
    fh.save_list( datalist, output_file )
    print('recorded observations to {}'.format( output_file ))
else:
    print('No valid observations found, no output file generated.')
