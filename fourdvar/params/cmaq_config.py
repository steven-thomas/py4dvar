"""
cmaq_config.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os

from fourdvar.params.root_path_defn import store_path, share_path

#notes: the patterns <YYYYMMDD>, <YYYYDDD> & <YYYY-MM-DD> will be replaced
#with the year, month and day of the current model run

use_jobfs = False

#No. of processors per column
npcol = 1
#npcol = 4
#No. of processors per row
nprow = 1
#nprow = 4
#note: if npcol and nprow are 1 then cmaq is run in serial mode

#extra ioapi write logging
ioapi_logging = False

#max & min No. seconds per sync (science) step
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

#number of emission sensitivity layers to use.
#'template' means value calculated from template files.
#note: should always be >= emis_lays
sense_emis_lays = 'template'

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
fwd_appl = 'fwd_CO_CO2.<YYYYMMDD>'
bwd_appl = 'bwd_CO_CO2.<YYYYMMDD>'

#emis_date, use unknown
emisdate = '<YYYYMMDD>'

#output sensitivity on each sync (science) step
#WARNING: this option must match the sensitivity template files
sense_sync = False

#date and time model parameters
stdate = '<YYYYDDD>' #use unknown
sttime = [0,0,0] #start time of single run [hours, minutes, seconds]
runlen = [24,0,0] #duration of single run [hours, minutes, seconds] #DO NOT MODIFY
tstep = [1,0,0] #output timestep [hours, minutes, seconds]

cmaq_base = os.path.join( store_path, 'CMAQ' )
output_path = os.path.join( cmaq_base, 'output' )
if use_jobfs is True:
    chk_path = os.environ.get('PBS_JOBFS',None)
    if chk_path is None:
        msg = 'cannot find PBS_JOBFS, use_jobfs can only be run with qsub.'
        raise ValueError(msg)
else:
    chk_path = os.path.join( cmaq_base, 'chkpnt' )
mcip_path = os.path.join( share_path, 'mcip' )
grid_path = os.path.join( share_path, 'grid' )
jproc_path = os.path.join( share_path, 'jproc' )
bcon_path = os.path.join( cmaq_base, 'bcon' )
icon_path = os.path.join( cmaq_base, 'icon' )
emis_path = os.path.join( cmaq_base, 'emis' )

#horizontal grid definition file
griddesc = os.path.join( grid_path, 'GRIDDESC' )
gridname = 'CMAQ-BENCHMARK'

#logfile
fwd_logfile = os.path.join( output_path, 'fwd_CO_CO2.<YYYYMMDD>.log' )
bwd_logfile = os.path.join( output_path, 'bwd_CO_CO2.<YYYYMMDD>.log' )

#floor file
floor_file = os.path.join( output_path, 'FLOOR_bnmk' )

#checkpoint files
chem_chk = os.path.join( chk_path, 'CHEM_CHK.<YYYYMMDD>.nc' )
vdiff_chk = os.path.join( chk_path, 'VDIFF_CHK.<YYYYMMDD>.nc' )
aero_chk = os.path.join( chk_path, 'AERO_CHK.<YYYYMMDD>.nc' )
ha_rhoj_chk = os.path.join( chk_path, 'HA_RHOJ_CHK.<YYYYMMDD>.nc' )
va_rhoj_chk = os.path.join( chk_path, 'VA_RHOJ_CHK.<YYYYMMDD>.nc' )
hadv_chk = os.path.join( chk_path, 'HADV_CHK.<YYYYMMDD>.nc' )
vadv_chk = os.path.join( chk_path, 'VADV_CHK.<YYYYMMDD>.nc' )
emis_chk = os.path.join( chk_path, 'EMIS_CHK.<YYYYMMDD>.nc' )
emist_chk = os.path.join( chk_path, 'EMIST_CHK.<YYYYMMDD>.nc' )

#xfirst file
fwd_xfirst_file = os.path.join( output_path, 'XFIRST.<YYYYMMDD>' )
bwd_xfirst_file = os.path.join( output_path, 'XFIRST.bwd.<YYYYMMDD>' )

#input files
icon_file = os.path.join( icon_path, 'icon_CO_CO2.nc' )
bcon_file = os.path.join( bcon_path, 'bcon_CO_CO2.<YYYYMMDD>.nc' )
emis_file = os.path.join( emis_path, 'emis_CO_CO2.<YYYYMMDD>.nc' )
force_file = os.path.join( output_path, 'ADJ_FORCE.<YYYYMMDD>.nc' )
#required met data, use unknown
ocean_file = os.path.join( grid_path, 'surf_BENCHMARK.nc' )
grid_dot_2d = os.path.join( grid_path, 'GRIDDOT2D.nc' )
grid_cro_2d = os.path.join( grid_path, 'GRIDCRO2D.nc' )
met_cro_2d = os.path.join( mcip_path, 'METCRO2D_<YYYYMMDD>.nc' )
met_cro_3d = os.path.join( mcip_path, 'METCRO3D_<YYYYMMDD>.nc' )
met_dot_3d = os.path.join( mcip_path, 'METDOT3D_<YYYYMMDD>.nc' )
met_bdy_3d = os.path.join( mcip_path, 'METBDY3D_<YYYYMMDD>.nc' )
layerfile = met_cro_3d
depv_trac = met_cro_2d
xj_data = os.path.join( jproc_path, 'JTABLE_<YYYYDDD>' )

#output files
conc_file = os.path.join( output_path, 'CONC.<YYYYMMDD>.nc' )
avg_conc_file = os.path.join( output_path, 'ACONC.<YYYYMMDD>.nc' )
last_grid_file = os.path.join( output_path, 'CGRID.<YYYYMMDD>.nc' )
drydep_file = os.path.join( output_path, 'DRYDEP.<YYYYMMDD>.nc' )
wetdep1_file = os.path.join( output_path, 'WETDEP1.<YYYYMMDD>.nc' )
wetdep2_file = os.path.join( output_path, 'WETDEP2.<YYYYMMDD>.nc' )
ssemis_file = os.path.join( output_path, 'SSEMIS1.<YYYYMMDD>.nc' )
aerovis_file = os.path.join( output_path, 'AEROVIS.<YYYYMMDD>.nc' )
aerodiam_file = os.path.join( output_path, 'AERODIAM.<YYYYMMDD>.nc' )
ipr1_file = os.path.join( output_path, 'PA_1.<YYYYMMDD>.nc' )
ipr2_file = os.path.join( output_path, 'PA_2.<YYYYMMDD>.nc' )
ipr3_file = os.path.join( output_path, 'PA_3.<YYYYMMDD>.nc' )
irr1_file = os.path.join( output_path, 'IRR_1.<YYYYMMDD>.nc' )
irr2_file = os.path.join( output_path, 'IRR_2.<YYYYMMDD>.nc' )
irr3_file = os.path.join( output_path, 'IRR_3.<YYYYMMDD>.nc' )
rj1_file = os.path.join( output_path, 'RJ_1.<YYYYMMDD>.nc' )
rj2_file = os.path.join( output_path, 'RJ_2.<YYYYMMDD>.nc' )
conc_sense_file = os.path.join( output_path, 'LGRID.bwd_CO_CO2.<YYYYMMDD>.nc' )
emis_sense_file = os.path.join( output_path, 'EM.LGRID.bwd_CO_CO2.<YYYYMMDD>.nc' )
emis_scale_sense_file = os.path.join( output_path, 'EM_SF.LGRID.bwd_CO_CO2.<YYYYMMDD>.nc' )

curdir = os.path.realpath( os.curdir )

#temporary, change when reworking archive system
fwd_stdout_log = os.path.join( output_path, 'fwd_stdout.log' )
bwd_stdout_log = os.path.join( output_path, 'bwd_stdout.log' )

#list of patterns of logs created by cmaq in curent working dir
#cmaq_handle.wipeout resolves and deletes all listed files.
cwd_logs = [ os.path.join( curdir, 'CTM_LOG_*' ),
             os.path.join( curdir, 'N_SPC_EMIS.dat' ) ]

#list of all files above created by CMAQ (fwd & bwd) to be delete by wipeout()
wipeout_fwd_list = [ fwd_logfile, floor_file, chem_chk, vdiff_chk, aero_chk,
                     ha_rhoj_chk, va_rhoj_chk, hadv_chk, vadv_chk, emis_chk,
                     emist_chk, fwd_xfirst_file, conc_file, avg_conc_file,
                     last_grid_file, drydep_file, wetdep1_file, wetdep2_file,
                     ssemis_file, aerovis_file, aerodiam_file, ipr1_file,
                     ipr2_file, ipr3_file, irr1_file, irr2_file, irr3_file,
                     rj1_file, rj2_file, fwd_stdout_log ]
wipeout_bwd_list = [ bwd_logfile, bwd_xfirst_file, conc_sense_file,
                     emis_sense_file, emis_scale_sense_file, bwd_stdout_log ]

#drivers
fwd_prog = os.path.join( share_path, 'BLD_fwd_CO_CO2', 'ADJOINT_FWD' )
bwd_prog = os.path.join( share_path, 'BLD_bwd_CO_CO2', 'ADJOINT_BWD' )

#shell used to call drivers
cmd_shell = '/bin/csh'

#shell input added before running drivers
cmd_preamble = 'unlimit; '
