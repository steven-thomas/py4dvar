
import os

from fourdvar.params.root_path_defn import store_path

#Settings for archive processes

#location of archive directory
archive_path = os.path.join( store_path, 'archive' )

#experiment name & name of directory to save results in
experiment = 'example_experiment'

#description is copied into a txt file in the experiment directory
description = """simple model template
model is x**3
3 unknowns
obsop is simple sum
"""
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
