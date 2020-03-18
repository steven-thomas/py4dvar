
import os
import glob
import numpy as np

import context
from obsTropomi_defn import ObsTropomi
from model_space import ModelSpace
from netCDF4 import Dataset
import fourdvar.util.file_handle as fh
from fourdvar.params.root_path_defn import store_path
import fourdvar.params.input_defn as input_defn

#-CONFIG-SETTINGS---------------------------------------------------------

#'filelist': source = list of OCO2-Lite files
#'directory': source = directory, use all files in source
#'pattern': source = file_pattern_string, use all files that match pattern
source_type = 'pattern'

#source = os.path.join( store_path, 'obs_src' )
#source = os.path.join( store_path, 'obs_src', 'S5P*.nc' 
source = os.path.join( store_path, 'obs_src', 'tmp_test_obs.nc' )

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
        product = f.groups['PRODUCT']
        geoloc = f.groups['PRODUCT'].groups['SUPPORT_DATA'].groups['GEOLOCATIONS']
        detail = f.groups['PRODUCT'].groups['SUPPORT_DATA'].groups['DETAILED_RESULTS']
        
        latitude_center = product.variables['latitude'][:,:,:]
        longitude_center = product.variables['longitude'][:,:,:]
        latitude_bounds = geoloc.variables['latitude_bounds'][:,:,:,:]
        longitude_bounds = geoloc.variables['longitude_bounds'][:,:,:,:]
        solar_zenith_angle = geoloc.variables['solar_zenith_angle'][:,:,:]
        solar_azimuth_angle = geoloc.variables['solar_azimuth_angle'][:,:,:]
        viewing_zenith_angle = geoloc.variables['viewing_zenith_angle'][:,:,:]
        viewing_azimuth_angle = geoloc.variables['viewing_azimuth_angle'][:,:,:]
        time_utc = product.variables['time_utc'][:,:]
        qa_value = product.variables['qa_value'][:,:,:]
        co_total_column = product.variables['carbonmonoxide_total_column'][:,:,:]
        co_total_column_precision = product.variables['carbonmonoxide_total_column_precision'][:,:,:]
        layer = product.variables['layer'][:]
        column_averaging_kernel = detail.variables['column_averaging_kernel'][:,:,:,:]
        pressure_levels = detail.variables['pressure_levels'][:,:,:,:]
    #copy time value for every ground pixel
    ntime, nscan, npix = qa_value.shape
    time = np.stack([time_utc]*npix, axis=2)
    #divide kernel by layer height for each layer
    lh = np.concatenate( [layer, [0]] )
    layer_height = (lh[:-1]-lh[1:]).reshape((1,1,1,-1,))
    averaging_kernel = column_averaging_kernel / layer_height
    #make a quick first-pass filter for obs, with lat/lon bounds and quality>.5
    lat_min = latitude_bounds.min(axis=3)
    lat_max = latitude_bounds.max(axis=3)
    lon_min = longitude_bounds.min(axis=3)
    lon_max = longitude_bounds.max(axis=3)
    mask = ( (lat_min >= model_grid.lat_bounds[0])
             & (lat_max <= model_grid.lat_bounds[1])
             & (lon_min >= model_grid.lon_bounds[0])
             & (lon_max <= model_grid.lon_bounds[1])
             & (qa_value >= qa_cutoff) )

    size = mask.sum()
    print 'found {} soundings'.format( size )
    for i in range(size):
        var_dict = {}
        var_dict['latitude_center'] = latitude_center[mask][i]
        var_dict['longitude_center'] = longitude_center[mask][i]
        var_dict['latitude_bounds'] = latitude_bounds[mask][i,:]
        var_dict['longitude_bounds'] = longitude_bounds[mask][i,:]
        var_dict['solar_zenith_angle'] = solar_zenith_angle[mask][i]
        var_dict['solar_azimuth_angle'] = solar_azimuth_angle[mask][i]
        var_dict['viewing_zenith_angle'] = viewing_zenith_angle[mask][i]
        var_dict['viewing_azimuth_angle'] = viewing_azimuth_angle[mask][i]
        var_dict['time'] = time[mask][i]
        var_dict['qa_value'] = qa_value[mask][i]
        var_dict['co_total_column'] = co_total_column[mask][i]
        var_dict['co_total_column_precision'] = co_total_column_precision[mask][i]
        var_dict['averaging_kernel'] = averaging_kernel[mask][i,:]
        var_dict['pressure_levels'] = pressure_levels[mask][i,:]

        obs = ObsTropomi.create( **var_dict )
        obs.interp_time = False
        obs.model_process( model_grid )
        if obs.valid is True:
            obslist.append( obs.get_obsdict() )

if len( obslist ) > 0:
    domain = model_grid.get_domain()
    domain['is_lite'] = False
    datalist = [ domain ] + obslist
    fh.save_list( datalist, output_file )
    print 'recorded observations to {}'.format( output_file )
else:
    print 'No valid observations found, no output file generated.'
