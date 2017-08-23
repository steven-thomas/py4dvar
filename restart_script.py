"""
restarts a previous unfinished minimization run.
You MUST ensure that the observation_data, prior and archive experiment name
are all unchanged from the previous run.
"""
import os

import _get_root
import fourdvar.user_driver as user
import fourdvar._main_driver as main
import fourdvar.util.archive_handle as archive_handle
import fourdvar.params.archive_defn as archive_defn
import fourdvar.datadef as d
from fourdvar._transform import transform

# If true restart_script uses last iteration in archive
restart_from_last = True

# If restart_from_last = False provide restart number (integer)
restart_number = None

# Must match filename used by user_driver.callback_func!
iter_fname = 'iter{:04}.ncf'

# name of restart log file saved to archive
restart_log_fname = 'restart_log.txt'



archive_path = os.path.join( archive_defn.root_dir, archive_defn.experiment )
archive_handle.archive_path = archive_path
archive_handle.finished_setup = True

if restart_from_last == False:
    start_no = restart_number
else:
    start_no = 1
    while os.path.isfile( os.path.join( archive_path,
                                        iter_fname.format(start_no+1) ) ):
        start_no += 1

assert start_no == int(start_no), 'restart_number must be an integer.'
init_path = os.path.join( archive_path, iter_fname.format(start_no) )
assert os.path.isfile( init_path ), 'Cannot find {}'.format( init_path )

log_path = os.path.join( archive_path, restart_log_fname )
if os.path.isfile( log_path ):
    ftype = 'r+'
else:
    ftype = 'w'
with open( log_path, ftype ) as f:
    f.write( 'restarted from iteration {}\n'.format( start_no ) )

user.iter_num = start_no
init_phys = d.PhysicalData.from_file( init_path )
init_unk = transform( init_phys, d.UnknownData )
init_vec = init_unk.get_vector()

min_output = user.minim( main.cost_func, main.gradient_func, init_vec )
out_vector = min_output[0]
out_unknown = d.UnknownData( out_vector )
out_physical = transform( out_unknown, d.PhysicalData )
user.post_process( out_physical, min_output[1:] )
user.cleanup()
