
import datetime as dt

import _get_root
from fourdvar.util.date_handle import replace_date
import fourdvar.util.file_handle as fh
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.template_defn as template
import fourdvar.util.cmaq_config as cmaq_config
import fourdvar.util.global_config as global_config

all_files = { 'ModelInputData': {},
              'ModelOutputData': {},
              'AdjointForcingData': {},
              'SensitivityData': {} }

firsttime = True
def get_filedict( clsname ):
    """
    extension: return dictionary of files needed for data class
    input: string, name of dataclass
    output: dict, filedict has 3 keys: actual, template and archive
            actual: path to the file used by cmaq.
            template: path to the template file used to construct actual.
            archive: filename to use when saving an archvied copy of file.
    """
    msg = 'Must set global_config.{}'
    assert global_config.start_date is not None, msg.format('start_date')
    assert global_config.end_date is not None, msg.format('end_date')
    global all_files
    global firsttime
    if firsttime is True:
        firsttime = False
        build_filedict()
    return all_files[ clsname ]

def build_filedict():
    """
    extension: prepare dated copies of files for use in cmaq
    input: None
    output: None
    
    notes: should only be called once, after global_config has defined dates.
    """
    global all_files

    model_input_files = {}
    model_output_files = {}
    adjoint_forcing_files = {}
    sensitivity_files = {}
    
    all_files[ 'ModelInputData' ] = model_input_files
    all_files[ 'ModelOutputData' ] = model_output_files
    all_files[ 'AdjointForcingData' ] = adjoint_forcing_files
    all_files[ 'SensitivityData' ] = sensitivity_files

    fh.empty_dir( template.storage )

    ncf.copy_compress( template.icon, template.icon_store )
    ncf.set_date( template.icon_store, global_config.start_date )
    model_input_files['icon'] = {
        'actual': cmaq_config.icon_file,
        'template': template.icon_store,
        'archive': 'icon.ncf'
        }

    for date in global_config.get_datelist():
        dated_vsn = template.dated.copy()
        for src_path, dpat_path in template.dated.items():
            date_path = replace_date( dpat_path, date )
            dated_vsn[ src_path ] = date_path
            ncf.copy_compress( src_path, date_path )
            ncf.set_date( date_path, date )
        
        ymd = replace_date( '<YYYYMMDD>', date )
        model_input_files['emis.'+ymd] = {
            'actual': replace_date( cmaq_config.emis_file, date ),
            'template': dated_vsn[ template.emis ],
            'archive': 'emis.' + ymd + '.ncf'
            }
        model_output_files['conc.'+ymd] = {
            'actual': replace_date( cmaq_config.conc_file, date ),
            'template': dated_vsn[ template.conc ],
            'archive': 'conc.' + ymd + '.ncf'
            }
        adjoint_forcing_files['force.'+ymd] = {
            'actual': replace_date( cmaq_config.force_file, date ),
            'template': dated_vsn[ template.force ],
            'archive': 'force.' + ymd + '.ncf'
            }
        sensitivity_files['emis.'+ymd] = {
            'actual': replace_date( cmaq_config.emis_sense_file, date ),
            'template': dated_vsn[ template.sense_emis ],
            'archive': 'sense_emis.' + ymd + '.ncf'
            }
        sensitivity_files['conc.'+ymd] = {
            'actual': replace_date( cmaq_config.conc_sense_file, date ),
            'template': dated_vsn[ template.sense_conc ],
            'archive': 'sense_conc.' + ymd + '.ncf'
            }
    return None
