"""
Copies current cmaq input files into archive.
"""
from __future__ import absolute_import

import context
import fourdvar.datadef as d
import fourdvar.params.archive_defn as archive_defn
import fourdvar.util.archive_handle as archive_handle

# archive file name
archive_fname = 'original_CMAQ_input'

archive_handle.archive_path = archive_defn.archive_path
archive_handle.finished_setup = True

model_input = d.ModelInputData()
model_input.archive( archive_fname )
