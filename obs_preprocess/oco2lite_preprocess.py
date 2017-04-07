#!/apps/python/2.7.6/bin/python2.7

import os
import glob
import cPickle as pickle

from obsOCO2_defn import ObsOCO2
from model_space import ModelSpace
from netCDF4 import Dataset

#-CONFIG-SETTINGS---------------------------------------------------------

#'filelist': source = list of OCO2-Lite files
#'directory': source = directory, use all files in source
#'pattern': source = file_pattern_string, use all files that match pattern
source_type = 'directory'

#source = [ 'mok_oco2_data.nc4' ]
source = 'oco2_sample'

output_file = 'obs_oco2_example.pickle'

METCRO3D = 'METCRO3D'
METCRO2D = 'METCRO2D'
CONC = 'conc.ncf'

#--------------------------------------------------------------------------

model_grid = ModelSpace( METCRO3D, METCRO2D, CONC )

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

root_var = [ 'latitude',
             'longitude',
             'time',
             'solar_zenith_angle',
             'sensor_zenith_angle',
             'xco2',
             'xco2_uncertainty',
             'pressure_levels',
             'xco2_averaging_kernel' ]
sounding_var = [ 'solar_azimuth_angle', 'sensor_azimuth_angle' ]
obslist = []
for fname in filelist:
    print 'read {}'.format( fname )
    var_dict = {}
    with Dataset( fname, 'r' ) as f:
        size = f.dimensions[ 'sounding_id' ].size
        for var in root_var:
            var_dict[ var ] = f.variables[ var ][:]
        for var in sounding_var:
            var_dict[ var ] = f.groups[ 'Sounding' ].variables[ var ][:]
    print 'found {} soundings'.format( size )
    for i in range( size ):
        src_dict = { k: v[i] for k,v in var_dict.items() }
        obs = ObsOCO2.create( **src_dict )
        obs.model_process( model_grid )
        obsdict = obs.get_obsdict()
        if obsdict[ 'valid' ] is True:
            obslist.append( obsdict )
        else:
            print 'Sounding No. {} rejected.'.format( i )

if len( obslist ) > 0:
    gridmeta = model_grid.get_gridmeta()
    with open( output_file, 'w' ) as f:
        pickle.dump( gridmeta, f )
        pickle.dump( obslist, f )
    print 'recorded observations to {}'.format( output_file )
else:
    print 'No valid observations found, no output file generated.'
