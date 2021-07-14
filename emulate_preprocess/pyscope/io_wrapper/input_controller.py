
import os
import shutil

class InputController():
    def __init__( self, config, src_path='.' ):
        self.config = config

        print( src_path )

        #define source files
        self.source_atmofile = os.path.join( src_path, 'data/input/radiationdata/FLEX-S3_std.atm' )
        self.source_anglesfile = os.path.join( src_path, 'data/input/directional/brdf_angles2.dat' )
        self.source_optifile = os.path.join( src_path, 'data/input/fluspect_parameters/Optipar_fluspect_2014.txt' )
        self.source_soil_file = os.path.join( src_path, 'data/input/soil_spectrum/soilnew.txt' )

        self.source_input_path = os.path.join( src_path, 'data/input/' )
        self.source_Dataset_dir     = "for_verification"
        self.source_t_file          = "t_.dat"
        self.source_year_file       = "year_.dat"
        self.source_Rin_file        = "Rin_.dat"
        self.source_Rli_file        = "Rli_.dat"
        self.source_p_file          = "p_.dat"
        self.source_Ta_file         = "Ta_.dat"
        self.source_ea_file         = "ea_.dat"
        self.source_u_file          = "u_.dat"

        # Optional (leave as None for constant values)
        self.source_CO2_file        = None
        self.source_z_file          = None
        self.source_tts_file        = None

        # Optional two column tables (first column DOY second column value)
        self.source_LAI_file        = None
        self.source_hc_file         = None
        self.source_SMC_file        = None
        self.source_Vcmax_file      = None
        self.source_Cab_file        = None

        #update config paths to point to src_path
        def move_src( fname ):
            if fname.startswith('./'):
                return src_path + fname[1:]
        self.config.atmo.atmofile = move_src(self.config.atmo.atmofile)
        self.config.directional.anglesfile = move_src(self.config.directional.anglesfile)
        self.config.optipar.optifile = move_src(self.config.optipar.optifile)
        self.config.soil.soil_file = move_src(self.config.soil.soil_file)
        self.config.paths.input = move_src(self.config.paths.input)
        
        return None

    def _input_copy( self, src_fname, dst_fname ):
        """copy file to tmp input location. Create needed directories if inside
        config input path"""
        dst_loc = os.path.dirname( dst_fname )
        if (not os.path.isdir(dst_loc) and
            dst_loc.startswith(self.config.paths.input)):
            dlist = dst_loc[len(self.config.paths.input):].split('/')
            cur_dir = self.config.paths.input
            for dname in dlist:
                cur_dir = os.path.join( cur_dir, dname )
                if not os.path.isdir(cur_dir):
                    os.mkdir( cur_dir )
        shutil.copyfile( src_fname, dst_fname )
        return None

    def setup_new_run( self, src_path=None ):

        print( 'setting up new scope run.' )
        
        #overwite working directory files with source files
        self._input_copy( self.source_atmofile, self.config.atmo.atmofile )
        self._input_copy( self.source_anglesfile, self.config.directional.anglesfile )
        self._input_copy( self.source_optifile, self.config.optipar.optifile )
        self._input_copy( self.source_soil_file, self.config.soil.soil_file )

        xyt = self.config.xyt
        source_data_dir = self.source_input_path + 'dataset ' + self.source_Dataset_dir
        # Data direction location (copied from config.py)
        working_data_dir = os.path.join( self.config.paths.input,
                                         'dataset ' + xyt.Dataset_dir )

        self._input_copy( source_data_dir + '/' + self.source_t_file,
                         working_data_dir + '/' + xyt.t_file )
        self._input_copy( source_data_dir + '/' + self.source_year_file,
                         working_data_dir + '/' + xyt.year_file )
        self._input_copy( source_data_dir + '/' + self.source_Rin_file,
                         working_data_dir + '/' + xyt.Rin_file )
        self._input_copy( source_data_dir + '/' + self.source_Rli_file,
                         working_data_dir + '/' + xyt.Rli_file )
        self._input_copy( source_data_dir + '/' + self.source_p_file,
                         working_data_dir + '/' + xyt.p_file )
        self._input_copy( source_data_dir + '/' + self.source_Ta_file,
                         working_data_dir + '/' + xyt.Ta_file )
        self._input_copy( source_data_dir + '/' + self.source_ea_file,
                         working_data_dir + '/' + xyt.ea_file )
        self._input_copy( source_data_dir + '/' + self.source_u_file,
                         working_data_dir + '/' + xyt.u_file )

        #each of these files may be 'None'
        if self.source_CO2_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_CO2_file,
                             working_data_dir + '/' + xyt.CO2_file )
        if self.source_z_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_z_file,
                             working_data_dir + '/' + xyt.z_file )
        if self.source_tts_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_tts_file,
                             working_data_dir + '/' + xyt.tts_file )
        if self.source_LAI_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_LAI_file,
                             working_data_dir + '/' + xyt.LAI_file )
        if self.source_hc_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_hc_file,
                             working_data_dir + '/' + xyt.hc_file )
        if self.source_SMC_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_SMC_file,
                             working_data_dir + '/' + xyt.SMC_file )
        if self.source_Vcmax_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_Vcmax_file,
                             working_data_dir + '/' + xyt.Vcmax_file )
        if self.source_Cab_file is not None:
            self._input_copy( source_data_dir + '/' + self.source_Cab_file,
                             working_data_dir + '/' + xyt.Cab_file )
        return None
