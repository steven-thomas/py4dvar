"""
make_prior.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
import numpy as np

import context
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt
import fourdvar.util.file_handle as fh
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.input_defn as input_defn
from fourdvar.params.root_path_defn import store_path
from cmaq_preprocess.uncertainty import convert_unc

#parameters

# filepath to save new prior file to
save_path = input_defn.prior_file
#save_path = os.path.join( store_path, 'input/new_prior.nc' )
fh.ensure_path( os.path.dirname( save_path ) )

# spcs used in PhysicalData
# list of spcs (eg: ['CO2','CH4','CO']) OR 'all' to use all possible spcs
spc_list = ['CO']

# number of layers for PhysicalData emissions (fluxes)
# int for custom layers or 'all' to use all possible layers
emis_nlay = 1

# layer that splits upper and lower boundary regions
bcon_up_lay = 15
# total number of boundary regions
bcon_regions = 8

# No. days per PhysicalData diurnal timestep
# possible values:
# 'single' for using a single average across the entire model run
# integer to use custom number of days
tday = 'single'

# length of bcon timestep for PhysicalData (in seconds)
# allowed values:
# 'emis' to use timestep from emissions file
# 'single' for using a single average across the entire model run
# integer to use custom number of seconds
bcon_tsec = 'single'

# data for emission uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
#emis_unc = 1e-8 # mol/(s*m**2)
emis_unc = 0.01 # unitless emissions multiplier

# data for ICON scaling
# list of values, one for each species
icon_scale = [1.0]
icon_unc = [0.01]

# data for bcon uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
#for test case using 50ppb/day CO
bcon_unc = {'CO':5.787e-7} #ppm/s


# convert spc_list into valid list
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
if input_defn.inc_icon is True:
    ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    i_var_list = ncf.get_attr( ifile, 'VAR-LIST' ).split()
    var_list = list( set(var_list).intersection( set( i_var_list ) ) )
if str(spc_list).lower() == 'all':
    spc_list = [ v for v in var_list ]
else:
    try:
        assert set( spc_list ).issubset( set(var_list) )
        spc_list = [ s for s in spc_list ]
    except AssertionError:
        print 'spc_list must be a subset of cmaq spcs'
        raise
    except:
        print 'invalid spc_list'
        raise

# check that icon_scale & icon_unc are valid
if input_defn.inc_icon is True:
    assert len(spc_list)==len(icon_scale), 'Invalid icon_scale size'
    assert len(spc_list)==len(icon_unc), 'Invalid icon_unc size'

# convert emis_nlay into valid number
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
enlay = int( ncf.get_attr( efile, 'NLAYS' ) )
if str(emis_nlay).lower() == 'all':
    emis_nlay = enlay
else:
    try:
        assert int( emis_nlay ) == emis_nlay
        emis_nlay = int( emis_nlay )
    except:
        print 'invalid emis_nlay'
        raise
    if emis_nlay > enlay:
        raise AssertionError('emis_nlay must be <= {:}'.format( enlay ))

# convert tday into valid number of days
if str( tday ).lower() == 'single':
    tday = len( dt.get_datelist() )
else:
    try:
        assert int( tday ) == tday
        tday = int( tday )
    except:
        print 'invalid tday'
        raise
tot_nday = len( dt.get_datelist() )
assert tday <= tot_nday, 'tday must be <= No. days in model run'
assert tot_nday % tday == 0, 'tday must cleanly divide No. days in model run'

# convert bcon_tsec into valid time-step length
daysec = 24*60*60
if str( bcon_tsec ).lower() == 'emis':
    efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    hms = int( ncf.get_attr( efile, 'TSTEP' ) )
    bcon_tsec = 3600*(hms//10000) + 60*((hms//100)%100) + (hms%100)
elif str( bcon_tsec ).lower() == 'single':
    nday = len( dt.get_datelist() )
    bcon_tsec = nday * daysec
else:
    bcon_tsec = int( bcon_tsec )
    if bcon_tsec >= daysec:
        assert bcon_tsec % daysec == 0, 'invalid bcon_tsec'
        assert len( dt.get_datelist() ) % (bcon_tsec // daysec) == 0, 'invalid bcon_tsec'
    else:
        assert daysec % bcon_tsec == 0, 'invalid bcon_tsec'

# emis-file timestep must fit into PhysicalData tstep
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
estep = int( ncf.get_attr( efile, 'TSTEP' ) )
esec = 3600*(estep//10000) + 60*((estep//100)%100) + (estep%100)
msg = 'emission file TSTEP & bcon_tstep incompatible'
assert (bcon_tsec >= esec) and (bcon_tsec%esec == 0), msg

emis_nstep = tot_nday // tday
bcon_nstep = len(dt.get_datelist())*daysec // bcon_tsec

# convert emis-file data into needed PhysicalData format
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )
xcell = float( ncf.get_attr( efile, 'XCELL' ) )
ycell = float( ncf.get_attr( efile, 'YCELL' ) )
cell_area = xcell * ycell

# emis is scaling term, use to multiply a pre-defined daily pattern of emission values.
# set prior value to 1. (no change from template).
emis_dict = {}
for spc in spc_list:
    emis_data = np.ones((emis_nstep,emis_nlay,nrow,ncol,))
    emis_dict[ spc ] = emis_data

emis_unc = convert_unc( emis_unc, emis_dict )
emis_dict.update( emis_unc )

bcon_dict = { spc: np.zeros((bcon_nstep,bcon_regions)) for spc in spc_list }
bcon_unc = convert_unc( bcon_unc, bcon_dict )
bcon_dict.update( bcon_unc )    

# build data into new netCDF file
root_dim = { 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
              #'TSTEP': [ np.int32( tstep[0] ), np.int32( tstep[1] ) ],
              'VAR-LIST': ''.join( [ '{:<16}'.format(s) for s in spc_list ] ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

emis_dim = { 'TSTEP': None, 'LAY': emis_nlay }
emis_attr = { 'TDAY': tday }
emis_var = { k: ('f4', ('TSTEP','LAY','ROW','COL'), v) for k,v in emis_dict.items() }
ncf.create( parent=root, name='emis', dim=emis_dim, attr=emis_attr, var=emis_var, is_root=False )

if input_defn.inc_icon is True:
    icon_dim = { 'SPC': len(spc_list) }
    icon_var = { 'ICON-SCALE': ('f4', ('SPC',), np.array(icon_scale) ),
                 'ICON-UNC': ('f4', ('SPC',), np.array(icon_unc) ) }
    ncf.create( parent=root, name='icon', dim=icon_dim, var=icon_var, is_root=False )

bcon_dim = { 'TSTEP': None, 'BCON': bcon_regions }
bcon_attr = { 'TSEC': bcon_tsec,
              'UP_LAY': np.int32(bcon_up_lay) }
bcon_var = { k: ('f4', ('TSTEP','BCON',), v) for k,v in bcon_dict.items() }
ncf.create( parent=root, name='bcon', dim=bcon_dim, attr=bcon_attr, var=bcon_var, is_root=False )

root.close()
print 'Prior created and save to:\n  {:}'.format( save_path )
