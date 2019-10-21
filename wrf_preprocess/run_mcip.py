
import numpy as np
import os
import tarfile
import datetime
import glob
import subprocess
import shutil
from netCDF4 import Dataset

import context
import wrf_params
import wrf_util
import fourdvar.util.date_handle as dt

for day,date in zip( wrf_params.day_list, dt.get_datelist() ):
    nextDate = date + datetime.timedelta( days=1 )
    times = [ date + datetime.timedelta( seconds=h*60*60 )
              for h in range(24+1) ]
    
    #variables for namelist
    mcip_start = '{:}:00:00.0000'.format(date.strftime('%Y-%m-%d-%H'))
    mcip_end = '{:}:00:00.0000'.format(nextDate.strftime('%Y-%m-%d-%H'))
    intvl = 60
    ctmlays = "-1.0"
    #use unknown, check later
    btrim = 4
    x0 = 1
    y0 = 1
    ncols = 89
    nrows = 104
    lprt_col = 0
    lprt_row = 0
    wrf_lc_ref_lat = -999.0

    for di,dom in enumerate( wrf_params.dom_list ):
        
        day_dom = '{:}_{:}'.format( day, dom )
        mcip_dir = os.path.join( wrf_params.mcip_work_dir, day_dom )
        if os.path.exists( mcip_dir ):
            shutil.rmtree( mcip_dir )
        os.mkdir( mcip_dir )
        os.chdir( mcip_dir )

        wrf_util.setup_wrfout( dom, date, mcip_dir )
        wrf_files = wrf_params.wrf_files[ (dom,day) ]
                
        nl_fname = os.path.join( mcip_dir, 'namelist.mcip' )
        file_gd  = os.path.join( mcip_dir, 'GRIDDESC' )
        file_hdr = os.path.join( mcip_dir, 'mmheader.{:}'.format( wrf_params.APPL ) )

        nl_txt = [ '', ' &FILENAMES' ]
        nl_txt.append( '  file_gd    = "{:}"'.format(file_gd) )
        nl_txt.append( '  file_hdr   = "{:}"'.format(file_hdr) )
        for i,fname in enumerate( wrf_files ):
            if i == 0:
                lead_txt = '  file_mm    = '
            else:
                lead_txt = '               '
            nl_txt.append( '{:}"{:}",'.format( lead_txt, fname ) )
        geo_file = wrf_params.geo_file_list[ di ]
        nl_txt.append( '  file_ter   = "{:}"'.format( geo_file ) )
        nl_txt.append( '  makegrid   = .T.' )
        nl_txt += [ ' &END', '', ' &USERDEFS' ]
        nl_txt.append( '  lpv        =  0' )
        nl_txt.append( '  lwout      =  0' )
        nl_txt.append( '  luvcout    =  1' )
        nl_txt.append( '  lsat       =  0' )
        nl_txt.append( '  mcip_start = "{:}"'.format( mcip_start ) )
        nl_txt.append( '  mcip_end   = "{:}"'.format( mcip_end ) )
        nl_txt.append( '  intvl      =  {:}'.format( intvl ) )
        nl_txt.append( '  coordnam   = "{:}"'.format( wrf_params.coord_name ) )
        grid_name = wrf_params.grid_name_list[ di ]
        nl_txt.append( '  grdnam     = "{:}"'.format( grid_name ) )
        nl_txt.append( '  ctmlays    =  {:}'.format( ctmlays ) )
        nl_txt.append( '  btrim      =  {:}'.format( btrim ) )
        nl_txt.append( '  lprt_col   =  {:}'.format( lprt_col ) )
        nl_txt.append( '  lprt_row   =  {:}'.format( lprt_row ) )
        nl_txt.append( '  wrf_lc_ref_lat = {:}'.format( wrf_lc_ref_lat ) )
        nl_txt += [ ' &END', '', ' &WINDOWDEFS' ]
        nl_txt.append( '  x0         =  {:}'.format( x0 ) )
        nl_txt.append( '  y0         =  {:}'.format( y0 ) )
        nl_txt.append( '  ncolsin    =  {:}'.format( ncols ) )
        nl_txt.append( '  nrowsin    =  {:}'.format( nrows ) )
        nl_txt += [ ' &END' ]

        with open( nl_fname, 'w' ) as f:
            for line in nl_txt:
                f.write( line + '\n' )

        #setup links to FORTRAN units
        os.symlink( file_hdr, 'fort.2' )
        os.symlink( file_gd, 'fort.4' )
        os.symlink( nl_fname, 'fort.8' )
        os.symlink( geo_file, 'fort.9' )
        for i, fname in enumerate(wrf_files):
            os.symlink( fname, 'fort.{:}'.format( 10+i ) )

        #set environment variables
        os.environ[ 'IOAPI_CHECK_HEADERS' ] = 'T'
        os.environ[ 'EXECUTION_ID' ] = 'mcip'
        os.environ[ 'GRID_BDY_2D' ] = '{:}/GRIDBDY2D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'GRID_CRO_2D' ] = '{:}/GRIDCRO2D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'GRID_CRO_3D' ] = '{:}/GRIDCRO3D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'GRID_DOT_3D' ] = '{:}/GRIDDOT3D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'MET_BDY_3D' ] = '{:}/METBDY3D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'MET_CRO_2D' ] = '{:}/METCRO2D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'MET_CRO_3D' ] = '{:}/METCRO3D_{:}'.format( mcip_dir, wrf_params.APPL )
        os.environ[ 'MET_DOT_3D' ] = '{:}/METDOT3D_{:}'.format( mcip_dir, wrf_params.APPL )

        #call mcip
        with open( 'output_mcip.log', 'w' ) as f:
            status = subprocess.call( wrf_params.mcip_exe, stdout=f, stderr=f )
        if status == 0:
            for fname in glob.glob( 'fort.*' ):
                os.remove( fname )
            wrf_util.clean_wrfout( dom, date, mcip_dir )
            print 'Finished Successfully.'
        else:
            print 'Failed running mcip.'
