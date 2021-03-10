
import os
import shutil

import  pyscope.common.library_output   as library_output

class OutputController():

    archive_loc = './data/archive/'

    def __init__(self, leafopt, gap, rad, profiles, thermal, fluxes, directional):
        self.leafopt = leafopt
        self.gap = gap
        self.rad = rad
        self.profiles = profiles
        self.thermal = thermal
        self.fluxes = fluxes
        self.directional = directional
        return None
    
    def archive( self, name='save', overwrite=True ):
        archive_fname = os.path.join( self.archive_loc, name )
        if os.path.isdir( archive_fname ):
            if overwrite is True:
                print( '{:} already exists. Deleting and replacing it.'.format(archive_fname) )
                shutil.rmtree( archive_fname )
            else:
                orig_fname = archive_fname
                i = 1
                while os.path.isdir( archive_fname ):
                    archive_fname = orig_fname + '_{:04}'.format(i)
                    i += 1
                print( '{:} already exists, switching to {:}'.format(orig_fname,archive_fname) )
        library_output.write_output_list(archive_fname, self.leafopt, self.gap, self.rad, \
                                         self.profiles, self.thermal, self.fluxes, \
                                         self.directional)
        return None

    def clean_working( self ):
        for item in os.listdir( self.working_out_dir ):
            path = self.working_out_dir + '/' + item
            if os.path.isdir( path ):
                shutil.rmtree( path )
            else:
                os.remove( path )
        return None
