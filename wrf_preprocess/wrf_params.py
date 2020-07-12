"""
wrf_params.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import os
import datetime

import context
from fourdvar.params.root_path_defn import store_path
import fourdvar.util.date_handle as dt

APPL = 'NWQLD'
dom_list = ['d01','d02','d03']
day_list = [ date.strftime('%Y%m%d') for date in dt.get_datelist()]
target_dom = 'd01'


# MCIP settings
mcip_exe = '/home/563/spt563/CMAQ/CMAQv5.0.2/scripts/mcip/src/mcip.exe'
coord_name = 'LamCon_34S_134E'
grid_name_list = [ 'AUS_{:}'.format(dom) for dom in dom_list ]

wrf_pre_dir = os.path.join( store_path, 'wrf_preprocess_data' )
mcip_work_dir = os.path.join( wrf_pre_dir, 'mcip_work' )
geo_file_list = [ os.path.join( wrf_pre_dir, 'geo_data',
                                'geo_em.{:}.nc'.format(dom) )
                  for dom in dom_list ]

wrfout_dir = os.path.join( wrf_pre_dir, 'wrfout_data' )
#tar_fname = os.path.join( wrf_dir, 'wrfout_{:}.tar'.format(date.strftime('%Y%m%d')) )

# key = (domain, date), value = [ list of wrf files ]
wrf_files = {}
for dom in dom_list:
    for day,date in zip( day_list, dt.get_datelist() ):
        d = datetime.datetime( date.year, date.month, date.day )
        time_list = [ d + datetime.timedelta( seconds=h*60*60 )
                      for h in range(24+1) ]
        flist = [ 'wrfout_{:}_{:}'.format( dom,
                  time.strftime( '%Y-%m-%d_%H:%M:%S' ) )
                  for time in time_list ]
        wrf_files[ (dom,day,) ] = flist
