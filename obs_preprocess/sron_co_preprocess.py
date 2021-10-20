"""
sron_co_preprocess.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
import glob
import numpy as np
import datetime as dt

import context
from obsSRON_defn import ObsSRON
from model_space import ModelSpace
from netCDF4 import Dataset
import fourdvar.util.file_handle as fh
from fourdvar.util.date_handle import start_date, end_date
from fourdvar.params.root_path_defn import store_path
import fourdvar.params.input_defn as input_defn

##NS added:
import pdb

#-CONFIG-SETTINGS---------------------------------------------------------

#'filelist': source = list of OCO2-Lite files
#'directory': source = directory, use all files in source
#'pattern': source = file_pattern_string, use all files that match pattern
source_type = 'filelist'
     
#source = [ os.path.join( store_path, 'obs_src', 's5p_l2_co_0007_04270.nc' ) ]
source = glob.glob( '/data/gpfs/projects/punim0762/nshahrokhis/sron_data/s5p_l2_co_0007_*.nc' ) 

output_file = input_defn.obs_file

# minimum qa_value before observation is discarded
qa_cutoff = 0.5
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

obslist = []
for fname in filelist:
    print 'read {}'.format( fname )
    var_dict = {}
    with Dataset( fname, 'r' ) as f:
        instrument = f.groups['instrument']
        meteo = f.groups['meteo']
        product = f.groups['target_product']
        diag = f.groups['diagnostics']
        
        time = instrument.variables['time'][:,:]
        latitude_center = instrument.variables['latitude_center'][:]
        longitude_center = instrument.variables['longitude_center'][:]
        latitude_corners = instrument.variables['latitude_corners'][:,:]
        longitude_corners = instrument.variables['longitude_corners'][:,:]
        solar_zenith_angle = instrument.variables['solar_zenith_angle'][:]
        viewing_zenith_angle = instrument.variables['viewing_zenith_angle'][:,0]
        solar_azimuth_angle = instrument.variables['solar_azimuth_angle'][:]
        viewing_azimuth_angle = instrument.variables['viewing_azimuth_angle'][:,0]
        pressure_levels = meteo.variables['pressure_levels'][:,:]
        co_column = product.variables['co_column'][:]
        co_column_precision = product.variables['co_column_precision'][:]
        co_column_apriori = product.variables['co_column_apriori'][:]
        co_profile_apriori = product.variables['co_profile_apriori'][:,:]
        qa_value = diag.variables['qa_value'][:]

    mask_arr = np.ma.getmaskarray( co_column )

    #quick filter out: mask, lat, lon and quality
    lat_filter = np.logical_and( latitude_center>=model_grid.lat_bounds[0],
                                 latitude_center<=model_grid.lat_bounds[1] )
    lon_filter = np.logical_and( longitude_center>=model_grid.lon_bounds[0],
                                 longitude_center<=model_grid.lon_bounds[1] )
    mask_filter = np.logical_not( mask_arr )
    qa_filter = ( qa_value > qa_cutoff )
    include_filter = np.logical_and.reduce((lat_filter,lon_filter,mask_filter,qa_filter))

    epoch = dt.datetime.utcfromtimestamp(0)
    sdate = dt.datetime( start_date.year, start_date.month, start_date.day )
    edate = dt.datetime( end_date.year, end_date.month, end_date.day )
    size = include_filter.sum()
    print 'found {} soundings'.format( size )
    for i,iflag in enumerate(include_filter):
        if iflag:
            #scanning time is slow, do it after other filters.
            tsec = (dt.datetime(*time[i,:])-epoch).total_seconds()
            time0 = (sdate-epoch).total_seconds()
            time1 = (edate-epoch).total_seconds() + 24*60*60
            if tsec < time0 or tsec > time1:
                continue
            
            var_dict = {}
            var_dict['time'] = dt.datetime( *time[i,:] )
            var_dict['latitude_center'] = latitude_center[i]
            var_dict['longitude_center'] = longitude_center[i]
            var_dict['latitude_corners'] = latitude_corners[i,:]
            var_dict['longitude_corners'] = longitude_corners[i,:]
            var_dict['solar_zenith_angle'] = solar_zenith_angle[i]
            var_dict['viewing_zenith_angle'] = viewing_zenith_angle[i]
            var_dict['solar_azimuth_angle'] = solar_azimuth_angle[i]
            var_dict['viewing_azimuth_angle'] = viewing_azimuth_angle[i]
            var_dict['pressure_levels'] = pressure_levels[i,:]
            var_dict['co_column'] = co_column[i]
            var_dict['co_column_precision'] = co_column_precision[i]
            var_dict['co_column_apriori'] = co_column_apriori[i]
            var_dict['co_profile_apriori'] = co_profile_apriori[i,:]
            var_dict['qa_value'] = qa_value[i]

            obs = ObsSRON.create( **var_dict )
            obs.interp_time = False
            obs.model_process( model_grid )
            if obs.valid is True:
                obslist.append( obs.get_obsdict() )
                ##pdb.set_trace() ##NS added
if len( obslist ) > 0:
    domain = model_grid.get_domain()
    domain['is_lite'] = False
    datalist = [ domain ] + obslist     
    fh.save_list( datalist, output_file )
    print 'recorded observations to {}'.format( output_file )
else:
    print 'No valid observations found, no output file generated.'
