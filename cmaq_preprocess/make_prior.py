
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

# spcs used in PhysicalData diurnal output
# list of spcs (eg: ['CO2','CH4','CO'])
emis_spc_out = ['CO2']
# spcs used in PhysicalData proportional output
# list of spcs (eg: ['CO2','CH4','CO'])
prop_spc_out = ['CO']
# spcs used in PhysicalData proportional input
# list of spcs (eg: ['CO2','CH4','CO']) (same length as spcs_out_list)
prop_spc_in = ['CO2']

if input_defn.inc_icon is True:
    raise ValueError('setup not enabled for ICON solving.')
    #spc_icon_list = ['CO','CO2']

# default proportional fraction value
# list of floats (same length as spcs_out_list)
prop_val = [ 0.05 ]

# number of layers for PhysicalData initial condition
# int for custom layers or 'all' to use all possible layers
#icon_nlay = 'all'

# number of layers for PhysicalData emissions (fluxes)
# int for custom layers or 'all' to use all possible layers
emis_nlay = 'all'

# length of proportial emission timestep for PhysicalData (in seconds)
# allowed values:
# 'emis' to use timestep from emissions file
# 'single' for using a single average across the entire model run
# integer to use custom number of seconds
tsec = 24*60*60

# No. days per PhysicalData diurnal timestep
# possible values:
# 'single' for using a single average across the entire model run
# integer to use custom number of days
#tday = 'single'
tday = 1

# data for proportial emission uncertainty
# allowed values:
# single number: apply value to every uncertainty
# dict: apply single value to each spcs ( eg: { 'CO2':1e-6, 'CO':1e-7 } )
# string: filename for netCDF file already correctly formatted.
prop_unc = 1e-3 # unitless proportion

# data for diurnal emission uncertainty
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
#icon_unc = 1.0 # ppm


# check spc_out & spc_in are valid
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
msg = 'spc_out_list and spc_in_list must be disjoint'
assert set( prop_spc_out ).isdisjoint( set( prop_spc_in ) ), msg
assert set( prop_spc_out ).issubset( set(var_list) ), 'prop_spc_out must all be in emis file'
assert set( prop_spc_in ).issubset( set(var_list) ), 'propspc_in must all be in emis file'
assert set( emis_spc_out ).issubset( set(var_list) ), 'emis_spc_out must all be in emis file'
assert set(emis_spc_out).isdisjoint( set(prop_spc_out) ), 'emis/prop spc clash.'
# convert spc_icon_list to valid list
if input_defn.inc_icon is True:
    raise ValueError('setup not enabled for ICON solving.')
    #ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    #var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
    #if str(spc_icon_list).lower() == 'all':
    #    spc_icon_list = [ v for v in var_list ]
    #assert set( spc_icon_list ).issubset( set(var_list) )
    #spc_icon_list = [ s for s in spc_icon_list ]

# convert icon_nlay into valid number (only if we need icon)
if input_defn.inc_icon is True:
    raise ValueError('setup not enabled for ICON solving.')
    #ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    #inlay = int( ncf.get_attr( ifile, 'NLAYS' ) )
    #if str(icon_nlay).lower() == 'all':
    #    icon_nlay = inlay
    #else:
    #    try:
    #        assert int( icon_nlay ) == icon_nlay
    #        icon_nlay = int( icon_nlay )
    #    except:
    #        print 'invalid icon_nlay'
    #        raise
    #    if icon_nlay > inlay:
    #        raise AssertionError('icon_nlay must be <= {:}'.format( inlay ))

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

# emis-file timestep must fit into PhysicalData tstep
efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
estep = int( ncf.get_attr( efile, 'TSTEP' ) )
esec = 3600*(estep//10000) + 60*((estep//100)%100) + (estep%100)
msg = 'emission file TSTEP & tstep incompatible'
assert (tsec >= esec) and (tsec%esec == 0), msg

prop_nstep = len(dt.get_datelist())*daysec // tsec
emis_nstep = tot_nday // tday

# convert emis-file data into needed PhysicalData format
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )
xcell = float( ncf.get_attr( efile, 'XCELL' ) )
ycell = float( ncf.get_attr( efile, 'YCELL' ) )
cell_area = xcell * ycell

cat_list = ncf.get_attr( template.diurnal, 'CAT-LIST' ).strip().split()
ncat = len( cat_list )

prop_arr = np.zeros( (prop_nstep,emis_nlay,nrow,ncol) )
prop_dict = { spc: prop_arr + prop_val[i] for i,spc in enumerate(prop_spc_out) }
prop_unc = convert_unc( prop_unc, prop_dict )
prop_dict.update( prop_unc )

emis_dict = {}
for spc in emis_spc_out:
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
        data = np.nanmean( data.reshape((emis_nstep,-1,emis_nlay,nrow,ncol,)), axis=1 )
        cat_arr_list.append( data )
    
    emis_data = np.stack( cat_arr_list, axis=0 )
    msg = "emis_data produced invalid shape."
    assert emis_data.shape == (ncat,emis_nstep,emis_nlay,nrow,ncol), msg
    emis_dict[ spc ] = emis_data

emis_unc = convert_unc( emis_unc, emis_dict )
emis_dict.update( emis_unc )

# create icon data if needed
if input_defn.inc_icon is True:
    raise ValueError('setup not enabled for ICON solving.')
    #ifile = dt.replace_date( cmaq_config.icon_file, dt.start_date )
    #idict = ncf.get_variable( ifile, spc_icon_list )
    #icon_dict = { k:v[0, :icon_nlay, :, :] for k,v in idict.items() }
    #icon_unc = convert_unc( icon_unc, icon_dict )
    #icon_dict.update( icon_unc )
    

# build data into new netCDF file
root_dim = { 'LAY': emis_nlay, 'ROW': nrow, 'COL': ncol }
root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
              'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ) }

root = ncf.create( path=save_path, attr=root_attr, dim=root_dim, is_root=True )

prop_dim = { 'TSTEP': None }
prop_attr = { 'TSEC': tsec,
              'OUT_SPC': ''.join( [ '{:<16}'.format(s) for s in prop_spc_out ] ),
              'IN_SPC': ''.join( [ '{:<16}'.format(s) for s in prop_spc_in ] ) }
prop_var = { k: ('f4', ('TSTEP','LAY','ROW','COL',), v) for k,v in prop_dict.items() }
ncf.create( parent=root, name='prop', dim=prop_dim, attr=prop_attr, var=prop_var, is_root=False )

emis_dim = { 'TSTEP': None, 'CAT': ncat }
emis_attr = { 'TDAY': tday,
              'OUT_SPC': ''.join( [ '{:<16}'.format(s) for s in emis_spc_out ] ),
              'CAT_NAME':  ''.join( [ '{:<16}'.format(s) for s in cat_list ] ) }
emis_var = { k: ('f4', ('CAT','TSTEP','LAY','ROW','COL'), v)
             for k,v in emis_dict.items() }
ncf.create( parent=root, name='emis', dim=emis_dim, attr=emis_attr, var=emis_var, is_root=False )

if input_defn.inc_icon is True:
    raise ValueError('setup not enabled for ICON solving.')
    #icon_dim = { 'LAY': icon_nlay }
    #icon_attr = {'SPC': ''.join( [ '{:<16}'.format(s) for s in spc_icon_list ] ) }
    #icon_var = { k: ('f4', ('LAY','ROW','COL'), v) for k,v in icon_dict.items() }
    #ncf.create( parent=root, name='icon', dim=icon_dim, attr=icon_attr, var=icon_var, is_root=False )

root.close()
print 'Prior created and save to:\n  {:}'.format( save_path )
