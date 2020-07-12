"""
make_prior.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

import cPickle as pickle
import gzip
import numpy as np
import os
import glob

import context
from cmaq_preprocess.uncertainty import convert_unc
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.input_defn as input_defn
import fourdvar.params.date_defn as date_defn
from fourdvar.params.root_path_defn import store_path
import fourdvar.util.date_handle as dt
import fourdvar.util.netcdf_handle as ncf
import pandas as pd
import datetime
import sys 
#parameters

# filepath to save new prior file to
#save_path = input_defn.prior_file
save_path = os.path.join( store_path, 'input/monthly_prior_2015.nc' )

# spcs used in PhysicalData
# list of spcs (eg: ['CO2','CH4','CO']) OR 'all' to use all possible spcs
spc_list = 'all'

# number of layers for PhysicalData emissions (fluxes)
# int for custom layers or 'all' to use all possible layers
emis_nlay = 'all'

# layer that splits bcon upper and lower regions
bcon_up_lay = 15
# total number of boundary regions (upper & lower for N,S,E,W)
bcon_regions = 8

# length of emission timestep for PhysicalData
# allowed values:
# 'emis' to use timestep from emissions file
# 'single' for using a single average across the entire model run
# 'month' to use one timestep per month
# [ sec1, sec2, ... ] for custom lengths
# int(sec) for constant repeating timestep eg: (3-hour == 3*60*60)
#tstep = 24*60*60 #daily average emissions
#tstep = 'single'
tstep = 'month'
hr = 60*60 #seconds in an hr.
#tstep = [ 6*hr, 18*hr ] #test case for variable-timestep code

# length of bcon timestep for PhysicalData (in seconds)
# allowed values:
# 'emis' to use timestep from emissions file
# 'single' for using a single average across the entire model run
# 'month' to use one timestep per month
# integer to use custom number of seconds
bcon_tstep = 24*60*60

# data for emission uncertainty
# allowed values:
# list of strings: filenames for netCDF file already correctly formatted.
#Directory where we find eigen values and its associated eigen vectors
ctmDir =  '/data/cephfs/punim0762/yvillalobos/data/CTM/AUS4/uncertainties'
sdate = datetime.datetime.strptime( str( date_defn.start_date ), '%Y%m%d' )
edate = datetime.datetime.strptime( str( date_defn.end_date ), '%Y%m%d' ) + datetime.timedelta( days=1 )
daterange = pd.date_range(start = sdate, end = edate, freq='M')
stringdates = [d.strftime("%Y-%m-%d")for d in daterange]
dates = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in stringdates]
doms = ['d01']

# data for bcon uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
#for test case use 1ppm/day CO2
bcon_unc = {'CO2':1.157e-5} #ppm/s

emis_eigen_vectors_files = []
emis_eigen_values_files = []
for date in dates:
    yyyymmdd_dashed = date.strftime('%Y-%m-%d')

    for idom, dom in enumerate(doms):
        uncdir = '{}/{}/{}'.format(ctmDir, yyyymmdd_dashed, dom)
        eigen_vectors_files = '{}/principal_components_eig_vecs_{}.pickle.zip'.format(uncdir, yyyymmdd_dashed) 
        eigen_values_files = '{}/principal_eig_vals_{}.pickle.zip'.format(uncdir, yyyymmdd_dashed )
        emis_eigen_vectors_files.append(eigen_vectors_files)
        emis_eigen_values_files.append(eigen_values_files)


#print emis_eigen_vectors_files 
#print emis_eigen_values_files

#Example of list of eigen_vectors and eigen_values
#emis_eigen_vectors_files = ['eigen_vectors_01.pic.gz','eigen_vectors_02.pic.gz']
#emis_eigen_values_files = ['eigen_values_01.pic.gz','eigen_values_02.pic.gz']

# data for ICON scaling
# list of values, one for each species
icon_scale = [1.0]
icon_unc = [0.01]


# convert spc_list into valid list
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
if input_defn.inc_icon is True:
    ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    i_var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
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

# convert tstep into valid time-step (seconds)
daysec = 24*60*60
if str( tstep ).lower() == 'emis':
    efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    hms = int( ncf.get_attr( efile, 'TSTEP' ) )
    tstep = 3600*(hms//10000) + 60*((hms//100)%100) + (hms%100)
elif str( tstep ).lower() == 'single':
    tstep = len(dt.get_datelist()) * daysec
elif str( tstep ).lower() == 'month':
    tstep = []
    for m in range(max(dt.month_index())+1):
        nday = len([ 1 for i in dt.month_index() if i==m ])
        tstep.append( nday * daysec )
#validate tstep: cleanly fits into days.
if type( tstep ) == int:
    nstep = (daysec*len(dt.get_datelist())) // tstep
    tstep = [ tstep ] * nstep
else:
    assert type( tstep ) == list, 'invalid tstep'
    assert all( [ type(i) == int for i in tstep ] ), 'invalid tstep'
tsec_list = np.cumsum( [0] + tstep )
msg = 'timestep does not fit entire model run.'
#print [ t//daysec for t in tstep ]
#print len(dt.get_datelist())
assert tsec_list[-1] == daysec*len(dt.get_datelist()), msg
ind_list = [ i for i,t in enumerate(tsec_list) if t%daysec != 0 ]
for i in ind_list:
    t = tsec_list[i]
    day_start = daysec * (t // daysec )
    day_end = day_start + daysec
    msg = 'sub-day timestep cannot span multiple days.'
    assert tsec_list[i-1] >= day_start, msg
    assert tsec_list[i+1] <= day_end, msg

# convert bcon_tstep into valid time-step (seconds)
if str( bcon_tstep ).lower() == 'emis':
    efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    hms = int( ncf.get_attr( efile, 'TSTEP' ) )
    bcon_tstep = 3600*(hms//10000) + 60*((hms//100)%100) + (hms%100)
elif str( bcon_tstep ).lower() == 'single':
    bcon_tstep = len(dt.get_datelist()) * daysec
elif str( bcon_tstep ).lower() == 'month':
    bcon_tstep = []
    for m in range(max(dt.month_index())+1):
        nday = len([ 1 for i in dt.month_index() if i==m ])
        bcon_tstep.append( nday * daysec )
#validate tstep: cleanly fits into days.
if type( bcon_tstep ) == int:
    nstep = (daysec*len(dt.get_datelist())) // bcon_tstep
    bcon_tstep = [ bcon_tstep ] * nstep
else:
    assert type( bcon_tstep ) == list, 'invalid tstep'
    assert all( [ type(i) == int for i in bcon_tstep ] ), 'invalid tstep'
bcon_tsec_list = np.cumsum( [0] + bcon_tstep )
msg = 'BCON timestep does not fit entire model run.'
assert bcon_tsec_list[-1] == daysec*len(dt.get_datelist()), msg
ind_list = [ i for i,t in enumerate(bcon_tsec_list) if t%daysec != 0 ]
for i in ind_list:
    t = bcon_tsec_list[i]
    day_start = daysec * (t // daysec )
    day_end = day_start + daysec
    msg = 'sub-day timestep cannot span multiple days.'
    assert tsec_list[i-1] >= day_start, msg
    assert tsec_list[i+1] <= day_end, msg

# emis-file timestep must fit into PhysicalData tstep
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
estep = int( ncf.get_attr( efile, 'TSTEP' ) )
esec = 3600*(estep//10000) + 60*((estep//100)%100) + (estep%100)
msg = 'emission file TSTEP & tstep incompatible'
assert all([ (t >= esec) and (t%esec == 0) for t in tstep ]), msg


#emis_nlay
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )
nstep = len( tstep )
emis_shape = ( nstep, emis_nlay, nrow, ncol, )

emis_dict = { spc: np.zeros(emis_shape) for spc in spc_list }

def load_obj( fname ):
    with gzip.GzipFile( fname, 'rb' ) as f:
        obj = pickle.load( f )
    return obj

emis_eigen_values = [ load_obj( f ) for f in emis_eigen_values_files ]
emis_eigen_vectors = [ load_obj( f ) for f in emis_eigen_vectors_files ]

msg = 'need one set of emis_eigen_vectors for each timestep.'
assert len( emis_eigen_vectors ) == nstep, msg
for i,arr in enumerate(emis_eigen_vectors):
    msg = '{:} must be 2 dimensional'.format(emis_eigen_vectors_files[i])
    assert len(arr.shape) == 2, msg
    d1,d2 = arr.shape
    if d2 > d1:
        print '{:} transposed!'.format(emis_eigen_vectors_files[i])
        emis_eigen_vectors[i] = np.transpose( arr )

cell_list, unk_list = zip( *[arr.shape for arr in emis_eigen_vectors] )

msg = 'emis_eigen_vector length is invalid.'
ncells = len( spc_list ) * np.prod( emis_shape ) / nstep
assert all([ c == ncells for c in cell_list ]), msg

msg = 'need one set of emis_eigen_values for each timestep.'
assert len( emis_eigen_values ) == nstep, msg
for i,arr in enumerate( emis_eigen_values ):
    msg = '{:} must be 1 dimensional'.format(emis_eigen_values_files[i])
    assert len(arr.shape) == 1, msg
    msg = 'emis_eigen_vectors do not match emis_eigen_values.'
    assert unk_list[i] == arr.size, msg

#convert uncertainty data into format for netCDF storage.
max_unk = max( unk_list )
vec_storage = np.zeros(( nstep, ncells, max_unk ))
val_storage = np.zeros(( nstep, max_unk ))
for i in range( nstep ):
    unk_len = unk_list[i]
    vec_storage[ i, :, :unk_len ] = emis_eigen_vectors[i][:]
    val_storage[ i, :unk_len ] = emis_eigen_values[i][:]

#create BCON values and uncertainties
bcon_nstep = len( bcon_tstep )
bcon_dict = { spc: np.zeros((bcon_nstep,bcon_regions)) for spc in spc_list }
bcon_unc = convert_unc( bcon_unc, bcon_dict )
bcon_dict.update( bcon_unc )

# build data into new netCDF file
root_dim = { 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
              'VAR-LIST': ''.join( [ '{:<16}'.format(s) for s in spc_list ] ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

if input_defn.inc_icon is True:
    icon_dim = { 'SPC': len(spc_list) }
    icon_var = { 'ICON-SCALE': ('f4', ('SPC',), np.array(icon_scale) ),
                 'ICON-UNC': ('f4', ('SPC',), np.array(icon_unc) ) }
    ncf.create( parent=root, name='icon', dim=icon_dim, var=icon_var, is_root=False )

if all([ t==tstep[0] for t in tstep ]):
    tstep_out = tstep[0]
else:
    tstep_out = [ t for t in tstep ]
emis_dim = { 'LAY': emis_nlay, 'TSTEP': None }
emis_attr = { 'TSTEP': tstep_out }
emis_var = { k: ('f4', ('TSTEP','LAY','ROW','COL'), v) for k,v in emis_dict.items() }
ncf.create( parent=root, name='emis', dim=emis_dim, attr=emis_attr,
            var=emis_var, is_root=False )

corr_unc_dim = { 'ALL_CELLS': ncells, 'UNKNOWNS':max_unk }
corr_unc_var = { 'EIGEN_VECTORS': ('f4', ('TSTEP','ALL_CELLS','UNKNOWNS',), vec_storage),
                 'EIGEN_VALUES': ('f4', ('TSTEP','UNKNOWNS',), val_storage) }
corr_unc_attr = { 'UNKNOWNS': [ np.int32( unk ) for unk in unk_list ] }
ncf.create( parent=root, name='corr_unc', attr=corr_unc_attr,
            dim=corr_unc_dim, var=corr_unc_var, is_root=False )

if all([ t==bcon_tstep[0] for t in bcon_tstep ]):
    bcon_tstep_out = bcon_tstep[0]
else:
    bcon_tstep_out = [ t for t in bcon_tstep ]
bcon_dim = { 'BCON': bcon_regions, 'TSTEP': None }
bcon_attr = { 'TSTEP': bcon_tstep_out, 'UP_LAY': np.int32( bcon_up_lay ) }
bcon_var = { k: ('f4', ('TSTEP','BCON',), v) for k,v in bcon_dict.items() }
ncf.create( parent=root, name='bcon', dim=bcon_dim, attr=bcon_attr,
            var=bcon_var, is_root=False )

root.close()
print 'Prior created and save to:\n  {:}'.format( save_path )
