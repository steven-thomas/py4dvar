
import _get_root
import fourdvar.util.date_handle as dt
import fourdvar.util.file_handle as file_handle
import fourdvar.util.netcdf_handle as ncf
import fourdvar.params.template_defn as template
import fourdvar.params.archive_defn as archive
import fourdvar.params.cmaq_config as cmaq_config

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
            archive: filename to use when saving an archived copy of file.
    """
    msg = 'Must set date_handle.{}'
    assert dt.start_date is not None, msg.format('start_date')
    assert dt.end_date is not None, msg.format('end_date')
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
    
    notes: should only be called once, after date_handle has defined dates.
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

    file_handle.empty_dir( template.storage )

    ncf.copy_compress( template.icon, template.icon_store )
    ncf.set_date( template.icon_store, dt.start_date )
    model_input_files['icon'] = {
        'actual': cmaq_config.icon_file,
        'template': template.icon_store,
        'archive': archive.icon_file
        }

    for date in dt.get_datelist():
        dated_vsn = template.dated.copy()
        for src_path, dpat_path in template.dated.items():
            date_path = dt.replace_date( dpat_path, date )
            dated_vsn[ src_path ] = date_path
            ncf.copy_compress( src_path, date_path )
            ncf.set_date( date_path, date )
        
        ymd = dt.replace_date( '<YYYYMMDD>', date )
        model_input_files['emis.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.emis_file, date ),
            'template': dated_vsn[ template.emis ],
            'archive': dt.replace_date( archive.emis_file, date )
            }
        model_output_files['conc.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.conc_file, date ),
            'template': dated_vsn[ template.conc ],
            'archive': dt.replace_date( archive.conc_file, date )
            }
        adjoint_forcing_files['force.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.force_file, date ),
            'template': dated_vsn[ template.force ],
            'archive': dt.replace_date( archive.force_file, date )
            }
        sensitivity_files['emis.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.emis_sense_file, date ),
            'template': dated_vsn[ template.sense_emis ],
            'archive': dt.replace_date( archive.sens_emis_file, date )
            }
        sensitivity_files['conc.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.conc_sense_file, date ),
            'template': dated_vsn[ template.sense_conc ],
            'archive': dt.replace_date( archive.sens_conc_file, date )
            }
    return None
