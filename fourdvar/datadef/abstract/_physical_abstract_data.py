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
    tday_emis = None        #No. days per emission timestep
    nstep_emis = None       #No. timesteps for emis data
    tsec_prop = None        #No. seconds per proportional timestep
    nstep_prop = None       #No. timesteps for proportional data
    nlays_emis = None       #No. layers for emission data
    nrows = None            #No. rows for all data
    ncols = None            #No. columns for all data
    spcs_out_emis = None    #list of species with direct emissions (CO2 in mex-test)
    spcs_out_prop = None    #list of species constructed by proportion (CO in mex-test)
    spcs_in_prop = None     #list of species used for proportional emissions
    prop_unc = None         #dict of proportion uncertainty values
    emis_unc = None         #dict of direct emission uncertainty values
    cat_emis = None         #list of diurnal category names for emission data
    
    bcon_region = None      #No. bcon regions
    bcon_spcs = None        #list of species with boundary conditions
    tsec_bcon = None        #No. seconds per boundary condition timestep
    nstep_bcon = None       #No. timesteps for boundary condition data
    bcon_up_lay = None      #bottom layer of upper region of boundary conditions
    bcon_unc = None         #dict of boundary condition uncertainties
    
    if inc_icon is True:
        raise ValueError('This build is not configured to solve for inital conditions')

    #these class variables should be overloaded in children
    archive_name = 'physical_abstract_data.ncf' #default archive filename
    emis_units = 'NA'  #unit to attach to netCDF archive
    
    def __init__( self, emis_dict, prop_dict, bcon_dict ):
        """
        application: create an instance of PhysicalData
        input: user-defined
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        #prop_dict: {var-name: np.array([time, layer, row, column])
        #emis_dict: {var-name: np.array([cat, time, layer, row, column])
        
        #params must all be set and not None (usally using cls.from_file)
        self.assert_params()
        
        if inc_icon is True:
            msg = 'This build is not configured to solve for inital conditions'
            raise ValueError( msg )
        
        assert set( emis_dict.keys() ) == set( self.spcs_out_emis ), 'invalid emis spcs.'
        assert set( prop_dict.keys() ) == set( self.spcs_out_prop ), 'invalid prop spcs.'
        assert set( bcon_dict.keys() ) == set( self.bcon_spcs ), 'invalid prop spcs.'
        self.emis = {}
        self.prop = {}
        self.bcon = {}
        
        for spcs_name in self.spcs_out_emis:
            emis_data = np.array( emis_dict[ spcs_name ] )
            assert len( emis_data.shape ) == 5, 'emis dimensions invalid.'
            encat,ent,enl,enr,enc = emis_data.shape
            assert encat == len(self.cat_emis), 'emis category indices invalid.'
            assert ent == self.nstep_emis, 'emis timesteps invalid.'
            assert enl == self.nlays_emis, 'emis layers invalid.'
            assert enr == self.nrows, 'emis rows invalid.'
            assert enc == self.ncols, 'emis columns invalid.'
            
            self.emis[ spcs_name ] = emis_data
        
        for spcs_name in self.spcs_out_prop:
            prop_data = np.array( prop_dict[ spcs_name ] )            
            assert len( prop_data.shape ) == 4, 'prop dimensions invalid.'
            pnt,pnl,pnr,pnc = prop_data.shape
            assert pnt == self.nstep_prop, 'prop timesteps invalid.'
            assert pnl == self.nlays_emis, 'prop layers invalid.'
            assert pnr == self.nrows, 'prop rows invalid.'
            assert pnc == self.ncols, 'prop columns invalid.'
            
            self.prop[ spcs_name ] = prop_data

        for spcs_name in self.bcon_spcs:
            bcon_data = np.array( bcon_dict[ spcs_name ] )            
            assert len( bcon_data.shape ) == 2, 'bcon dimensions invalid.'
            bnt,bnr = bcon_data.shape
            assert bnt == self.nstep_bcon, 'bcon timesteps invalid.'
            assert bnr == self.bcon_region, 'bcon regions invalid.'
            
            self.bcon[ spcs_name ] = bcon_data

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

        if inc_icon is True:
            msg = 'This build is not configured to solve for inital conditions'
            raise ValueError( msg )
        save_path = get_archive_path()
        if path is None:
            path = self.archive_name
        save_path = os.path.join( save_path, path )
        if os.path.isfile( save_path ):
            os.remove( save_path )
        #construct netCDF file
        attr_dict = { 'SDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.start_date) ),
                      'EDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.end_date) ) }
        dim_dict = { 'LAY': self.nlays_emis, 'ROW': self.nrows, 'COL': self.ncols }
        
        root = ncf.create( path=save_path, attr=attr_dict, dim=dim_dict, is_root=True )
        
        prop_dim = { 'TSTEP': None }
        prop_attr = { 'TSEC': self.tsec_prop,
                      'OUT_SPC': ''.join( ['{:<16}'.format(s)
                                           for s in self.spcs_out_prop] ),
                      'IN_SPC': ''.join( ['{:<16}'.format(s)
                                          for s in self.spcs_in_prop] ) }
        prop_var = {}
        for spc in self.spcs_out_prop:
            prop_var[ spc ] = ( 'f4', ('TSTEP','LAY','ROW','COL',), self.prop[ spc ], )
            prop_var[ unc(spc) ] = ( 'f4', ('TSTEP','LAY','ROW','COL',),
                                     self.prop_unc[ spc ], )
        ncf.create( parent=root, name='prop', attr=prop_attr, dim = prop_dim,
                    var = prop_var, is_root=False )
        
        emis_dim = { 'TSTEP': None, 'CAT': len(self.cat_emis) }
        emis_attr = { 'TDAY': self.tday_emis,
                      'OUT_SPC': ''.join( ['{:<16}'.format(s)
                                           for s in self.spcs_out_emis ] ),
                      'CAT_NAME': ''.join( ['{:<16}'.format(c)
                                            for c in self.cat_emis ] ) }
        emis_var = {}
        for spc in self.spcs_out_emis:
            emis_var[ spc ] = ( 'f4', ('CAT','TSTEP','LAY','ROW','COL'),
                                self.emis[ spc ] )
            emis_var[ unc(spc) ] = ( 'f4', ('CAT','TSTEP','LAY','ROW','COL'),
                                     self.emis_unc[ spc ] )
        
        ncf.create( parent=root, name='emis', dim=emis_dim, var=emis_var,
                    attr=emis_attr, is_root=False )
        
        bcon_dim = { 'TSTEP': None, 'BCON': self.bcon_region }
        bcon_attr = { 'UP_LAY': np.int32( self.bcon_up_lay ),
                      'TSEC': self.tsec_bcon,
                      'OUT_SPC': ''.join( ['{:<16}'.format(s)
                                           for s in self.bcon_spcs ] ) }
        bcon_var = {}
        for spc in self.bcon_spcs:
            bcon_var[ spc ] = ( 'f4', ('TSTEP','BCON',), self.bcon[ spc ] )
            bcon_var[ unc(spc) ] = ('f4',('TSTEP','BCON',),self.bcon_unc[ spc ])
        ncf.create( parent=root, name='bcon', dim=bcon_dim, var=bcon_var,
                    attr=bcon_attr, is_root=False )
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
        
        if inc_icon is True:
            msg = 'This build is not configured to solve for inital conditions'
            raise ValueError( msg )
        
        #get all data/parameters from file
        sdate = str( ncf.get_attr( filename, 'SDATE' ) )
        edate = str( ncf.get_attr( filename, 'EDATE' ) )
        tday_emis = ncf.get_attr( filename, 'TDAY', group='emis' )
        tsec_prop = ncf.get_attr( filename, 'TSEC', group='prop' )
        spcs_out_emis = ncf.get_attr( filename, 'OUT_SPC', group='emis' ).split()
        spcs_out_prop = ncf.get_attr( filename, 'OUT_SPC', group='prop' ).split()
        spcs_in_prop = ncf.get_attr( filename, 'IN_SPC', group='prop' ).split()
        cat_emis = ncf.get_attr( filename, 'CAT_NAME', group='emis' ).split()
        emis_unc_list = [ unc( spc ) for spc in spcs_out_emis ]
        prop_unc_list = [ unc( spc ) for spc in spcs_out_prop ]
        bcon_up_lay = ncf.get_attr( filename, 'UP_LAY', group='bcon' )
        tsec_bcon = ncf.get_attr( filename, 'TSEC', group='bcon' )
        bcon_spcs = ncf.get_attr( filename, 'OUT_SPC', group='bcon' ).split()
        bcon_unc_list = [ unc( spc ) for spc in bcon_spcs ]
        
        emis_dict = ncf.get_variable( filename, spcs_out_emis, group='emis' )
        emis_unc = ncf.get_variable( filename, emis_unc_list, group='emis' )
        prop_dict = ncf.get_variable( filename, spcs_out_prop, group='prop' )
        prop_unc = ncf.get_variable( filename, prop_unc_list, group='prop' )
        bcon_dict = ncf.get_variable( filename, bcon_spcs, group='bcon' )
        bcon_unc = ncf.get_variable( filename, bcon_unc_list, group='bcon' )
        
        for spc in spcs_out_emis:
            emis_unc[ spc ] = emis_unc.pop( unc( spc ) )
        for spc in spcs_out_prop:
            prop_unc[ spc ] = prop_unc.pop( unc( spc ) )
        for spc in bcon_spcs:
            bcon_unc[ spc ] = bcon_unc.pop( unc( spc ) )
        
        #ensure parameters from file are valid
        msg = 'invalid start date'
        assert sdate == dt.replace_date( '<YYYYDDD>', dt.start_date ), msg
        msg = 'invalid end date'
        assert edate == dt.replace_date( '<YYYYDDD>', dt.end_date ), msg
        
        emis_shape = [ e.shape for e in emis_dict.values() ]
        for eshape in emis_shape[1:]:
            assert eshape == emis_shape[0], 'all emis spcs must have the same shape.'
        prop_shape = [ p.shape for p in prop_dict.values() ]
        for pshape in prop_shape[1:]:
            assert pshape == prop_shape[0], 'all prop spcs must have the same shape.'
        bcon_shape = [ b.shape for b in bcon_dict.values() ]
        for bshape in bcon_shape[1:]:
            assert bshape == bcon_shape[0], 'all bcon spcs must have the same shape.'
        ecat, estep, elays, erows, ecols = emis_shape[0]
        pstep, plays, prows, pcols = prop_shape[0]
        bstep, bregion = bcon_shape[0]
                
        assert max(daysec,tsec_prop) % min(daysec,tsec_prop) == 0, 'tsec_prop must be a factor or multiple of No. seconds in a day.'
        assert (tsec_prop >= daysec) or (pstep % (daysec//tsec_prop) == 0), 'nstep_prop must cleanly divide into days.'
        assert max(daysec,tsec_bcon) % min(daysec,tsec_bcon) == 0, 'tsec_bcon must be a factor or multiple of No. seconds in a day.'
        assert (tsec_bcon >= daysec) or (bstep % (daysec//tsec_bcon) == 0), 'nstep_bcon must cleanly divide into days.'
        assert len(dt.get_datelist()) == tday_emis*estep, 'invalid emission tstep/tday'
        valid_spcs = set(spcs_out_prop).isdisjoint(set(spcs_in_prop))
        assert valid_spcs, 'spcs_out_prop & spcs_in_prop must be disjoint.'
        valid_spcs = set(spcs_out_prop).isdisjoint(set(spcs_out_emis))
        assert valid_spcs, 'spcs_out_prop & spcs_out_emis must be disjoint.'
        
        for spc in spcs_out_emis:
            msg = 'Emis uncertainty values are invalid for this data.'
            assert emis_unc[ spc ].shape == emis_dict[ spc ].shape, msg
            assert ( emis_unc[ spc ] > 0 ).all(), msg
        for spc in spcs_out_prop:
            msg = 'Prop uncertainty values are invalid for this data.'
            assert prop_unc[ spc ].shape == prop_dict[ spc ].shape, msg
            assert ( prop_unc[ spc ] > 0 ).all(), msg
        for spc in bcon_spcs:
            msg = 'Bcon uncertainty values are invalid for this data.'
            assert bcon_unc[ spc ].shape == bcon_dict[ spc ].shape, msg
            assert ( bcon_unc[ spc ] > 0 ).all(), msg
        
        #assign new param values.
        par_name = ['tday_emis','nstep_emis','tsec_prop','nstep_prop',
                    'nlays_emis','nrows','ncols','spcs_out_emis','spcs_out_prop',
                    'spcs_in_prop','cat_emis','emis_unc','prop_unc',
                    'bcon_region','bcon_spcs','tsec_bcon','nstep_bcon',
                    'bcon_up_lay','bcon_unc']
        par_val = [ tday_emis, estep, tsec_prop, pstep,
                    elays, erows, ecols, spcs_out_emis, spcs_out_prop,
                    spcs_in_prop, cat_emis, emis_unc, prop_unc,
                    bregion, bcon_spcs, tsec_bcon, bstep,
                    bcon_up_lay, bcon_unc ]
        par_mutable = ['emis_unc','prop_unc','bcon_unc']

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
        
        return cls.create_new( emis_dict, prop_dict, bcon_dict )

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
        emis_val = 0
        prop_val = 0
        bcon_val = 0
        
        #params must all be set and not None (usally using cls.from_file)
        cls.assert_params()
        
        if inc_icon is True:
            msg = 'This build is not configured to solve for inital conditions'
            raise ValueError( msg )
        
        emis_val += np.zeros((len(cls.cat_emis), cls.nstep, cls.nlays_emis,
                              cls.nrows, cls.ncols,))
        prop_val += np.zeros((cls.nstep_prop, cls.nlays_emis,
                              cls.nrows, cls.ncols,))
        bcon_val += np.zeros((cls.nstep_bcon, cls.bcon_region,))
        emis_dict = { spc: emis_val.copy() for spc in cls.spcs_out_emis }
        prop_dict = { spc: prop_val.copy() for spc in cls.spcs_out_prop }
        bcon_dict = { spc: bcon_val.copy() for spc in cls.bcon_spcs }
        
        return cls.create_new( emis_dict, prop_dict, bcon_dict )
    
    @classmethod
    def assert_params( cls ):
        """
        extension: assert that all needed physical parameters are valid.
        input: None
        output: None
        
        notes: method raises assertion error if None valued parameter is found.
        """
        par_name = ['tday_emis','nstep_emis','tsec_prop','nstep_prop',
                    'nlays_emis','nrows','ncols','spcs_out_emis','spcs_out_prop',
                    'spcs_in_prop','cat_emis','emis_unc','prop_unc',
                    'bcon_region','bcon_spcs','tsec_bcon','nstep_bcon',
                    'bcon_up_lay','bcon_unc']
        if inc_icon is True:
            msg = 'This build is not configured to solve for inital conditions'
            raise ValueError( msg )
        for param in par_name:
            msg = 'missing definition for {0}.{1}'.format( cls.__name__, param )
            assert getattr( cls, param ) is not None, msg
        assert max(24*60*60,cls.tsec_prop) % min(24*60*60,cls.tsec_prop) == 0, 'invalid step size (tsec).'
        assert (cls.tsec_prop>=24*60*60) or (cls.nstep_prop % ((24*60*60)//cls.tsec_prop) == 0), 'invalid step count (nstep).'
        assert len(dt.get_datelist()) % cls.tday_emis == 0, 'invalid step size (tday)'
        assert cls.tday_emis*cls.nstep_emis == len(dt.get_datelist()), 'invalid step count (nstep)'
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
