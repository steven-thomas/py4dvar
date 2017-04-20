#!/apps/python/2.7.6/bin/python2.7

import os
import shutil
import numpy as np

import _get_root
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt
import fourdvar.util.cmaq_handle as cmaq_handle
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.template_defn as template
import cmaq_preprocess.setup_config as setup_config
import cmaq_preprocess.uncertainty as uncertainty

#check emission start time & timestep
if setup_config.match_emis_stime is True:
    cmaq_stime = ''.join( [ '{:02d}'.format(i) for i in cmaq_config.sttime ] )
    for date in dt.get_datelist():
        efile = dt.replace_date( cmaq_config.emis_file, date )
        emis_stime = int( ncf.get_attr( efile, 'STIME' ) )
        emis_stime = '{:06d}'.format( emis_stime )
        msg = 'cmaq_config.sttime & {}.STIME are incompatible'.format( efile )
        assert cmaq_stime == emis_stime, msg

if setup_config.match_emis_tstep is True:
    cmaq_tstep = ''.join( [ '{:02d}'.format(i) for i in cmaq_config.tstep ] )
    for date in dt.get_datelist():
        efile = dt.replace_date( cmaq_config.emis_file, date )
        emis_tstep = int( ncf.get_attr( efile, 'TSTEP' ) )
        emis_tstep = '{:06d}'.format( emis_tstep )
        msg = 'cmaq_config.tstep & {}.TSTEP are incompatible'.format( efile )
        assert cmaq_tstep == emis_tstep, msg


#construct a PhysicalData prior
if setup_config.create_prior is True:

    #phys_spcs = 'icon' OR 'emis' OR ['x','y']
    if str( setup_config.phys_spcs ).lower() == 'icon':
        var_list = ncf.get_attr( cmaq_config.icon_file, 'VAR-LIST' ).split()
    elif str( setup_config.phys_spcs ).lower() == 'emis':
        efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
        var_list = ncf.get_attr( efile, 'VAR-LIST' ).split()
    else:
        var_list = [ spc for spc in setup_config.phys_spcs ]
    
    #phys_icon_lays = 'icon' OR int
    if str( setup_config.phys_icon_lays ).lower() == 'icon':
        icon_lays = int( ncf.get_attr( cmaq_config.icon_file, 'NLAYS' ) )
    else:
        icon_lays = int( setup_config.phys_icon_lays )
    
    #phys_emis_lays = 'emis' OR int
    if str( setup_config.phys_emis_lays ).lower() == 'emis':
        efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
        emis_lays = int( ncf.get_attr( efile, 'NLAYS' ) )
    else:
        emis_lays = int( setup_config.phys_emis_lays )
    
    #phys_tstep = 'emis' OR [day,hour,minute,second]
    if str( setup_config.phys_tstep ).lower() == 'emis':
        efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
        hms_int = int( ncf.get_attr( efile, 'TSTEP' ) )
        tstep = [ 0, hms_int ]
    else:
        tstep = [ setup_config.phys_tstep[0], setup_config.phys_tstep[1] ]
    
    #handle icon:
    icon_attr_dict = ncf.get_all_attr( cmaq_config.icon_file )
    root_dim = { 'ROW' : icon_attr_dict[ 'NROWS' ],
                 'COL' : icon_attr_dict[ 'NCOLS' ] }
    icon_var_dict = {}
    for spc,val in ncf.get_variable( cmaq_config.icon_file, var_list ).items():
        t,l,r,c = val.shape
        assert t == 1, 'icon file must have dimension TSTEP size == 1'
        assert l >= icon_lays, 'phys_icon_lays too large'
        assert r == root_dim['ROW'], 'all data must have same No. rows'
        assert c == root_dim['COL'], 'all data must have same No. cols'
        icon_var_dict[ spc ] = val[ 0, :icon_lays, :, : ].copy()
    #inital conditions have no timestep
    del icon_attr_dict[ 'TSTEP' ]
    icon_attr_dict[ 'NLAYS' ] = icon_lays
    #change VGLVLS?
    
    icon_unc_dict = {}
    for spc,val in uncertainty.icon_unc( icon_var_dict, icon_attr_dict ).items():
        assert val.shape == icon_var_dict[ spc ].shape, 'unc & data must match'
        assert (val > 0).all(), 'uncertainties must be greater than 0.'
        icon_unc_dict[ spc + '_UNC' ] = val.copy()
    msg = 'some spcs are mission uncertainties'
    assert len(icon_unc_dict.keys())==len(icon_var_dict.keys()), msg
    icon_var_dict.update( icon_unc_dict )
    
    #handle emis:
    daysec = 24*60*60
    efile = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    emis_attr_dict = ncf.get_all_attr( efile )
    
    estep = emis_attr_dict[ 'TSTEP' ]
    esec = 3600*(estep//10000) + 60*((estep//100)%100) + (estep%100)
    day,hms = tstep
    tsec = daysec*day + 3600*(hms//10000) + 60*((hms//100)%100) + (hms%100)
    assert max(tsec,daysec) % min(tsec,daysec) == 0, 'invalid phys_tstep'
    assert daysec % esec == 0, 'invalid emission file TSTEP'
    msg = 'emission file TSTEP & phys_tstep incompatible'
    assert (tsec >= esec) and (tsec%esec == 0), msg
    
    assert emis_lays <= int( emis_attr_dict[ 'NLAYS' ] ), 'invalid phys_emis_lays'
    eshape = ( 0, emis_lays, emis_attr_dict['NROWS'], emis_attr_dict['NCOLS'], )
    full_emis_dict = { spc: np.zeros(eshape) for spc in var_list }
    cell_area = int( emis_attr_dict[ 'XCELL' ] ) * int( emis_attr_dict[ 'YCELL' ] )
    for date in dt.get_datelist():
        efile = dt.replace_date( cmaq_config.emis_file, date )
        edict = ncf.get_variable( efile, var_list )
        for spc in full_emis_dict.keys():
            to_add = edict[ spc ][ :-1, :emis_lays, :, : ] / cell_area
            new_arr = np.append( full_emis_dict[ spc ], to_add, axis=0 )
            full_emis_dict[ spc ] = new_arr
    fac = tsec // esec
    avg = lambda arr: np.array([ arr[i::fac,...] for i in range(fac) ]).mean(axis=0)
    emis_var_dict = { spc: avg( full_emis_dict[ spc ] ) for spc in var_list }
    emis_attr_dict[ 'TSTEP' ] = tstep
    emis_attr_dict[ 'NLAYS' ] = emis_lays
    #change VGLVLS?

    emis_unc_dict = {}
    for spc,val in uncertainty.emis_unc( emis_var_dict, emis_attr_dict ).items():
        assert val.shape == emis_var_dict[ spc ].shape, 'unc & data must match'
        assert (val > 0).all(), 'uncertainties must be greater than 0.'
        emis_unc_dict[ spc + '_UNC' ] = val.copy()
    msg = 'some spcs are mission uncertainties'
    assert len(emis_unc_dict.keys())==len(emis_var_dict.keys()), msg
    emis_var_dict.update( emis_unc_dict )
    
    root_attr = { 'SDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.start_date ) ),
                  'EDATE': np.int32( dt.replace_date( '<YYYYDDD>', dt.end_date ) ),
                  'TSTEP': [ np.int32(tstep[0]), np.int32(tstep[1]) ],
                  'VAR-LIST': ''.join( [ '{:<16}'.format(v) for v in var_list ] ) }
    icon_dim = { 'LAY': icon_lays }
    emis_dim = { 'TSTEP': None, 'LAY': emis_lays }
    
    icon_var = { k: ('f4', ('LAY','ROW','COL'), v)
                 for k,v in icon_var_dict.items() }
    emis_var = { k: ('f4', ('TSTEP','LAY','ROW','COL'), v)
                 for k,v in emis_var_dict.items() }
    
    root = ncf.create( path=setup_config.phys_path,
                       attr=root_attr, dim=root_dim, is_root=True )
    ncf.create( parent=root, name='icon',
                dim=icon_dim, var=icon_var, is_root=False )
    ncf.create( parent=root, name='emis',
                dim=emis_dim, var=emis_var, is_root=False )
    root.close()


#create a new set of template files for CMAQ-fourdvar interface
if setup_config.create_templates is True:
    # get all cmaq source files for start_date
    emis_file = dt.replace_date( cmaq_config.emis_file, dt.start_date )
    icon_file = cmaq_config.icon_file
    conc_file = dt.replace_date( cmaq_config.conc_file, dt.start_date )
    force_file = dt.replace_date( cmaq_config.force_file, dt.start_date )
    sense_conc_file = dt.replace_date( cmaq_config.conc_sense_file, dt.start_date )
    sense_emis_file = dt.replace_date( cmaq_config.emis_sense_file, dt.start_date )
    
    # set emis_lays
    if str( setup_config.emis_lays ).lower() == 'all':
        emis_lays = int( ncf.get_attr( emis_file, 'NLAYS' ) )
    else:
        emis_lays = int( setup_config.emis_lays )
    if str( cmaq_config.emis_lays ).lower() == 'template':
        cmaq_config.emis_lays = str( emis_lays )
    
    # set conc_out_lays
    if str( setup_config.conc_out_lays ).lower() == 'icon':
        conc_lay = int( ncf.get_attr( icon_file, 'NLAYS' ) )
    elif str( setup_config.conc_out_lays ).lower() == 'emis':
        conc_lay = int( ncf.get_attr( emis_file, 'NLAYS' ) )
    else:
        conc_lay = int( setup_config.conc_out_lays )
    if str( cmaq_config.conc_out_lays ).lower() == 'template':
        cmaq_config.conc_out_lays = '1 {:}'.format( conc_lay )
    if str( cmaq_config.avg_conc_out_lays ).lower() == 'template':
        cmaq_config.avg_conc_out_lays = '1 {:}'.format( conc_lay )
    
    # set conc_spcs
    if str( setup_config.conc_spcs ).lower() == 'icon':
        conc_spcs = ncf.get_attr( icon_file, 'VAR-LIST' ).split()
    elif str( setup_config.conc_spcs ).lower() == 'emis':
        conc_spcs = ncf.get_attr( emis_file, 'VAR-LIST' ).split()
    else:
        conc_spcs = [ str(s) for s in setup_config.conc_spcs ]
    if str( cmaq_config.conc_spcs ).lower() == 'template':
        cmaq_config.conc_spcs = ' '.join( conc_spcs )
    if str( cmaq_config.avg_conc_spcs ).lower() == 'template':
        cmaq_config.avg_conc_spcs = ' '.join( conc_spcs )
    
    # set force_lays
    if str( setup_config.force_lays ).lower() == 'conc':
        force_lay = int( conc_lay )
    else:
        force_lay = int( setup_config.force_lays )
    if str( cmaq_config.force_lays ).lower() == 'template':
        cmaq_config.force_lays = str( force_lay )
    
    # set sense_emis_lays
    if str( setup_config.sense_emis_lays ).lower() == 'emis':
        sense_lay = int( emis_lays )
    elif str( setup_config.sense_emis_lays ).lower() == 'conc':
        sense_lay = int( conc_lay )
    else:
        sense_lay = int( setup_config.sense_emis_lays )
    if str( cmaq_config.sense_emis_lays ).lower() == 'template':
        cmaq_config.sense_emis_lays = str( sense_lay )

    cmaq_handle.wipeout()
    cmaq_handle.run_fwd_single( dt.start_date, is_first=True )
    #use conc_file as force_file
    shutil.copyfile( conc_file, force_file )
    cmaq_handle.run_bwd_single( dt.start_date, is_first=True )
    
    # copy files into template locations
    shutil.copyfile( emis_file, template.emis )
    shutil.copyfile( icon_file, template.icon )
    shutil.copyfile( conc_file, template.conc )
    shutil.copyfile( force_file, template.force )
    shutil.copyfile( sense_emis_file, template.sense_emis )
    shutil.copyfile( sense_conc_file, template.sense_conc )
    
    # clean up new files created by cmaq
    cmaq_handle.wipeout()
