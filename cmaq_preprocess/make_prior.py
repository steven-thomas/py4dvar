
import os
import numpy as np

import context
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.input_defn as input_defn
import fourdvar.params.template_defn as template
from fourdvar.params.root_path_defn import store_path
from cmaq_preprocess.uncertainty import convert_unc

#parameters

# filepath to save new prior file to
#save_path = input_defn.prior_file
save_path = os.path.join( store_path, 'input/new_prior.ncf' )

# spcs used in PhysicalData
# list of spcs (eg: ['CO2','CH4','CO']) OR 'all' to use all possible spcs
spc_list = 'all'

# number of layers for PhysicalData initial condition
# int for custom layers or 'all' to use all possible layers
icon_nlay = 'all'

# number of layers for PhysicalData emissions (fluxes)
# int for custom layers or 'all' to use all possible layers
emis_nlay = 'all'

# No. days per PhysicalData timestep
# possible values:
# 'single' for using a single average across the entire model run
# integer to use custom number of days
#tday = 'single'
tday = 1

# data for emission uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
emis_unc = 1e-6 # mol/(s*m**2)

# data for inital condition uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
icon_unc = 1.0 # ppm


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

daysec = 24*60*60

efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )
xcell = float( ncf.get_attr( efile, 'XCELL' ) )
ycell = float( ncf.get_attr( efile, 'YCELL' ) )
cell_area = xcell * ycell

cat_list = ncf.get_attr( template.diurnal, 'CAT-LIST' ).strip().split()
ncat = len( cat_list )
emis_dict = {}
phys_nstep = tot_nday // tday

for spc in spc_list:
    ecat_dict = { c: [] for c in range( ncat ) }
    cat_arr = ncf.get_variable( template.diurnal, spc )[ :-1, :emis_nlay, :, : ]
    for date in dt.get_datelist():
        efile = dt.replace_date( cmaq_config.emis_file, date )
        e_arr = ncf.get_variable( efile, spc )[ :-1, :emis_nlay, :, : ] / cell_area
        for c in range( ncat ):
            data = e_arr.copy()
            data[ cat_arr!=c ] = np.nan
            ecat_dict[c].append( data )
    
    cat_arr_list = []
    for c in range( ncat ):
        data = ecat_dict[ c ]
        data = np.concatenate( data, axis=0 )
        data = np.nanmean( data.reshape((phys_nstep,-1,emis_nlay,nrow,ncol,)), axis=1 )
        cat_arr_list.append( data )
    
    emis_data = np.stack( cat_arr_list, axis=0 )
    msg = "emis_data produced invalid shape."
    assert emis_data.shape == (ncat,phys_nstep,emis_nlay,nrow,ncol), msg
    emis_dict[ spc ] = emis_data

emis_unc = convert_unc( emis_unc, emis_dict )
emis_dict.update( emis_unc )

# create icon data if needed
if input_defn.inc_icon is True:
    ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    idict = ncf.get_variable( ifile, spc_list )
    icon_dict = { k:v[0, :icon_nlay, :, :] for k,v in idict.items() }
    
    icon_unc = convert_unc( icon_unc, icon_dict )
    icon_dict.update( icon_unc )

# build data into new netCDF file
root_dim = { 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
              'TDAY': np.int32( tday ),
              'VAR-LIST': ''.join( [ '{:<16}'.format(s) for s in spc_list ] ),
              'CAT-LIST': ''.join( [ '{:<16}'.format(c) for c in cat_list ] ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

emis_dim = { 'TSTEP': None, 'LAY': emis_nlay, 'CAT': ncat }
emis_var = { k: ('f4', ('CAT','TSTEP','LAY','ROW','COL'), v)
             for k,v in emis_dict.items() }
ncf.create( parent=root, name='emis', dim=emis_dim, var=emis_var, is_root=False )

if input_defn.inc_icon is True:
    icon_dim = { 'LAY': icon_nlay }
    icon_var = { k: ('f4', ('LAY','ROW','COL'), v) for k,v in icon_dict.items() }
    ncf.create( parent=root, name='icon', dim=icon_dim, var=icon_var, is_root=False )

root.close()
print 'Prior created and save to:\n  {:}'.format( save_path )
