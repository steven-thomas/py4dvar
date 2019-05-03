"""
application: format used to store data on physical space of interest
parent of PhysicalData & PhysicalAdjointData classes,
the two child classes share almost all attributes
therefore most of their code is here.
"""

import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.date_handle as dt
from fourdvar.params.input_defn import inc_icon

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    
    #Parameters
    tsec = None          #No. seconds per timestep
    nstep = None         #No. timesteps for emis data
    nlays_emis = None    #No. layers for emis_data
    nrows = None         #No. rows for all data
    ncols = None         #No. columns for all data
    spcs_out = None      #list of species constructed by proportion
    spcs_in = None       #list of species used for proportion
    emis_unc = None      #dict of emis uncertainty values
    
    if inc_icon is True:
        nlays_icon = None  #No. layers for icon data
        spcs_icon = None   #list of species used for initial conditions
        icon_unc = None    #dict of icon uncertainty values
        #this class variable should be overloaded in children
        icon_units = 'NA'  #unit to attach to netCDF archive

    #these class variables should be overloaded in children
    archive_name = 'physical_abstract_data.ncf' #default archive filename
    emis_units = 'NA'  #unit to attach to netCDF archive
    
    def __init__( self, icon_dict, emis_dict ):
        """
        application: create an instance of PhysicalData
        input: user-defined
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        #icon_dict: {var-name: np.array([layer, row, column])
        #emis_dict: {var-name: np.array([time, layer, row, column])
        
        #params must all be set and not None (usally using cls.from_file)
        self.assert_params()
        
        if inc_icon is True:
            assert set( icon_dict.keys() ) == set( self.spcs_icon ), 'invalid icon spcs.'
            self.icon = {}
            for spcs_name in self.spcs_icon:
                icon_data = np.array( icon_dict[ spcs_name ] )
                
                assert len( icon_data.shape ) == 3, 'icon dimensions invalid.'
                inl,inr,inc = icon_data.shape
                assert inl == self.nlays_icon, 'icon layers invalid.'
                assert inr == self.nrows, 'icon rows invalid.'
                assert inc == self.ncols, 'icon columns invalid.'
                
                self.icon[ spcs_name ] = icon_data
        
        assert set( emis_dict.keys() ) == set( self.spcs_out ), 'invalid emis spcs.'
        self.emis = {}
        
        for spcs_name in self.spcs_out:
            
            emis_data = np.array( emis_dict[ spcs_name ] )
            
            assert len( emis_data.shape ) == 4, 'emis dimensions invalid.'            
            ent,enl,enr,enc = emis_data.shape
            assert ent == self.nstep, 'emis timesteps invalid.'
            assert enl == self.nlays_emis, 'emis layers invalid.'
            assert enr == self.nrows, 'emis rows invalid.'
            assert enc == self.ncols, 'emis columns invalid.'
            
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
        unc = lambda spc: spc + '_UNC'
        
        save_path = get_archive_path()
        if path is None:
            path = self.archive_name
        save_path = os.path.join( save_path, path )
        if os.path.isfile( save_path ):
            os.remove( save_path )
        #construct netCDF file
        attr_dict = { 'SDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.start_date) ),
                      'EDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.end_date) ), 
                      'TSEC': self.tsec }

        dim_dict = { 'ROW': self.nrows, 'COL': self.ncols }
        
        root = ncf.create( path=save_path, attr=attr_dict, dim=dim_dict,
                           is_root=True )
        
        if inc_icon is True:
            icon_dim = { 'LAY': self.nlays_icon }
            spcs_txt = ''.join( [ '{:<16}'.format( s ) for s in self.spcs_icon ] )
            icon_attr = { 'SPC': spcs_txt }
            icon_var = {}
            for spc in self.spcs_icon:
                icon_var[ spc ] = ( 'f4', ('LAY','ROW','COL',), self.icon[ spc ] )
                icon_var[ unc(spc) ] = ( 'f4', ('LAY','ROW','COL'),
                                         self.icon_unc[ spc ] )
        
        emis_dim = { 'LAY': self.nlays_emis, 'TSTEP': None }
        spcs_out_txt = ''.join( [ '{:<16}'.format( s ) for s in self.spcs_out ] )
        spcs_in_txt = ''.join( [ '{:<16}'.format( s ) for s in self.spcs_in ] )
        emis_attr = { 'SPC_OUT': spcs_out_txt, 'SPC_IN': spcs_in_txt }
        emis_var = {}
        
        for spc in self.spcs_out:
            emis_var[ spc ] = ( 'f4', ('TSTEP','LAY','ROW','COL'),
                                self.emis[ spc ] )
            emis_var[ unc(spc) ] = ( 'f4', ('TSTEP','LAY','ROW','COL'),
                                     self.emis_unc[ spc ] )
        
        if inc_icon is True:
            ncf.create( parent=root, name='icon', dim=icon_dim, var=icon_var,
                        attr=icon_attr, is_root=False )
        ncf.create( parent=root, name='emis', dim=emis_dim, var=emis_var,
                    attr=emis_attr, is_root=False )
        root.close()
        return None
    
    @classmethod
    def from_file( cls, filename ):
        """
        extension: create a PhysicalData instance from a file
        input: user-defined
        output: PhysicalData
        
        eg: prior_phys = datadef.PhysicalData.from_file( "saved_prior.data" )
        """
        daysec = 24*60*60
        unc = lambda spc: spc + '_UNC'
        
        #get all data/parameters from file
        sdate = str( ncf.get_attr( filename, 'SDATE' ) )
        edate = str( ncf.get_attr( filename, 'EDATE' ) )
        tsec = ncf.get_attr( filename, 'TSEC' )
        spcs_out = ncf.get_attr( filename, 'SPC_OUT', group='emis' ).split()
        spcs_in = ncf.get_attr( filename, 'SPC_IN', group='emis' ).split()
        emis_unc_list = [ unc( spc ) for spc in spcs_out ]
        
        if inc_icon is True:
            spcs_icon = ncf.get_attr( filename, 'SPC', group='icon' ).split()
            icon_unc_list = [ unc( spc ) for spc in spcs_icon ]
            icon_dict = ncf.get_variable( filename, spcs_icon, group='icon' )
            icon_unc = ncf.get_variable( filename, icon_unc_list, group='icon' )
        emis_dict = ncf.get_variable( filename, spcs_out, group='emis' )
        emis_unc = ncf.get_variable( filename, emis_unc_list, group='emis' )

        if inc_icon is True:
            for spc in spcs_icon:
                icon_unc[ spc ] = icon_unc.pop( unc( spc ) )
        
        for spc in spcs_out:
            emis_unc[ spc ] = emis_unc.pop( unc( spc ) )
        
        #ensure parameters from file are valid
        msg = 'invalid start date'
        assert sdate == dt.replace_date( '<YYYYDDD>', dt.start_date ), msg
        msg = 'invalid end date'
        assert edate == dt.replace_date( '<YYYYDDD>', dt.end_date ), msg
        
        emis_shape = [ e.shape for e in emis_dict.values() ]
        for eshape in emis_shape[1:]:
            assert eshape == emis_shape[0], 'all emis spcs must have the same shape.'
        estep, elays, erows, ecols = emis_shape[0]
        
        if inc_icon is True:
            icon_shape = [ i.shape for i in icon_dict.values() ]
            for ishape in icon_shape[1:]:
                assert ishape == icon_shape[0], 'all icon spcs must have the same shape.'
            ilays, irows, icols = icon_shape[0]
            assert irows == erows, 'icon & emis must match rows.'
            assert icols == ecols, 'icon & emis must match columns.'
        
        assert max(daysec,tsec) % min(daysec,tsec) == 0, 'tsec must be a factor or multiple of No. seconds in a day.'
        assert (tsec >= daysec) or (estep % (daysec//tsec) == 0), 'nstep must cleanly divide into days.'
        if inc_icon is True:
            msg = 'Icon uncertainty values are invalid for this data.'
            for spc in spcs_icon:
                assert icon_unc[ spc ].shape == icon_dict[ spc ].shape, msg
                assert ( icon_unc[ spc ] > 0 ).all(), msg
        for spc in spcs_out:
            msg = 'Emis uncertainty values are invalid for this data.'
            assert emis_unc[ spc ].shape == emis_dict[ spc ].shape, msg
            assert ( emis_unc[ spc ] > 0 ).all(), msg
        prop_valid = set(spcs_out).isdisjoint(set(spcs_in))
        assert prop_valid, 'spcs_out and spcs_in must be disjoint.'
        
        #assign new param values.
        par_name = ['tsec','nstep','nlays_emis','nrows','ncols','spcs_out',
                    'spcs_in','emis_unc']
        par_val = [tsec, estep, elays, erows, ecols, spcs_out, spcs_in, emis_unc]
        par_mutable = ['emis_unc']
        if inc_icon is True:
            par_name += [ 'nlays_icon', 'spcs_icon', 'icon_unc' ]
            par_val += [ ilays, spcs_icon, icon_unc ]
            par_mutable += ['icon_unc']

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
        
        if inc_icon is False:
            icon_dict = None
        return cls( icon_dict, emis_dict )

    @classmethod
    def example( cls ):
        """
        application: return a valid example with arbitrary values.
        input: None
        output: PhysicalData
        
        eg: mock_phys = datadef.PhysicalData.example()
        
        notes: only used for testing.
        must have date_handle dates & PhysicalData parameters already defined.
        """
        icon_val = 0
        emis_val = 0
        
        #params must all be set and not None (usally using cls.from_file)
        cls.assert_params()
        
        if inc_icon is True:
            icon_val += np.zeros((cls.nlays_icon, cls.nrows, cls.ncols))
            icon_dict = { spc: icon_val.copy() for spc in cls.spcs_icon }
        else:
            icon_dict = None
        
        emis_val += np.zeros((cls.nstep, cls.nlays_emis, cls.nrows, cls.ncols))
        emis_dict = { spc: emis_val.copy() for spc in cls.spcs_out }
        
        return cls( icon_dict, emis_dict )
    
    @classmethod
    def assert_params( cls ):
        """
        extension: assert that all needed physical parameters are valid.
        input: None
        output: None
        
        notes: method raises assertion error if None valued parameter is found.
        """
        par_name = ['tsec','nstep','nlays_emis','nrows','ncols','spcs_out',
                    'spcs_in','emis_unc']
        if inc_icon is True:
            par_name += [ 'nlays_icon', 'spcs_icon', 'icon_unc' ]
        for param in par_name:
            msg = 'missing definition for {0}.{1}'.format( cls.__name__, param )
            assert getattr( cls, param ) is not None, msg
        assert max(24*60*60,cls.tsec) % min(24*60*60,cls.tsec) == 0, 'invalid step size (tsec).'
        assert (cls.tsec>=24*60*60) or (cls.nstep % ((24*60*60)//cls.tsec) == 0), 'invalid step count (nstep).'
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
