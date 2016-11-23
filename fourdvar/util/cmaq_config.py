
import os

import _get_root
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.global_config as glob_cfg

#notes: the patterns <YYYYMMDD> & <YYYYDDD> will be replaced
#with the year, month and day of the current model run

#No. of processors per column
#npcol = 1
npcol = 4
#No. of processors per row
#nprow = 1
nprow = 4
#note: if npcol and nprow are 1 then cmaq is run in serial mode

#extra ioapi write logging
ioapi_logging = False

#sync range, use unknown
maxsync = 600
minsync = 600

#use PT3DEMIS (option not supported)
#DO NOT MODIFY
pt3demis = False

#number of emission layers to use.
#'template' means value calculated from template files.
emis_lays = 'template'

#number of forcing layers to use.
#'template' means value calculated from template files.
force_lays = 'template'

#kzmin, use unknown
kzmin = False

#stop on input file mismatch
fl_err_stop = False

#use IO-API prompt interactive mode
promptflag = False

#output species
#'template' means value calculated from template files
conc_spcs = 'template'
avg_conc_spcs = 'template'

#output layers
#'template' means value calculated from template files
conc_out_lays = 'template'
avg_conc_out_lays = 'template'

#perturbation variables (option not supported)
#DO NOT MODIFY
pertcols = '1'
pertrows = '1'
pertlevs = '1'
pertspcs = '2'
pertdelt = '1.00'

#application name
fwd_appl = 'fwd_CO2only.<YYYYMMDD>'
bwd_appl = 'bwd_CO2only.<YYYYMMDD>'

#emis_date, use unknown
emisdate = '<YYYYMMDD>'

#sync sensitivity output to timestep (required)
#DO NOT TOUCH
sense_sync = True

#date and time model parameters
stdate = '<YYYYDDD>' #use unknown
sttime = [0,0,0] #start time of single run [hours, minutes, seconds]
runlen = [24,0,0] #duration of single run [hours, minutes, seconds]
tstep = [1,0,0] #output timestep [hours, minutes, seconds]


cmaq_base = os.path.join( '/', 'home', '563', 'spt563', 'cmaq_adj' )
cmaq_data = os.path.join( cmaq_base, 'CMAQadjBnmkData' )
output_path = os.path.join( cmaq_data, 'GHG_output' )
mcip_path = os.path.join( cmaq_data, 'mcip' )

#horizontal grid definition file
griddesc = os.path.join( cmaq_data, 'other', 'GRIDDESC' )
gridname = 'CMAQ-BENCHMARK'

#logfile
fwd_logfile = os.path.join( output_path, 'fwd_CO2only.<YYYYMMDD>.log' )
bwd_logfile = os.path.join( output_path, 'bwd_CO2only.<YYYYMMDD>.log' )

#floor file
floor_file = os.path.join( output_path, 'FLOOR_bnmk' )

#checkpoint files
chem_chk = os.path.join( output_path, 'CHEM_CHK.<YYYYMMDD>' )
vdiff_chk = os.path.join( output_path, 'VDIFF_CHK.<YYYYMMDD>' )
aero_chk = os.path.join( output_path, 'AERO_CHK.<YYYYMMDD>' )
ha_rhoj_chk = os.path.join( output_path, 'HA_RHOJ_CHK.<YYYYMMDD>' )
va_rhoj_chk = os.path.join( output_path, 'VA_RHOJ_CHK.<YYYYMMDD>' )
hadv_chk = os.path.join( output_path, 'HADV_CHK.<YYYYMMDD>' )
vadv_chk = os.path.join( output_path, 'VADV_CHK.<YYYYMMDD>' )
emis_chk = os.path.join( output_path, 'EMIS_CHK.<YYYYMMDD>' )
emist_chk = os.path.join( output_path, 'EMIST_CHK.<YYYYMMDD>' )

#xfirst file
fwd_xfirst_file = os.path.join( output_path, 'XFIRST.<YYYYMMDD>' )
bwd_xfirst_file = os.path.join( output_path, 'XFIRST.bwd.<YYYYMMDD>' )

#input files
icon_file = os.path.join( cmaq_data, 'icon', 'ICON_CMAQ-CO2test_profile' )
bcon_file = os.path.join( cmaq_data, 'bcon', 'BCON_CMAQ-CO2test_profile' )
emis_file = os.path.join( cmaq_data, 'emis', 'emis_CMAQ-CO2test_<YYYYMMDD>.ncf' )
force_file = os.path.join( output_path, 'ADJ_FORCE.<YYYYMMDD>' )
#required met data, use unknown
ocean_file = os.path.join( cmaq_data, 'other', 'surf_BENCHMARK.ncf' )
grid_dot_2d = os.path.join( mcip_path, 'GRIDDOT2D_<YYYYMMDD>' )
grid_cro_2d = os.path.join( mcip_path, 'GRIDCRO2D_<YYYYMMDD>' )
met_cro_2d = os.path.join( mcip_path, 'METCRO2D_<YYYYMMDD>' )
met_cro_3d = os.path.join( mcip_path, 'METCRO3D_<YYYYMMDD>' )
met_dot_3d = os.path.join( mcip_path, 'METDOT3D_<YYYYMMDD>' )
met_bdy_3d = os.path.join( mcip_path, 'METBDY3D_<YYYYMMDD>' )
layerfile = met_cro_3d
depv_trac = met_cro_2d
xj_data = os.path.join( cmaq_data, 'jproc', 'JTABLE_<YYYYDDD>' )

#output files
conc_file = os.path.join( output_path, 'CONC.<YYYYMMDD>' )
avg_conc_file = os.path.join( output_path, 'ACONC.<YYYYMMDD>' )
last_grid_file = os.path.join( output_path, 'CGRID.<YYYYMMDD>' )
drydep_file = os.path.join( output_path, 'DRYDEP.<YYYYMMDD>' )
wetdep1_file = os.path.join( output_path, 'WETDEP1.<YYYYMMDD>' )
wetdep2_file = os.path.join( output_path, 'WETDEP2.<YYYYMMDD>' )
ssemis_file = os.path.join( output_path, 'SSEMIS1.<YYYYMMDD>' )
aerovis_file = os.path.join( output_path, 'AEROVIS.<YYYYMMDD>' )
aerodiam_file = os.path.join( output_path, 'AERODIAM.<YYYYMMDD>' )
ipr1_file = os.path.join( output_path, 'PA_1.<YYYYMMDD>' )
ipr2_file = os.path.join( output_path, 'PA_2.<YYYYMMDD>' )
ipr3_file = os.path.join( output_path, 'PA_3.<YYYYMMDD>' )
irr1_file = os.path.join( output_path, 'IRR_1.<YYYYMMDD>' )
irr2_file = os.path.join( output_path, 'IRR_2.<YYYYMMDD>' )
irr3_file = os.path.join( output_path, 'IRR_3.<YYYYMMDD>' )
rj1_file = os.path.join( output_path, 'RJ_1.<YYYYMMDD>' )
rj2_file = os.path.join( output_path, 'RJ_2.<YYYYMMDD>' )
conc_sense_file = os.path.join( output_path, 'LGRID.bwd_CO2only.<YYYYMMDD>' )
emis_sense_file = os.path.join( output_path,
                                'EM.LGRID.bwd_CO2only.<YYYYMMDD>' )
emis_scale_sense_file = os.path.join( output_path,
                                      'EM_SF.LGRID.bwd_CO2only.<YYYYMMDD>' )

#drivers
fwd_prog = os.path.join( cmaq_base, 'BLD_fwd_CO2only', 'ADJOINT_FWD' )
bwd_prog = os.path.join( cmaq_base, 'BLD_bwd_CO2only', 'ADJOINT_BWD' )


curdir = os.path.realpath( os.curdir )
archdir = os.path.join( get_archive_path(), 'cmaq_extra' )

fwd_stdout_log = os.path.join( archdir, 'fwd_stdout.log' )
bwd_stdout_log = os.path.join( archdir, 'bwd_stdout.log' )

#format: [cmaq_path, storage_path, is_netcdf]
#notes: storage_path==None means file is not kept.
#<I> in storage_path is replaced with iteration number, therefore every iteration is stored
#is_netcdf==True means storage uses netcdf_handle.copy_compress
created_files = [
    [ os.path.join( curdir, 'CTM_LOG_<PROC_NO>.'+fwd_appl ), None, False ],
    [ os.path.join( curdir, 'CTM_LOG_<PROC_NO>.'+bwd_appl ), None, False ],
    [ os.path.join( curdir, 'N_SPC_EMIS.dat' ), None, False ],
    [ fwd_logfile, os.path.join( archdir, os.path.basename( fwd_logfile ) ), False ],
    [ bwd_logfile, os.path.join( archdir, os.path.basename( bwd_logfile ) ), False ],
    [ floor_file, os.path.join( archdir, 'FLOOR.<I>.<YYYYMMDD>' ), False ],
    [ chem_chk, os.path.join( archdir, os.path.basename( chem_chk ) ), True ],
    [ vdiff_chk, os.path.join( archdir, os.path.basename( vdiff_chk ) ), True ],
    [ aero_chk, os.path.join( archdir, os.path.basename( aero_chk ) ), True ],
    [ ha_rhoj_chk, os.path.join( archdir, os.path.basename( ha_rhoj_chk ) ), True ],
    [ va_rhoj_chk, os.path.join( archdir, os.path.basename( va_rhoj_chk ) ), True ],
    [ hadv_chk, os.path.join( archdir, os.path.basename( hadv_chk ) ), True ],
    [ vadv_chk, os.path.join( archdir, os.path.basename( vadv_chk ) ), True ],
    [ emis_chk, os.path.join( archdir, os.path.basename( emis_chk ) ), True ],
    [ emist_chk, os.path.join( archdir, os.path.basename( emist_chk ) ), True ],
    [ fwd_xfirst_file, None, False ],
    [ bwd_xfirst_file, None, False ],
    [ conc_file, os.path.join( archdir, os.path.basename( conc_file ) ), True ],
    [ avg_conc_file, os.path.join( archdir, os.path.basename( avg_conc_file ) ), True ],
    [ last_grid_file, os.path.join( archdir, os.path.basename( last_grid_file ) ), True ],
    [ drydep_file, os.path.join( archdir, os.path.basename( drydep_file ) ), True ],
    [ wetdep1_file, os.path.join( archdir, os.path.basename( wetdep1_file ) ), True ],
    [ wetdep2_file, os.path.join( archdir, os.path.basename( wetdep2_file ) ), True ],
    [ ssemis_file, os.path.join( archdir, os.path.basename( ssemis_file ) ), True ],
    [ aerovis_file, os.path.join( archdir, os.path.basename( aerovis_file ) ), True ],
    [ aerodiam_file, os.path.join( archdir, os.path.basename( aerodiam_file ) ), True ],
    [ ipr1_file, os.path.join( archdir, os.path.basename( ipr1_file ) ), True ],
    [ ipr2_file, os.path.join( archdir, os.path.basename( ipr2_file ) ), True ],
    [ ipr3_file, os.path.join( archdir, os.path.basename( ipr3_file ) ), True ],
    [ irr1_file, os.path.join( archdir, os.path.basename( irr1_file ) ), True ],
    [ irr2_file, os.path.join( archdir, os.path.basename( irr2_file ) ), True ],
    [ irr3_file, os.path.join( archdir, os.path.basename( irr3_file ) ), True ],
    [ rj1_file, os.path.join( archdir, os.path.basename( rj1_file ) ), True ],
    [ rj2_file, os.path.join( archdir, os.path.basename( rj2_file ) ), True ],
    [ conc_sense_file, os.path.join( archdir, os.path.basename( conc_sense_file ) ), True ],
    [ emis_sense_file, os.path.join( archdir, os.path.basename( emis_sense_file ) ), True ],
    [ emis_scale_sense_file,
      os.path.join( archdir, os.path.basename( emis_scale_sense_file ) ), True ],
    [ force_file, os.path.join( archdir, os.path.basename( force_file ) ), True ]
]
