"""
application: stores data on physical space of interest
used to store prior/background, construct model input and minimizer input
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

class PhysicalData( InterfaceData ):
    """Starting point of background, link between model and unknowns
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
    spcs = None        #No. species for all data
    
    icon_archive_name = 'icon_grid.pickle'
    emis_archive_name = 'emis_grid.pickle'
    
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
        par_name = ['tsec','nstep','nlays_icon','nlays_emis','nrows','ncols','spcs']
        for p in par_name:
            msg = 'missing definition for {0}.{1}'.format( self.__class__.__name__, p )
            assert getattr( self, p ) is not None, msg
        
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
    
    def archive( self, dirname=None ):
        """
        extension: save a copy of data to archive/experiment directory
        input: string or None
        output: None

        notes: this will overwrite any clash in namespace.
        if input is None file will write to experiment directory
        else it will create dirname in experiment directory and save there.
        """
        save_path = get_archive_path()
        if dirname is not None:
            save_path = os.path.join( save_path, dirname )
        save_obj( self.icon, os.path.join( save_path, self.icon_archive_name ) )
        save_obj( self.emis, os.path.join( save_path, self.emis_archive_name ) )
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
        sdate = str( ncf.get_attr( filename, 'SDATE' ) )
        step = int( ncf.get_attr( filename, 'TSTEP' ) )
        varlist = ncf.get_attr( filename, 'VAR-LIST' )
        varlen = 16
        spcs = [varlist[i:i+varlen].strip() for i in range(0, len(varlist), varlen)]
        start_date = dt.datetime.strptime( sdate, '%Y%j' ).date()
        tsec = 3600*(step//10000) + 60*((step//100)%100) + step%100
        icon_dict = {}
        emis_dict = {}
        for spcs_name in spcs:
            icon_dict[ spcs_name ] = ncf.get_variable( filename, spcs_name, group='icon' )
            emis_dict[ spcs_name ] = ncf.get_variable( filename, spcs_name, group='emis' )
        
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
        assert estep % (daysec//tsec) == 0, 'nstep must cleanly divide into days.'
        
        #assign new param values and ensure old values are the same or None.
        end_date  = start_date + dt.timedelta( seconds=(tsec*estep - daysec) )
        bad_start = cfg.start_date is not None and cfg.start_date != start_date
        bad_end = cfg.end_date is not None and cfg.end_date != end_date
        assert not bad_start, 'cannot change start_date.'
        assert not bad_end, 'cannot change end_date.'
        cfg.start_date = start_date
        cfg.end_date = end_date
        par_name = ['tsec','nstep','nlays_icon','nlays_emis','nrows','ncols','spcs']
        par_val = [tsec, estep, ilays, elays, irows, icols, spcs]
        for name, val in zip( par_name, par_val ):
            old_val = getattr( cls, name )
            msg = 'cannot change {0}.{1}'.format( cls.__name__, name )
            assert old_val is None or old_val == val, msg
            setattr( cls, name, val )
        
        return cls( icon_dict, emis_dict )

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: PhysicalData
        
        eg: mock_phys = datadef.PhysicalData.example()
        
        notes: only used for testing.
        """
        pass
        #return cls( icon_dict, emis_dict )
        
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

