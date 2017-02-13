"""
application: format used to store data on physical space of interest
parent of PhysicalData & PhysicalAdjointData classes,
the two child classes share almost all attributes
therefore most of their code is here.
"""

import numpy as np
import datetime as dt
import os

import _get_root
from fourdvar.datadef.abstract._interface_data import InterfaceData

import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.archive_handle import get_archive_path
from fourdvar.util.file_handle import save_obj
import fourdvar.util.global_config as cfg

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( InterfaceData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    
    #add to the require set all the attributes that must be defined for an AdjointForcingData to be valid.
    require = InterfaceData.add_require( 'emis', 'icon' )
    
    #Parameters
    tsec = None        #No. seconds per timestep
    nstep = None       #No. timesteps for emis data
    nlays_icon = None  #No. layers for icon data
    nlays_emis = None  #No. layers for emis_data
    nrows = None       #No. rows for all data
    ncols = None       #No. columns for all data
    spcs = None        #list of species for all data
    icon_unc = None    #dict of icon uncertainty values
    emis_unc = None    #dict of emis uncertainty values

    #these class variables should be overloaded in children
    archive_name = 'physical_abstract_data.ncf' #default archive filename
    icon_units = 'NA' #units to attach to netCDF archive
    emis_units = 'NA'
        
    def __init__( self, icon_dict, emis_dict ):
        """
        application: create an instance of PhysicalData
        input: user-defined
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        #icon_dict: {var-name: np.array([layer, row, column])
        #emis_dict: {var-name: np.array([time, layer, row, column])
        InterfaceData.__init__( self )
        
        #params must all be set and not None (usally using cls.from_file)
        self.assert_params()
        
        assert set( icon_dict.keys() ) == set( self.spcs ), 'invalid icon spcs.'
        assert set( emis_dict.keys() ) == set( self.spcs ), 'invalid emis spcs.'
        
        self.icon = {}
        self.emis = {}
        for spcs_name in self.spcs:
            icon_data = np.array( icon_dict[ spcs_name ] )
            emis_data = np.array( emis_dict[ spcs_name ] )
            
            assert len( icon_data.shape ) == 3, 'icon dimensions invalid.'
            assert len( emis_data.shape ) == 4, 'emis dimensions invalid.'
            
            #check all dimension sizes match current parameters
            inl,inr,inc = icon_data.shape
            ent,enl,enr,enc = emis_data.shape
            assert inl == self.nlays_icon, 'icon layers invalid.'
            assert inr == self.nrows, 'icon rows invalid.'
            assert inc == self.ncols, 'icon columns invalid.'
            assert ent == self.nstep, 'emis timesteps invalid.'
            assert enl == self.nlays_emis, 'emis layers invalid.'
            assert enr == self.nrows, 'emis rows invalid.'
            assert enc == self.ncols, 'emis columns invalid.'
            
            self.icon[ spcs_name ] = icon_data
            self.emis[ spcs_name ] = emis_data
        return None
    
    def archive( self, path=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None
        output: None

        notes: this will overwrite any clash in namespace.
        if input is None file will write default archive_name.
        output is a netCDF file compatible with from_file method.
        """
        save_path = get_archive_path()
        if path is None:
            path = self.archive_name
        save_path = os.path.join( save_path, path )
        if os.path.isfile( save_path ):
            os.remove( save_path )
        #construct netCDF file
        ncf.phys_archive( self, save_path )
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        #get all data/parameters from file
        unc = lambda spc: spc + '_UNC'
        sdate = str( ncf.get_attr( filename, 'SDATE' ) )
        step = int( ncf.get_attr( filename, 'TSTEP' ) )
        start_date = dt.datetime.strptime( sdate, '%Y%j' ).date()
        tsec = 3600*(step//10000) + 60*((step//100)%100) + (step)%100
        spcs_list = ncf.get_attr( filename, 'VAR-LIST' ).split()
        unc_list = [ unc( spc ) for spc in spcs_list ]
        
        icon_dict = ncf.get_variable( filename, spcs_list, group='icon' )
        emis_dict = ncf.get_variable( filename, spcs_list, group='emis' )
        icon_unc = ncf.get_variable( filename, unc_list, group='icon' )
        emis_unc = ncf.get_variable( filename, unc_list, group='emis' )
        for spc in spcs_list:
            icon_unc[ spc ] = icon_unc.pop( unc( spc ) )
            emis_unc[ spc ] = emis_unc.pop( unc( spc ) )
        
        #ensure parameters from file are valid
        icon_shape = [ i.shape for i in icon_dict.values() ]
        emis_shape = [ e.shape for e in emis_dict.values() ]
        for ishape, eshape in zip( icon_shape[1:], emis_shape[1:] ):
            assert ishape == icon_shape[ 0 ], 'all icon spcs must have the same shape.'
            assert eshape == emis_shape[ 0 ], 'all emis spcs must have the same shape.'
        ilays, irows, icols = icon_shape[ 0 ]
        estep, elays, erows, ecols = emis_shape[ 0 ]
        assert irows == erows, 'icon & emis must match rows.'
        assert icols == ecols, 'icon & emis must match columns.'
        daysec = 24*60*60
        assert daysec % tsec == 0, 'tsec must cleanly divide a day.'
        assert (estep-1) % (daysec//tsec) == 0, 'nstep must cleanly divide into days.'
        for spc in spcs_list:
            msg = 'Uncertainty values are invalid for this data.'
            assert icon_unc[ spc ].shape == icon_dict[ spc ].shape, msg
            assert emis_unc[ spc ].shape == emis_dict[ spc ].shape, msg
            assert ( icon_unc[ spc ] > 0 ).all(), msg
            assert ( emis_unc[ spc ] > 0 ).all(), msg
        
        #assign new param values and ensure old values are the same or None.
        end_date  = start_date + dt.timedelta( seconds=(tsec*(estep-1) - daysec) )
        bad_start = cfg.start_date is not None and cfg.start_date != start_date
        bad_end = cfg.end_date is not None and cfg.end_date != end_date
        assert not bad_start, 'cannot change start_date.'
        assert not bad_end, 'cannot change end_date.'
        cfg.start_date = start_date
        cfg.end_date = end_date
        par_name = ['tsec','nstep','nlays_icon','nlays_emis',
                    'nrows','ncols','spcs','icon_unc','emis_unc']
        par_val = [tsec, estep, ilays, elays,
                   irows, icols, spcs_list, icon_unc, emis_unc]
        #list of cls variables that from_file can change
        par_mutable = ['icon_unc', 'emis_unc']
        for name, val in zip( par_name, par_val ):
            old_val = getattr( cls, name )
            if old_val is not None:
                #param already defined, ensure no clash.
                if name in par_mutable:
                    #parameter is mutable, affect applied globally
                    msg = 'Any change to PhysicalAbstractData.{} is applied globally!'.format( name )
                    logger.warn( msg )
                else:
                    msg = 'cannot change PhysicalAbstractData.{}'.format( name )
                    assert np.all( old_val == val ), msg
            #set this abstract classes attribute, not calling child!
            setattr( PhysicalAbstractData, name, val )
        
        return cls( icon_dict, emis_dict )

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: PhysicalData
        
        eg: mock_phys = datadef.PhysicalData.example()
        
        notes: only used for testing.
        must have global_config dates & PhysicalData parameters already defined.
        """
        icon_val = 0
        emis_val = 0
        
        msg = 'Must set global_config start_date & end_date.'
        assert cfg.start_date is not None and cfg.end_date is not None, msg
        #params must all be set and not None (usally using cls.from_file)
        cls.assert_params()
        
        icon_val += np.zeros((cls.nlays_icon, cls.nrows, cls.ncols))
        emis_val += np.zeros((cls.nstep, cls.nlays_emis, cls.nrows, cls.ncols))
        icon_dict = { spc: icon_val.copy() for spc in cls.spcs }
        emis_dict = { spc: emis_val.copy() for spc in cls.spcs }
        return cls( icon_dict, emis_dict )
    
    @classmethod
    def assert_params( cls ):
        """
        extension: assert that all needed physical parameters are valid.
        input: None
        output: None
        
        notes: method raises assertion error if None valued parameter is found.
        """
        par_name = ['tsec','nstep','nlays_icon','nlays_emis',
                    'nrows','ncols','spcs','icon_unc','emis_unc']
        for param in par_name:
            msg = 'missing definition for {0}.{1}'.format( cls.__name__, param )
            assert getattr( cls, param ) is not None, msg
        assert (24*60*60) % cls.tsec == 0, 'invalid step size (tsec).'
        assert (cls.nstep-1) % ( (24*60*60) // cls.tsec ) == 0, 'invalid step count (nstep).'
        return None
    
    def cleanup( self ):
        """
        application: called when physical data instance is no longer required
        input: None
        output: None
        
        eg: old_phys.cleanup()
        
        notes: called after test instance is no longer needed, used to delete files etc.
        """
        pass
        return None
