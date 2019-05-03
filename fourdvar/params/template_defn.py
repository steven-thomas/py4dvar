
import os
from fourdvar.params.root_path_defn import store_path

template_path = os.path.join( store_path, 'templates/CO_CO2_dir' )

#filepaths to template netCDF files used by CMAQ & fourdvar
conc = os.path.join( template_path, 'conc_template.ncf' )
force = os.path.join( template_path, 'force_template.ncf' )
sense_emis = os.path.join( template_path, 'sense_emis_template.ncf' )
sense_conc = os.path.join( template_path, 'sense_conc_template.ncf' )

#fwd model inputs are "records" instead of templates.
emis = os.path.join( template_path, 'record', 'emis_record_<YYYYMMDD>.ncf' )
icon = os.path.join( template_path, 'record', 'icon_record.ncf' )
