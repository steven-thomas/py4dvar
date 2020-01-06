
import os
import glob
import numpy as np
from netCDF4 import Dataset
import datetime as dt

import context
from obs_preprocess.obsGEOCARB_defn import ObsGEOCARB_XCO2, ObsGEOCARB_XCO
from obs_preprocess.model_space import ModelSpace
import fourdvar.util.file_handle as fh
from fourdvar.params.root_path_defn import store_path

#-CONFIG-SETTINGS---------------------------------------------------------

date_list = [ 20060300 + i for i in range(23,30) ]
time_list = [ 4138 + i*10**4 for i in [14,18,22] ]

retrieval_src = os.path.join( store_path, 'obs_src_data', 'l2_retrievals',
                              'l2_mexico_city_{:}_{:}.h5' )
geometry_src = os.path.join( store_path, 'obs_src_data', 'geometry',
                             'mexico_city_{:}_{:}.hdf' )
profile_src = os.path.join( store_path, 'obs_src_data', 'prior_profiles',
                            'prior_profiles_mexico_city_{:}_{:}.txt' )

#output_file = './oco2_observed.pickle.zip'
output_file = './GEOCARB_CO_CO2_observed.pic.gz'

#skip CO/CO2 obs if xco2_uncert is too large (dud obs)
skip_large_unc = True
large_unc_value = 10.

nframe = 51
npixel = 51
nlvl = 20

#--------------------------------------------------------------------------

model_grid = ModelSpace.create_from_fourdvar()
obslist = []
file_id_list = [ [d,t] for d in date_list for t in time_list ]
for fid in file_id_list:
    ret_fname = retrieval_src.format( *fid )
    geo_fname = geometry_src.format( *fid )
    pro_fname = profile_src.format( *fid )
    if fid == [20060326,224138]:
        print 'omitting {:}, {:} due to bad values'.format( *fid )
        continue
    else:
        print 'reading {:}, {:}'.format( *fid )
    
    with Dataset( ret_fname, 'r' ) as f:
        if len( f.groups.keys() ) == 0:
            print 'no data in {:}'.format( ret_fname )
            continue
        frame_index = f.groups['RetrievalHeader'].variables['exposure_index'][:]
        sounding_id = f.groups['RetrievalHeader'].variables['sounding_id_reference'][:]
        xco2 = f.groups['RetrievalResults'].variables['xco2'][:]
        xco2_uncertainty = f.groups['RetrievalResults'].variables['xco2_uncert'][:]
        xco2_apriori = f.groups['RetrievalResults'].variables['xco2_apriori'][:]
        co2_profile = f.groups['RetrievalResults'].variables['co2_profile_apriori'][:]
        avg_kernel = f.groups['RetrievalResults'].variables['xco2_avg_kernel_norm'][:]
        pressure = f.groups['RetrievalResults'].variables['vector_pressure_levels'][:]
        #p_weight = f.groups['RetrievalResults'].variables['xco2_pressure_weighting_function'][:]
        co_scale = f.groups['RetrievalResults'].variables['co_scale_factor'][:]
        co_unc = f.groups['RetrievalResults'].variables['co_scale_factor_uncert'][:]

    with Dataset( geo_fname, 'r' ) as f:
        latitude = f.groups['Geometry'].variables['latitude_centre'][:]
        longitude = f.groups['Geometry'].variables['longitude_centre'][:]
    
    with open( pro_fname, 'r' ) as f:
        profile_txt = f.readlines()
    profile_vals = profile_txt[-nlvl:]
    profile_units = profile_txt[-nlvl-1]
    profile_names = profile_txt[-nlvl-2]
    profile_labels = profile_names.strip().split()[1:]
    profile_lays = [ [ float(x) for x in l.strip().split()] for l in profile_vals ]
    profile_data = { l:np.array(v) for l,v in zip( profile_labels, zip(*profile_lays) ) }
    
    nobs = len( frame_index )
    print 'found {} soundings'.format( nobs )
    for i in range( nobs ):
        frame_i = (frame_index[i]-1) // npixel
        pixel_i = (frame_index[i]-1) % npixel

        meta_dict = {}
        meta_dict['sounding_id'] = sounding_id[i]
        meta_dict['latitude'] = latitude[ frame_i, pixel_i ]
        meta_dict['longitude'] = longitude[ frame_i, pixel_i ]
        meta_dict['pressure_levels'] = pressure[i,:].copy()
        # Time extracted from sounding id
        meta_dict['time'] = dt.datetime.strptime( str(sounding_id[i]//10**4), '%Y%m%d%H%M%S' )

        xco2_dict = meta_dict.copy()
        xco2_dict['xco2_averaging_kernel'] = avg_kernel[i,:].copy()
        # convert to ppm
        xco2_dict['xco2'] = xco2[i] * 10**6
        xco2_dict['xco2_uncertainty'] = xco2_uncertainty[i] * 10**6
        xco2_dict['xco2_apriori'] = xco2_apriori[i] * 10**6
        xco2_dict['co2_profile_apriori'] = co2_profile[i,:].copy() * 10**6
        
        xco_dict = meta_dict.copy()
        xco_dict['co_scale_factor'] = co_scale[i]
        xco_dict['co_scale_factor_uncert'] = co_unc[i]
        # convert to ppm
        xco_dict['co_profile_apriori'] = profile_data['CO'].copy() * 10**6

        #skip over obs if xco2 uncertainty is too large
        if skip_large_unc is True and xco2_dict['xco2_uncertainty'] > large_unc_value:
            continue

        obs_pair = ( ObsGEOCARB_XCO2.create( **xco2_dict ),
                     ObsGEOCARB_XCO.create( **xco_dict ) )
        for obs in obs_pair:
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
