
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
#save_path = input_defn.prior_file
save_path = os.path.join( store_path, 'input/new_prior.ncf' )
fh.ensure_path( os.path.dirname( save_path ) )

# spcs used in PhysicalData proportional output
# list of spcs (eg: ['CO2','CH4','CO'])
spc_out_list = ['CO']
# spcs used in PhysicalData proportional input
# list of spcs (eg: ['CO2','CH4','CO']) (same length as spcs_out_list)
spc_in_list = ['CO2']

if input_defn.inc_icon is True:
    spc_icon_list = ['CO','CO2']

# default proportional fraction value
# list of floats (same length as spcs_out_list)
prop_val = [ 0.05 ]

# number of layers for PhysicalData initial condition
# int for custom layers or 'all' to use all possible layers
icon_nlay = 'all'

# number of layers for PhysicalData emissions (fluxes)
# int for custom layers or 'all' to use all possible layers
emis_nlay = 'all'

# length of emission timestep for PhysicalData (in seconds)
# allowed values:
# 'emis' to use timestep from emissions file
# 'single' for using a single average across the entire model run
# integer to use custom number of seconds
tsec = 24*60*60

# data for emission uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
emis_unc = 1e-3 # unitless proportion

# data for inital condition uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
icon_unc = 1.0 # ppm


# check spc_out & spc_in are valid
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
msg = 'spc_out_list and spc_in_list must be disjoint'
assert set( spc_out_list ).isdisjoint( set( spc_in_list ) ), msg
assert set( spc_out_list ).issubset( set(var_list) ), 'spc_out must all be in emis file'
assert set( spc_in_list ).issubset( set(var_list) ), 'spc_in must all be in emis file'
# convert spc_icon_list to valid list
if input_defn.inc_icon is True:
    ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
    if str(spc_icon_list).lower() == 'all':
        spc_icon_list = [ v for v in var_list ]
    assert set( spc_icon_list ).issubset( set(var_list) )
    spc_icon_list = [ s for s in spc_icon_list ]

# convert icon_nlay into valid number (only if we need icon)
if input_defn.inc_icon is True:
    ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    inlay = int( ncf.get_attr( ifile, 'NLAYS' ) )
    if str(icon_nlay).lower() == 'all':
        icon_nlay = inlay
    else:
        try:
            assert int( icon_nlay ) == icon_nlay
            icon_nlay = int( icon_nlay )
        except:
            print 'invalid icon_nlay'
            raise
        if icon_nlay > inlay:
            raise AssertionError('icon_nlay must be <= {:}'.format( inlay ))

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

# convert tsec into valid time-step length
daysec = 24*60*60
if str( tsec ).lower() == 'emis':
    efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    hms = int( ncf.get_attr( efile, 'TSTEP' ) )
    tsec = 3600*(hms//10000) + 60*((hms//100)%100) + (hms%100)
elif str( tsec ).lower() == 'single':
    nday = len( dt.get_datelist() )
    tsec = nday * daysec
else:
    tsec = int( tsec )
    if tsec >= daysec:
        assert tsec % daysec == 0, 'invalid tsec'
        assert len( dt.get_datelist() ) % (tsec // daysec) == 0, 'invalid tsec'
    else:
        assert daysec % tsec == 0, 'invalid tsec'

# emis-file timestep must fit into PhysicalData tstep
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
estep = int( ncf.get_attr( efile, 'TSTEP' ) )
esec = 3600*(estep//10000) + 60*((estep//100)%100) + (estep%100)
msg = 'emission file TSTEP & tstep incompatible'
assert (tsec >= esec) and (tsec%esec == 0), msg

nstep = len(dt.get_datelist())*daysec // tsec

# convert emis-file data into needed PhysicalData format
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )

arr = np.zeros( (nstep,emis_nlay,nrow,ncol) )
emis_dict = { spc: arr + prop_val[i] for i,spc in enumerate(spc_out_list) }

emis_unc = convert_unc( emis_unc, emis_dict )
emis_dict.update( emis_unc )

# create icon data if needed
if input_defn.inc_icon is True:
    ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    idict = ncf.get_variable( ifile, spc_icon_list )
    icon_dict = { k:v[0, :icon_nlay, :, :] for k,v in idict.items() }
    
    icon_unc = convert_unc( icon_unc, icon_dict )
    icon_dict.update( icon_unc )
    

# build data into new netCDF file
root_dim = { 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
              'TSEC': np.int32( tsec ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

emis_dim = { 'TSTEP': None, 'LAY': emis_nlay }
spc_out_txt = ''.join( [ '{:<16}'.format(s) for s in spc_out_list ] )
spc_in_txt = ''.join( [ '{:<16}'.format(s) for s in spc_in_list ] )
emis_attr = { 'SPC_OUT': spc_out_txt, 'SPC_IN': spc_in_txt }
emis_var = { k: ('f4', ('TSTEP','LAY','ROW','COL'), v) for k,v in emis_dict.items() }
ncf.create( parent=root, name='emis', dim=emis_dim, attr=emis_attr, var=emis_var, is_root=False )

if input_defn.inc_icon is True:
    icon_dim = { 'LAY': icon_nlay }
    icon_attr = {'SPC': ''.join( [ '{:<16}'.format(s) for s in spc_icon_list ] ) }
    icon_var = { k: ('f4', ('LAY','ROW','COL'), v) for k,v in icon_dict.items() }
    ncf.create( parent=root, name='icon', dim=icon_dim, attr=icon_attr, var=icon_var, is_root=False )

root.close()
print 'Prior created and save to:\n  {:}'.format( save_path )
