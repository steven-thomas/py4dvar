
import os
import _get_root

#Settings for archive processes

#location of archive directory
root_dir = os.path.join( '/', 'home', '563', 'spt563',
                         'fourdvar', 'cmaq_vsn1',
                         'fourdvar', 'data', 'archive' )

#experiment name & name of directory to save results in
experiment = 'core_test_baseline'

#description is copied into a txt file in the experiment directory
description = """This is a test of the fourdvar system.
The description here should contain details of the experiment
baseline for comparison: only run on one node"""
#name of txt file holding the description, if empty string ('') file is not created.
desc_name = 'description.txt'

#if True, delete any existing archive with the same name.
#if False, create a new archive name to save results into.
overwrite = True

#pattern used to create new archive name if overwrite is False
#<E> is replaced with the experiment name
#<I> if replace with a number to make a unique directory name
#if a tag is missing the assumed format is: <E>extension<I>
extension = '<E>_vsn<I>'


#cmaq datadef files can be archived. These require an archive name pattern
#initial conditions file
icon_file = 'icon.ncf'
#emission file, requires a tag to map date (<YYYYMMDD> or <YYYYDDD>)
emis_file = 'emis.<YYYYMMDD>.ncf'
#concentration file, requires a tag to map date (<YYYYMMDD> or <YYYYDDD>)
conc_file = 'conc.<YYYYMMDD>.ncf'
#adjoint forcing file, requires a tag to map date (<YYYYMMDD> or <YYYYDDD>)
force_file = 'force.<YYYYMMDD>.ncf'
#concentration sensitivity file, requires a tag to map date (<YYYYMMDD> or <YYYYDDD>)
sens_conc_file = 'sens_conc.<YYYYMMDD>.ncf'
#emission sensitivity file, requires a tag to map date (<YYYYMMDD> or <YYYYDDD>)
sens_emis_file = 'sens_emis.<YYYYMMDD>.ncf'
