
from __future__ import absolute_import

import cPickle as pickle
import gzip
import numpy as np
import os

import context
from cmaq_preprocess.uncertainty import convert_unc
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.input_defn as input_defn
from fourdvar.params.root_path_defn import store_path
import fourdvar.util.date_handle as dt
import fourdvar.util.netcdf_handle as ncf

#parameters

# filepath to save new prior file to
#save_path = input_defn.prior_file
save_path = os.path.join( store_path, 'input/prior_timevar.nc' )

# spcs used in PhysicalData
# list of spcs (eg: ['CO2','CH4','CO']) OR 'all' to use all possible spcs
spc_list = 'all'

# number of layers for PhysicalData emissions (fluxes)
# int for custom layers or 'all' to use all possible layers
emis_nlay = 'all'

# length of emission timestep for PhysicalData
# allowed values:
# 'emis' to use timestep from emissions file
# 'single' for using a single average across the entire model run
# 'month' to use one timestep per month
# [ sec1, sec2, ... ] for custom lengths
# int(sec) for constant repeating timestep eg: (3-hour == 3*60*60)
#tstep = 24*60*60 #daily average emissions
#tstep = 'single'
# tstep = 'month'
hr = 60*60 #seconds in an hr.
tstep = [ 48*hr, 12*hr, 12*hr, 24*hr ] #test case for variable-timestep code

# data for emission uncertainty
# allowed values:
# string: filename for netCDF file already correctly formatted.
emis_unc_vector = 'tmp_unc_vector.pic.gz'
emis_corr_matrix = 'tmp_corr_matrix.pic.gz'

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
    for m in range(max(dt.month_index())):
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
assert tsec_list[-1] == daysec*len(dt.get_datelist()), msg
ind_list = [ i for i,t in enumerate(tsec_list) if t%daysec != 0 ]
for i in ind_list:
    t = tsec_list[i]
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

emis_unc_vector = load_obj( emis_unc_vector )
emis_corr_matrix = load_obj( emis_corr_matrix )

assert len( emis_corr_matrix.shape ) == 2, 'emis_corr_matrix must be 2-dimensional'
d1,d2 = emis_corr_matrix.shape
if d2 > d1:
    emis_corr_matrix = np.transpose( emis_corr_matrix )

all_cells, unknowns = emis_corr_matrix.shape

msg = 'emis_corr_matrix long dimension is invalid.'
assert all_cells == len(spc_list) * np.prod( emis_shape ), msg

assert len( emis_unc_vector.shape ) == 1, 'emis_unc_vector must be 1-dimensional'
msg = 'emis_corr_matrix short dimension does not match emis_unc_vector.'
assert unknowns == emis_unc_vector.shape[0], msg


# build data into new netCDF file
if all([ t==tstep[0] for t in tstep ]):
    tstep_out = tstep[0]
else:
    tstep_out = [ t for t in tstep ]
root_dim = { 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
              'TSTEP': tstep_out,
              'VAR-LIST': ''.join( [ '{:<16}'.format(s) for s in spc_list ] ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

if input_defn.inc_icon is True:
    icon_dim = { 'SPC': len(spc_list) }
    icon_var = { 'ICON-SCALE': ('f4', ('SPC',), np.array(icon_scale) ),
                 'ICON-UNC': ('f4', ('SPC',), np.array(icon_unc) ) }
    ncf.create( parent=root, name='icon', dim=icon_dim, var=icon_var, is_root=False )

emis_dim = { 'TSTEP': None, 'LAY': emis_nlay }
emis_var = { k: ('f4', ('TSTEP','LAY','ROW','COL'), v) for k,v in emis_dict.items() }
ncf.create( parent=root, name='emis', dim=emis_dim, var=emis_var, is_root=False )

corr_unc_dim = { 'ALL_CELLS': all_cells, 'UNKNOWNS':unknowns }
corr_unc_var = { 'corr_matrix': ('f4', ('ALL_CELLS','UNKNOWNS',), emis_corr_matrix),
                 'unc_vector': ('f4', ('UNKNOWNS',), emis_unc_vector) }
ncf.create( parent=root, name='corr_unc', dim=corr_unc_dim, var=corr_unc_var, is_root=False )

root.close()
ncf.copy_compress( save_path, save_path )
print 'Prior created and save to:\n  {:}'.format( save_path )
