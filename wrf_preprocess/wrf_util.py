
import os
import subprocess
import tarfile
from netCDF4 import Dataset

import context
import wrf_params

#jds version stores wrfout data in tar files on MDSS.
mdss_path = 'jds563/WRF/NWQLD'
get_tar_fname = lambda dom,date: 'wrfout_{:}.tar'.format(date.strftime('%Y%m%d'))

def setup_wrfout( dom, date, dst_path ):
    """After setup_wrfout returns the files listed in:
    wrf_params.wrf_files[ (dom,date) ]
    must exist in the
    wrf_params.wrfout_dir
    directory."""

    if dom == wrf_params.dom_list[0]:
        tar_fname = get_tar_fname( dom, date )

        cwd = os.getcwd()
        if not os.path.exists( wrf_params.wrfout_dir ):
            os.mkdir( wrf_params.wrfout_dir )
        os.chdir( wrf_params.wrfout_dir )
        cmd = 'mdss get {:}/{:}'.format( mdss_path, tar_fname )
        with open( os.path.join( cwd, 'output_mdss.log' ), 'w' ) as f:
            status = subprocess.call( cmd.split(' '), stdout=f, stderr=f )
        if status != 0:
            print "'mdss get' failed."
    
        with tarfile.open( tar_fname ) as f:
            tar_names = f.getnames()
            f.extractall( path=wrf_params.wrfout_dir )
        stime = date.strftime('%Y-%m-%d_%H:%M:%S')
        for fname in tar_names:
            src = os.path.join( wrf_params.wrfout_dir, fname )
            dst = os.path.join( wrf_params.wrfout_dir, fname.lower() )
            os.rename( src, dst )
            with Dataset( dst, 'r+' ) as f:
                f.setncattr( 'SIMULATION_START_DATE', stime )
        os.chdir( cwd )
    #check all needed wrf files exist
    day = date.strftime('%Y%m%d')
    for fname in wrf_params.wrf_files[ (dom,day) ]:
        src = os.path.join( wrf_params.wrfout_dir, fname )
        dst = os.path.join( dst_path, fname )
        if not os.path.exists( src ):
            raise RuntimeError( 'File not found: {:}'.format(fname) )
        os.rename( src, dst )
    return None

def clean_wrfout( dom, date, dst_path ):
    if dom == wrf_params.dom_list[-1]:
        tar_fname = get_tar_fname( dom, date )
        os.remove( os.path.join( wrf_params.wrfout_dir, tar_fname ) )
    day = date.strftime('%Y%m%d')
    for fname in wrf_params.wrf_files[ (dom,day) ]:
        dst = os.path.join( dst_path, fname )
        os.remove( dst )    
    return None
