
import datetime as dt

import _get_root
import fourdvar.util.file_handle as fh
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.cmaq_config as cfg
import fourdvar.util.template_defn as template

model_input_files = {}
model_output_files = {}
adjoint_forcing_files = {}
sensitivity_files = {}

fh.empty_dir( template.storage )

ncf.copy_compress( template.icon, template.icon_store )
ncf.set_date( template.icon_store, cfg.start_date )
model_input_files['icon'] = {
    'actual': cfg.icon_file,
    'template': template.icon_store,
    'archive': 'icon.ncf'
}

cur_date = cfg.start_date
while cur_date <= cfg.end_date:
    ymd = cur_date.strftime( '%Y%m%d' )    
    dated_vsn = template.dated.copy()
    for src_path, dpat_path in template.dated.items():
        date_path = dpat_path.replace( '<YYYYMMDD>', ymd )
        dated_vsn[ src_path ] = date_path
        ncf.copy_compress( src_path, date_path )
        ncf.set_date( date_path, cur_date )
    
    model_input_files['emis.'+ymd] = {
        'actual': cfg.emis_file.replace( '<YYYYMMDD>', ymd ),
        'template': dated_vsn[ template.emis ],
        'archive': 'emis.' + ymd + '.ncf'
    }
    model_output_files['conc.'+ymd] = {
        'actual': cfg.conc_file.replace( '<YYYYMMDD>', ymd ),
        'template': dated_vsn[ template.conc ],
        'archive': 'conc.' + ymd + '.ncf'
    }
    adjoint_forcing_files['force.'+ymd] = {
        'actual': cfg.force_file.replace( '<YYYYMMDD>', ymd ),
        'template': dated_vsn[ template.force ],
        'archive': 'force.' + ymd + '.ncf'
    }
    sensitivity_files['emis.'+ymd] = {
        'actual': cfg.emis_sense_file.replace( '<YYYYMMDD>', ymd ),
        'template': dated_vsn[ template.sense_emis ],
        'archive': 'sense_emis.' + ymd + '.ncf'
    }
    sensitivity_files['conc.'+ymd] = {
        'actual': cfg.conc_sense_file.replace( '<YYYYMMDD>', ymd ),
        'template': dated_vsn[ template.sense_conc ],
        'archive': 'sense_conc.' + ymd + '.ncf'
    }
    cur_date += dt.timedelta( days=1 )
