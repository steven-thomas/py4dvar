
import os
import shutil
import datetime as dt
import subprocess

import _get_root
import fourdvar.util.cmaq_config as cfg
import fourdvar.util.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.file_handle as fh


import setup_logging
logger = setup_logging.get_logger( __file__ )

def parse_env_dict( env_dict, date ):
    """
    extension: convert date patterns into values
    input: dictionary (envvar_name: pattern_value), dt.date
    output: dictionary (envvar_name: actual_value)
    """
    ymd = date.strftime('%Y%m%d')
    yj = date.strftime('%Y%j')
    yesterday = ( date - dt.timedelta(days=1) ).strftime('%Y%m%d')
    tomorrow = ( date + dt.timedelta(days=1) ).strftime('%Y%m%d')
    rep_dict = {'<YYYYMMDD>': ymd, '<YYYYDDD>': yj,
                '<YESTERDAY>': yesterday, '<TOMORROW>': tomorrow}
    for old, new in rep_dict.items():
        env_dict = { key: value.replace( old, new ) for key, value in env_dict.items() }
    return env_dict

def load_env( env_dict ):
    """
    extension: load dictionary into environment variables
    input: dictionary (envvar_name: value)
    output: None
    
    notes: all names and values must be strings
    """
    for name, value in env_dict.items():
        logger.debug( 'setenv {} = {}'.format( name, value ) )
        os.environ[ name ] = value
    return None

def clean_env( env_dict ):
    """
    extension: remove dictionary keys from environment variables
    input: dictionary (envvar_name: value)
    output: None
    """
    for name in env_dict.keys():
        del os.environ[ name ]
    return None

def setup_run():
    """
    extension: setup all the constant environment variables
    input: None
    output: None
    """
    env_dict = {}
    env_dict['NPCOL_NPROW'] = '{:} {:}'.format(cfg.npcol, cfg.nprow)
    env_dict['IOAPI_LOG_WRITE'] = 'T' if cfg.ioapi_logging else 'F'
    env_dict['CTM_MAXSYNC'] = str(cfg.maxsync)
    env_dict['CTM_MINSYNC'] = str(cfg.minsync)
    env_dict['CTM_PT3DEMIS'] = 'Y' if cfg.pt3demis else 'N'
    env_dict['KZMIN'] = 'Y' if cfg.kzmin else 'N'
    env_dict['FL_ERR_STOP'] = 'T' if cfg.fl_err_stop else 'F'
    env_dict['PROMPTFLAG'] = 'T' if cfg.promptflag else 'F'
    env_dict['EMISDATE'] = cfg.emisdate
    env_dict['CTM_STDATE'] = cfg.stdate
    env_dict['CTM_STTIME'] = ''.join( [ '{:02d}'.format(i) for i in cfg.sttime ] )
    env_dict['CTM_RUNLEN'] = ''.join( [ '{:02d}'.format(i) for i in cfg.runlen ] )
    env_dict['CTM_TSTEP'] = ''.join( [ '{:02d}'.format(i) for i in cfg.tstep ] )
    
    emlays = str(int(ncf.get_attr( template.emis, 'NLAYS' ) ) )
    conclays = str(int( ncf.get_attr( template.conc, 'NLAYS' ) ) )
    concspcs = str( ncf.get_attr( template.conc, 'VAR-LIST' ) )
    if cfg.emis_lays.strip().lower() == 'template':
        env_dict['CTM_EMLAYS'] = emlays
    else:
        env_dict['CTM_EMLAYS'] = cfg.emis_lays
    if cfg.conc_out_lays.strip().lower() == 'template':
        env_dict['CONC_BLEV_ELEV'] = '1 {:}'.format( conclays )
    else:
        env_dict['CONC_BLEV_ELEV'] = cfg.conc_out_lays
    if cfg.avg_conc_out_lays.strip().lower() == 'template':
        env_dict['ACONC_BLEV_ELEV'] = '1 {:}'.format( conclays )
    else:
        env_dict['ACONC_BLEV_ELEV'] = cfg.avg_conc_out_lays
    if cfg.conc_spcs.strip().lower() == 'template':
        env_dict['CONC_SPCS'] = ' '.join( concspcs.split() )
    else:
        env_dict['CONC_SPCS'] = cfg.conc_spcs
    if cfg.avg_conc_spcs.strip().lower() == 'template':
        env_dict['AVG_CONC_SPCS'] = ' '.join( concspcs.split() )
    else:
        env_dict['AVG_CONC_SPCS'] = 'template'
    
    env_dict['ADJ_CHEM_CHK'] = cfg.chem_chk + ' -v'
    env_dict['ADJ_VDIFF_CHK'] = cfg.vdiff_chk + ' -v'
    env_dict['ADJ_AERO_CHK'] = cfg.aero_chk + ' -v'
    env_dict['ADJ_HA_RHOJ_CHK'] = cfg.ha_rhoj_chk + ' -v'
    env_dict['ADJ_VA_RHOJ_CHK'] = cfg.va_rhoj_chk + ' -v'
    env_dict['ADJ_HADV_CHK'] = cfg.hadv_chk + ' -v'
    env_dict['ADJ_VADV_CHK'] = cfg.vadv_chk + ' -v'
    env_dict['ADJ_EMIS_CHK'] = cfg.emis_chk + ' -v'
    env_dict['ADJ_EMIST_CHK'] = cfg.emist_chk + ' -v'
    env_dict['GRIDDESC'] = cfg.griddesc
    env_dict['GRID_NAME'] = cfg.gridname
    env_dict['DEPV_TRAC_1'] = cfg.depv_trac
    env_dict['OCEAN_1'] = cfg.ocean_file
    env_dict['EMIS_1'] = cfg.emis_file
    env_dict['BNDY_GASC_1'] = cfg.bcon_file
    env_dict['BNDY_AERO_1'] = cfg.bcon_file
    env_dict['BNDY_NONR_1'] = cfg.bcon_file
    env_dict['BNDY_TRAC_1'] = cfg.bcon_file
    env_dict['GRID_DOT_2D'] = cfg.grid_dot_2d
    env_dict['GRID_CRO_2D'] = cfg.grid_cro_2d
    env_dict['MET_CRO_2D'] = cfg.met_cro_2d
    env_dict['MET_CRO_3D'] = cfg.met_cro_3d
    env_dict['MET_DOT_3D'] = cfg.met_dot_3d
    env_dict['MET_BDY_3D'] = cfg.met_bdy_3d
    env_dict['LAYER_FILE'] = cfg.layerfile
    env_dict['XJ_DATA'] = cfg.xj_data
    env_dict['CTM_CONC_1'] = cfg.conc_file + ' -v'
    env_dict['A_CONC_1'] = cfg.avg_conc_file + ' -v'
    env_dict['S_CGRID'] = cfg.last_grid_file + ' -v'
    env_dict['CTM_DRY_DEP_1'] = cfg.drydep_file + ' -v'
    env_dict['CTM_WET_DEP_1'] = cfg.wetdep1_file + ' -v'
    env_dict['CTM_WET_DEP_2'] = cfg.wetdep2_file + ' -v'
    env_dict['CTM_SSEMIS_1'] = cfg.ssemis_file + ' -v'
    env_dict['CTM_VIS_1'] = cfg.aerovis_file + ' -v'
    env_dict['CTM_DIAM_1'] = cfg.aerodiam_file + ' -v'
    env_dict['CTM_IPR_1'] = cfg.ipr1_file + ' -v'
    env_dict['CTM_IPR_2'] = cfg.ipr2_file + ' -v'
    env_dict['CTM_IPR_3'] = cfg.ipr3_file + ' -v'
    env_dict['CTM_IRR_1'] = cfg.irr1_file + ' -v'
    env_dict['CTM_IRR_2'] = cfg.irr2_file + ' -v'
    env_dict['CTM_IRR_3'] = cfg.irr3_file + ' -v'
    env_dict['CTM_RJ_1'] = cfg.rj1_file + ' -v'
    env_dict['CTM_RJ_2'] = cfg.rj2_file + ' -v'
    return env_dict

def run_fwd_single( date, is_first ):
    """
    extension: run cmaq fwd for a single day
    input: dt.date, Boolean (is this day the first of the model)
    output: None
    """
    
    env_dict = setup_run()

    env_dict['PERTCOLS'] = cfg.pertcols
    env_dict['PERTROWS'] = cfg.pertrows
    env_dict['PERTLEVS'] = cfg.pertlevs
    env_dict['PERTSPCS'] = cfg.pertspcs
    env_dict['PERTDELT'] = cfg.pertdelt
    env_dict['CTM_APPL'] = cfg.fwd_appl
    env_dict['CTM_XFIRST_OUT'] = cfg.fwd_xfirst_file
    env_dict['LOGFILE'] = cfg.fwd_logfile
    env_dict['FLOOR_FILE'] = cfg.floor_file
    env_dict['CTM_PROGNAME'] = cfg.fwd_prog

    if is_first is True:
        env_dict['INIT_GASC_1'] = cfg.icon_file
        env_dict['INIT_AERO_1'] = cfg.icon_file
        env_dict['INIT_NONR_1'] = cfg.icon_file
        env_dict['INIT_TRAC_1'] = cfg.icon_file
        env_dict['CTM_XFIRST_IN'] = ''
    else:
        prev_grid = cfg.last_grid_file.replace('<YYYYMMDD>', '<YESTERDAY>' )
        prev_xfirst = cfg.fwd_xfirst_file.replace('<YYYYMMDD>', '<YESTERDAY>' )
        env_dict['INIT_GASC_1'] = prev_grid
        env_dict['INIT_AERO_1'] = prev_grid
        env_dict['INIT_NONR_1'] = prev_grid
        env_dict['INIT_TRAC_1'] = prev_grid
        env_dict['CTM_XFIRST_IN'] = prev_xfirst
    
    env_dict = parse_env_dict( env_dict, date )
    load_env( env_dict )
    
    runlist = []
    if int(cfg.npcol) != 1 or int(cfg.nprow) != 1:
        #use mpi
        runlist = ['mpirun', '-np', str( int( cfg.npcol ) * int( cfg.nprow ) ) ]
    runlist.append( cfg.fwd_prog )
    fh.ensure_path( cfg.fwd_stdout_log, inc_file=True )
    with open( cfg.fwd_stdout_log, 'w' ) as stdout_file:
        statcode = subprocess.call( runlist, stdout=stdout_file, stderr=subprocess.STDOUT )
    if statcode != 0:
        msg = 'cmaq fwd failed on {}.'.format( date.strftime('%Y%m%d') )
        logger.error( msg )
        cleanup()
        raise AssertionError( msg )
    
    clean_env( env_dict )
    return None

def run_bwd_single( date, is_first ):
    """
    extension: run cmaq bwd for a single day
    input: dt.date, Boolean (is this the first time called)
    output: None
    """
    
    env_dict = setup_run()
    
    env_dict['CTM_APPL'] = cfg.bwd_appl
    env_dict['CTM_XFIRST_OUT'] = cfg.bwd_xfirst_file
    env_dict['CTM_XFIRST_IN'] = cfg.fwd_xfirst_file
    env_dict['LOGFILE'] = cfg.bwd_logfile
    env_dict['CTM_PROGNAME'] = cfg.bwd_prog
    env_dict['CHK_PATH'] = cfg.output_path
    env_dict['INIT_GASC_1'] = cfg.last_grid_file + ' -v'
    env_dict['INIT_AERO_1'] = cfg.last_grid_file + ' -v'
    env_dict['INIT_NONR_1'] = cfg.last_grid_file + ' -v'
    env_dict['INIT_TRAC_1'] = cfg.last_grid_file + ' -v'
    env_dict['CTM_CONC_FWD'] = cfg.conc_file + ' -v'
    env_dict['CTM_CGRID_FWD'] = cfg.last_grid_file + ' -v'
    env_dict['ADJ_LGRID'] = cfg.conc_sense_file + ' -v'
    env_dict['ADJ_LGRID_EM'] = cfg.emis_sense_file + ' -v'
    env_dict['ADJ_LGRID_EM_SF'] = cfg.emis_scale_sense_file + ' -v'
    env_dict['ADJ_FORCE'] = cfg.force_file

    if cfg.sense_sync is True:
        env_dict['LGRID_OUTPUT_FREQ'] = 'SYNC_STEP'
    else:
        env_dict['LGRID_OUTPUT_FREQ'] = cfg.sense_sync
    
    frclays = str(int(ncf.get_attr( template.force, 'NLAYS' ) ) )
    if cfg.force_lays.strip().lower() == 'template':
        env_dict['NLAYS_FRC'] = frclays
    else:
        env_dict['NLAYS_FRC'] = cfg.force_lays
    
    if is_first is not True:
        prev_conc = cfg.conc_sense_file.replace( '<YYYYMMDD>', '<TOMORROW>' )
        prev_emis = cfg.emis_sense_file.replace( '<YYYYMMDD>', '<TOMORROW>' )
        prev_scale = cfg.emis_scale_sense_file.replace( '<YYYYMMDD>', '<TOMORROW>' )
        env_dict['INIT_LGRID_1'] = prev_conc
        env_dict['INIT_EM_1'] = prev_emis
        env_dict['INIT_EM_SF_1'] = prev_scale
    
    env_dict = parse_env_dict( env_dict, date )
    load_env( env_dict )
    
    runlist = []
    if int(cfg.npcol) != 1 or int(cfg.nprow) != 1:
        #use mpi
        runlist = ['mpirun', '-np', str( int( cfg.npcol ) * int( cfg.nprow ) ) ]
    runlist.append( cfg.bwd_prog )
    fh.ensure_path( cfg.bwd_stdout_log, inc_file=True )
    with open( cfg.bwd_stdout_log, 'w' ) as stdout_file:
        statcode = subprocess.call( runlist, stdout=stdout_file, stderr=subprocess.STDOUT )
    if statcode != 0:
        msg = 'cmaq bwd failed on {}.'.format( date.strftime('%Y%m%d') )
        logger.error( msg )
        cleanup()
        raise AssertionError( msg )
        
    clean_env( env_dict )
    return None

def run_fwd():
    """
    extension: run cmaq fwd from current config
    input: None
    output: None
    """
    cur_date = cfg.start_date
    isfirst = True
    while cur_date <= cfg.end_date:
        run_fwd_single(cur_date, isfirst)
        isfirst = False
        cur_date += dt.timedelta(days=1)
    return None

def run_bwd():
    """
    extension: run cmaq bwd from current config
    input: None
    output: None
    """
    cur_date = cfg.end_date
    isfirst = True
    while cur_date >= cfg.start_date:
        run_bwd_single(cur_date, isfirst)
        isfirst = False
        cur_date -= dt.timedelta(days=1)
    return None

def cleanup():
    """
    extension: move/delete all files created by a run of cmaq
    input: None
    output: None
    
    notes: to move or delete file is set in cmaq_config
    """
    fh.ensure_path( cfg.archdir, inc_file=False )
    nprocs = int( cfg.npcol )*int( cfg.nprow )
    for (src_pattern, dst_pattern, is_ncf) in cfg.created_files:
        cur_date = cfg.start_date
        while cur_date <= cfg.end_date:
            ymd = cur_date.strftime('%Y%m%d')
            yj = cur_date.strftime('%Y%j')
            for proc_no in range(1, 1 + nprocs ):
                pn = '{:03}'.format( proc_no )
                rep_dict = { '<YYYYMMDD>': ymd, '<YYYYDDD>': yj, '<PROC_NO>': pn }
                src = src_pattern
                for old, new in rep_dict.items():
                    src = src.replace( old, new )
                if not os.path.isfile( src ):
                    #ignore missing file
                    continue
                if dst_pattern is not None:
                    #store file
                    dst = dst_pattern
                    for old, new in rep_dict.items():
                        dst = dst.replace( old, new )
                    if '<I>' in dst:
                        i = 1
                        while os.path.isfile( dst.replace('<I>','iter'+str(i)) ):
                            i += 1
                        dst = dst.replace('<I>','iter'+str(i))
                    if is_ncf is True:
                        ncf.copy_compress( src, dst )
                    else:
                        shutil.copyfile( src, dst )
                os.remove( src )
            cur_date += dt.timedelta(days=1)
    return None

def wipeout():
    """
    extension: delete all files created by a run of cmaq
    input: None
    output: None
    """
    for (src_pattern, dst_pattern, is_ncf) in cfg.created_files:
        cur_date = cfg.start_date
        while cur_date <= cfg.end_date:
            ymd = cur_date.strftime('%Y%m%d')
            yj = cur_date.strftime('%Y%j')
            rep_dict = { '<YYYYMMDD>': ymd, '<YYYYDDD>': yj }
            src = src_pattern
            for old, new in rep_dict.items():
                src = src.replace( old, new )
            if os.path.isfile( src ):
                os.remove( src )
            cur_date += dt.timedelta(days=1)
    return None
