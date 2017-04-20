
import os
import _get_root

data_root = os.path.join( '/', 'home', '563', 'spt563',
                              'fourdvar', 'cmaq_vsn1',
                              'fourdvar', 'data' )

template_root = os.path.join( data_root, 'templates' )

#filepaths to template netCDF files used by CMAQ & fourdvar
emis = os.path.join( template_root, 'emis_template.ncf' )
icon = os.path.join( template_root, 'icon_template.ncf' )
conc = os.path.join( template_root, 'conc_template.ncf' )
force = os.path.join( template_root, 'force_template.ncf' )
sense_emis = os.path.join( template_root, 'sense_emis_template.ncf' )
sense_conc = os.path.join( template_root, 'sense_conc_template.ncf' )
