
import os

import _get_root
import fourdvar.util.file_handle as file_handle
import fourdvar.params.archive_defn as defn

import setup_logging
logger = setup_logging.get_logger( __file__ )

finished_setup = False
archive_path = ''

def setup():
    """
    extension: setup the archive/experiment directory.
    input: None
    output: None
    
    notes: creates an empty directory for storing data
    """
    global finished_setup
    global archive_path
    if finished_setup is True:
        logger.warn( 'archive setup called again. Ignoring' )
        return None
    path = os.path.join( defn.archive_path, defn.experiment )
    if os.path.isdir( path ) is True:
        logger.warn( '{} already exists.'.format( path ) )
        if (defn.overwrite is False):
            #need to generate new archive path name
            extn = defn.extension
            if '<E>' not in extn:
                extn = '<E>' + extn
            if '<I>' not in extn:
                extn = extn + '<I>'
            template = extn.replace( '<E>', defn.experiment )
            i = 1
            unique = False
            while unique is False:
                path = os.path.join( defn.archive_path, template.replace('<I>',str(i)) )
                unique = not os.path.isdir( path )
                i += 1
            logger.warn( 'moved archive to {}'.format( path ) )
        else:
            logger.warn( 'deleted old archive.' )
    archive_path = path
    file_handle.empty_dir( archive_path )
    if defn.desc_name != '':
        #add description to archive as text file.
        with open( os.path.join( archive_path, defn.desc_name ), 'w' ) as desc_file:
            desc_file.write( defn.description )
    finished_setup = True
    
def get_archive_path():
    global archive_path
    global finished_setup
    if finished_setup is False:
        setup()
    return archive_path
