
import os
import numpy as np
import gzip
import cPickle as pickle

import _get_root
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.input_defn as input_defn
from fourdvar.params.root_path_defn import store_path
from cmaq_preprocess.uncertainty import convert_unc

#parameters

# filepath to save new prior file to
#save_path = input_defn.prior_file
save_path = os.path.join( store_path, 'input/prior.ncf' )

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
# [ days, HoursMinutesSeconds ] for custom length eg: (half-hour = [0,3000])
#tstep = [1,0] #daily average emissions
tstep = 'single'

# data for emission uncertainty
# allowed values:
# string: filename for netCDF file already correctly formatted.
emis_unc_vector = 'tmp_unc_vector.pickle.zip'
emis_corr_matrix = 'tmp_corr_matrix.pickle.zip'


assert input_defn.inc_icon is False, 'make_prior not configured for ICON optimization.'

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

# convert tstep into valid time-step
if str( tstep ).lower() == 'emis':
    efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    estep = int( ncf.get_attr( efile, 'TSTEP' ) )
    day = 0
    hms = estep
elif str( tstep ).lower() == 'single':
    nday = len( dt.get_datelist() )
    day = nday
    hms = 0
else:
    try:
        assert len( tstep ) == 2
        day,hms = tstep
        assert int(day) == day
        day = int(day)
        assert int(hms) == hms
        hms = int(hms)
    except:
        print 'invalid tstep'
        raise
tstep = [ day, hms ]

daysec = 24*60*60
tsec = daysec*day + 3600*(hms//10000) + 60*((hms//100)%100) + (hms%100)

# emis-file timestep must fit into PhysicalData tstep
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
estep = int( ncf.get_attr( efile, 'TSTEP' ) )
esec = 3600*(estep//10000) + 60*((estep//100)%100) + (estep%100)
msg = 'emission file TSTEP & tstep incompatible'
assert (tsec >= esec) and (tsec%esec == 0), msg

# PhysicalData tstep must fit into model days
assert max(tsec,daysec) % min(tsec,daysec) == 0, 'tstep must fit into days'
assert len(dt.get_datelist())*daysec % tsec == 0, 'tstep must fit into model length'



#emis_nlay
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )
nstep = len(dt.get_datelist())*daysec // tsec
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
root_dim = { 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
              'TSTEP': [ np.int32( tstep[0] ), np.int32( tstep[1] ) ],
              'VAR-LIST': ''.join( [ '{:<16}'.format(s) for s in spc_list ] ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

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
