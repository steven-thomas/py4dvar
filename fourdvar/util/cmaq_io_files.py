"""
cmaq_io_files.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.params.archive_defn as archive
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.input_defn as input_defn

all_files = { 'ModelInputData': {},
              'ModelOutputData': {},
              'AdjointForcingData': {},
              'SensitivityData': {} }

firsttime = True
def get_filedict( clsname ):
    """
    extension: return dictionary of files needed for data class
    input: string, name of dataclass
    output: dict, filedict has 4 keys: actual, template, archive and date
            actual: path to the file used by cmaq.
            template: path to the template file used to construct actual.
            archive: filename to use when saving an archived copy of file.
            date: date the file data is for
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
    extension: constructed the dictionary of files for the required dates
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

    if input_defn.inc_icon is True:
        raise ValueError('This build is not configured to handle ICON')
        #model_input_files['icon'] = {
        #    'actual': cmaq_config.icon_file,
        #    'template': template.icon,
        #    'archive': archive.icon_file,
        #    'date': None }

    for date in dt.get_datelist():
        
        ymd = dt.replace_date( '<YYYYMMDD>', date )
        model_input_files['emis.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.emis_file, date ),
            'template': dt.replace_date( template.emis, date ),
            'archive': dt.replace_date( archive.emis_file, date ),
            'date': date
            }
        model_output_files['conc.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.conc_file, date ),
            'template': template.conc,
            'archive': dt.replace_date( archive.conc_file, date ),
            'date': date
            }
        adjoint_forcing_files['force.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.force_file, date ),
            'template': template.force,
            'archive': dt.replace_date( archive.force_file, date ),
            'date': date
            }
        sensitivity_files['emis.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.emis_sense_file, date ),
            'template': template.sense_emis,
            'archive': dt.replace_date( archive.sens_emis_file, date ),
            'date': date
            }
        sensitivity_files['conc.'+ymd] = {
            'actual': dt.replace_date( cmaq_config.conc_sense_file, date ),
            'template': template.sense_conc,
            'archive': dt.replace_date( archive.sens_conc_file, date ),
            'date': date
            }
    return None
