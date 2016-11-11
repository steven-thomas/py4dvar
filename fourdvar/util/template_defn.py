
import os
import _get_root

template_root = os.path.join( '/', 'home', '563', 'spt563',
                              'fourdvar', 'cmaq_vsn1',
                              'fourdvar', 'data', 'templates' )

storage = os.path.join( template_root, 'dated_versions' )

emis = os.path.join( template_root, 'emis_template.ncf' )
icon = os.path.join( template_root, 'icon_template.ncf' )
conc = os.path.join( template_root, 'conc_template.ncf' )
force = os.path.join( template_root, 'force_template.ncf' )
sense_emis = os.path.join( template_root, 'sense_emis_template.ncf' )
sense_conc = os.path.join( template_root, 'sense_conc_template.ncf' )

icon_store = os.path.join( storage, 'icon.ncf' )
dated = {
    emis: os.path.join( storage, 'emis_<YYYYMMDD>.ncf' ),
    conc: os.path.join( storage, 'conc_<YYYYMMDD>.ncf' ),
    force: os.path.join( storage, 'force_<YYYYMMDD>.ncf' ),
    sense_emis: os.path.join( storage, 'sense_emis_<YYYYMMDD>.ncf' ),
    sense_conc: os.path.join( storage, 'sense_conc_<YYYYMMDD>.ncf' )
}
