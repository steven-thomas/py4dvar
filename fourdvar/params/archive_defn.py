
import os

from fourdvar.params.root_path_defn import store_path

#Settings for archive processes

#location of archive directory
archive_path = os.path.join( store_path, 'archive' )

#archive model output of each successful iteration
iter_model_output = False

#archive observation-lite of each successful iteration
iter_obs_lite = True

#experiment name & name of directory to save results in
experiment = 'example_experiment'

#description is copied into a txt file in the experiment directory
description = """This is a test of the fourdvar system.
The description here should contain details of the experiment
and is written to the description text file."""
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
#patterns can include <YYYYMMDD>, <YYYYDDD> or <YYYY-MM-DD> tags to specify day
#initial conditions file
icon_file = 'icon.nc'
#emission file, requires a tag to map date
emis_file = 'emis.<YYYYMMDD>.nc'
#concentration file, requires a tag to map date
conc_file = 'conc.<YYYYMMDD>.nc'
#adjoint forcing file, requires a tag to map date
force_file = 'force.<YYYYMMDD>.nc'
#concentration sensitivity file, requires a tag to map date
sens_conc_file = 'sens_conc.<YYYYMMDD>.nc'
#emission sensitivity file, requires a tag to map date
sens_emis_file = 'sens_emis.<YYYYMMDD>.nc'
