
import os
import sys

import _get_root
import fourdvar.util.file_handle as fh

#Settings
root_dir = '/home/563/spt563/fourdvar/cmaq_vsn1/fourdvar/data/archive'

experiment = 'example_full_test'
description = """This is a test of the system.
this should contain a description of the experiment setting
with enough detail for replication.
"""
auto_overwrite = True

#For temporary section
dir_extn = '_vsn<I>'

firstime = True
def setup():
    """
    extension: setup the archive/experiment directory.
    input: None
    output: None
    
    notes: creates an empty directory <root_dir>/<experiment> for storing data
    only functions the first time it is called. no-op otherwise.
    """
    global firstime
    global experiment
    if firstime is True:
        firstime = False
        path = os.path.join( root_dir, experiment )
        if auto_overwrite is False and os.path.isdir( path ) is True:
            #py2 & py3 have different input() func, this normalizes it
            if sys.version_info[0] == 2:
                input = raw_input
            user_ans = input( 'Experiment {} already exists. Overwrite?(y/n): '.format( experiment ) )
            if user_ans.lower()[0] != 'y':
                #print( 'program aborted to prevent overwrite.' )
                #sys.exit(1)
                #force an unused pathname
                i=1
                path += dir_extn
                while os.path.isdir( path.replace( '<I>', str(i) ) ):
                    i += 1
                experiment += dir_extn.replace( '<I>', str(i) )
                path = os.path.join( root_dir, experiment )
        fh.empty_dir( path )
        #add description to archive as text file.
        with open( os.path.join( path, 'description.txt' ), 'w' ) as desc_file:
            desc_file.write( description )
    return None

def get_archive_path():
    setup()
    return os.path.join( root_dir, experiment )
