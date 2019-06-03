
import os
import numpy as np

import context
import fourdvar.util.date_handle as dt
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.cmaq_handle as cmaq_handle
import fourdvar.util.file_handle as fh
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.template_defn as template

# define cmaq filenames for first day of model run.
emis_file = dt.replace_date( cmaq_config.emis_file, dt.start_date )
icon_file = dt.replace_date( cmaq_config.icon_file, dt.start_date )
conc_file = dt.replace_date( cmaq_config.conc_file, dt.start_date )
force_file = dt.replace_date( cmaq_config.force_file, dt.start_date )
sense_conc_file = dt.replace_date( cmaq_config.conc_sense_file, dt.start_date )
sense_emis_file = dt.replace_date( cmaq_config.emis_sense_file, dt.start_date )

# redefine any cmaq_config variables dependent on template files
if str( cmaq_config.emis_lays ).lower() == 'template':
    emis_lay = int( ncf.get_attr( emis_file, 'NLAYS' ) )
    cmaq_config.emis_lays = str( emis_lay )

if str( cmaq_config.conc_out_lays ).lower() == 'template':
    conc_lay = int( ncf.get_attr( icon_file, 'NLAYS' ) )
    cmaq_config.conc_out_lays = '1 {:}'.format( conc_lay )

if str( cmaq_config.avg_conc_out_lays ).lower() == 'template':
    conc_lay = int( ncf.get_attr( icon_file, 'NLAYS' ) )
    cmaq_config.avg_conc_out_lays = '1 {:}'.format( conc_lay )

if str( cmaq_config.conc_spcs ).lower() == 'template':
    conc_spcs = ncf.get_attr( icon_file, 'VAR-LIST' ).split()
    cmaq_config.conc_spcs = ' '.join( conc_spcs )

if str( cmaq_config.avg_conc_spcs ).lower() == 'template':
    conc_spcs = ncf.get_attr( icon_file, 'VAR-LIST' ).split()
    cmaq_config.avg_conc_spcs = ' '.join( conc_spcs )

if str( cmaq_config.force_lays ).lower() == 'template':
    force_lay = int( ncf.get_attr( icon_file, 'NLAYS' ) )
    cmaq_config.force_lays = str( force_lay )

if str( cmaq_config.sense_emis_lays ).lower() == 'template':
    sense_lay = int( ncf.get_attr( icon_file, 'NLAYS' ) )
    cmaq_config.sense_emis_lays = str( sense_lay )

# generate sample files by running 1 day of cmaq (fwd & bwd)
cmaq_handle.wipeout_fwd()
cmaq_handle.run_fwd_single( dt.start_date, is_first=True )
# make force file with same attr as conc and all data zeroed
conc_spcs = ncf.get_attr( conc_file, 'VAR-LIST' ).split()
conc_data = ncf.get_variable( conc_file, conc_spcs )
force_data = { k:np.zeros(v.shape) for k,v in conc_data.items() }
ncf.create_from_template( conc_file, force_file, force_data )
cmaq_handle.run_bwd_single( dt.start_date, is_first=True )

# create record for icon & emis files
fh.ensure_path( os.path.dirname( template.icon ) )
ncf.copy_compress( icon_file, template.icon )
for date in dt.get_datelist():
    emis_src = dt.replace_date( cmaq_config.emis_file, date )
    emis_dst = dt.replace_date( template.emis, date )
    fh.ensure_path( os.path.dirname( emis_dst ) )
    ncf.copy_compress( emis_src, emis_dst )

# create template for conc, force & sense files
fh.ensure_path( os.path.dirname( template.conc ) )
fh.ensure_path( os.path.dirname( template.force ) )
fh.ensure_path( os.path.dirname( template.sense_emis ) )
fh.ensure_path( os.path.dirname( template.sense_conc ) )
ncf.copy_compress( conc_file, template.conc )
ncf.copy_compress( force_file, template.force )
ncf.copy_compress( sense_emis_file, template.sense_emis )
ncf.copy_compress( sense_conc_file, template.sense_conc )

# clean up files created by cmaq
cmaq_handle.wipeout_fwd()
