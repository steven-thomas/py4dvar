"""
_physical_abstract_data.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
import fourdvar.util.netcdf_handle as ncf
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.date_handle as dt
from fourdvar.params.input_defn import inc_icon
import fourdvar.params.template_defn as template

import setup_logging
logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    
    #Parameters
    tday_emis = None   #No. seconds per timestep
    nstep_emis = None  #No. timesteps for emis data
    nlays_emis = None  #No. layers for emis_data
    nrows = None       #No. rows for all data
    ncols = None       #No. columns for all data
    spcs = None        #list of species for all data
    emis_unc = None    #dict of emis uncertainty values

    bcon_region = None #No. bcon regions
    tsec_bcon = None   #No. seconds per boundary condition timestep
    nstep_bcon = None  #No. timesteps for boundary condition data
    bcon_up_lay = None #bottom layer of upper region of boundary conditions
    bcon_unc = None    #dict of boundary condition uncertainties
    
    if inc_icon is True:
        icon_unc = None    #dict of icon uncertainty values
        #this class variable should be overloaded in children
        icon_units = 'NA'  #unit to attach to netCDF archive

    #these class variables should be overloaded in children
    archive_name = 'physical_abstract_data.ncf' #default archive filename
    emis_units = 'NA'  #unit to attach to netCDF archive
    
    def __init__( self, icon_dict, emis_dict, bcon_dict ):
        """
        application: create an instance of PhysicalData
        input: user-defined
        output: None
        
        eg: new_phys =  datadef.PhysicalData( filelist )
        """
        #icon_dict: {var-name: scaling_value}
        #emis_dict: {var-name: np.array([time, layer, row, column])}
        #bcon_dict: {var-name: np.array([time, b-region])}
        
        #params must all be set and not None (usally using cls.from_file)
        self.assert_params()
        
        if inc_icon is True:
            assert set( icon_dict.keys() ) == set( self.spcs ), 'invalid icon spcs.'
            self.icon = {}
        
        assert set( emis_dict.keys() ) == set( self.spcs ), 'invalid emis spcs.'
        assert set( bcon_dict.keys() ) == set( self.spcs ), 'invalid bcon spcs.'
        self.emis = {}
        self.bcon = {}
        
        for spcs_name in self.spcs:
            if inc_icon is True:
                icon_data = icon_dict[ spcs_name ]
                self.icon[ spcs_name ] = icon_data

            emis_data = np.array( emis_dict[ spcs_name ] )
            assert len( emis_data.shape ) == 4, 'emis dimensions invalid.'
            ent,enl,enr,enc = emis_data.shape
            assert ent == self.nstep_emis, 'emis timesteps invalid.'
            assert enl == self.nlays_emis, 'emis layers invalid.'
            assert enr == self.nrows, 'emis rows invalid.'
            assert enc == self.ncols, 'emis columns invalid.'
            
            self.emis[ spcs_name ] = emis_data

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
        
        save_path = get_archive_path()
        if path is None:
            path = self.archive_name
        save_path = os.path.join( save_path, path )
        if os.path.isfile( save_path ):
            os.remove( save_path )
        #construct netCDF file
        attr_dict = { 'SDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.start_date) ),
                      'EDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.end_date) ),
                      'VAR-LIST': ''.join( [ '{:<16}'.format( s ) for s in self.spcs ] ) }
        dim_dict = { 'ROW': self.nrows, 'COL': self.ncols }
        
        root = ncf.create( path=save_path, attr=attr_dict, dim=dim_dict,
                           is_root=True )
        
        if inc_icon is True:
            icon_dim = { 'SPC': len( self.spcs ) }
            icon_scale = np.array( [ self.icon[ s ] for s in self.spcs ] )
            icon_unc = np.array( [ self.icon_unc[ s ] for s in self.spcs ] )
            icon_var = { 'ICON-SCALE': ('f4', ('SPC',), icon_scale ),
                         'ICON-UNC': ('f4', ('SPC',), icon_unc ) }
            ncf.create( parent=root, name='icon', dim=icon_dim, var=icon_var,
                        is_root=False )

        emis_dim = { 'TSTEP': None, 'LAY': self.nlays_emis }
        emis_attr = { 'TDAY': self.tday_emis }
        emis_var = {}
        for spc in self.spcs:
            emis_var[ spc ] = ( 'f4', ('TSTEP','LAY','ROW','COL'),
                                self.emis[ spc ], )
            emis_var[ unc(spc) ] = ( 'f4', ('TSTEP','LAY','ROW','COL'),
                                     self.emis_unc[ spc ], )
        ncf.create( parent=root, name='emis', dim=emis_dim, attr=emis_attr,
                    var=emis_var, is_root=False )

        bcon_dim = { 'TSTEP': None, 'BCON': self.bcon_region }
        bcon_attr = { 'UP_LAY': np.int32( self.bcon_up_lay ),
                      'TSEC': self.tsec_bcon }
        bcon_var = {}
        for spc in self.spcs:
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
        
        #get all data/parameters from file
        sdate = str( ncf.get_attr( filename, 'SDATE' ) )
        edate = str( ncf.get_attr( filename, 'EDATE' ) )
        tday_emis = ncf.get_attr( filename, 'TDAY', group='emis' )
        spcs_list = ncf.get_attr( filename, 'VAR-LIST' ).split()
        unc_list = [ unc( spc ) for spc in spcs_list ]
        bcon_up_lay = ncf.get_attr( filename, 'UP_LAY', group='bcon' )
        tsec_bcon = ncf.get_attr( filename, 'TSEC', group='bcon' )
        
        if inc_icon is True:
            icon_val = ncf.get_variable( filename, 'ICON-SCALE', group='icon' )
            icon_dict = { s:v for s,v in zip( spcs_list, icon_val ) }
            icon_unc_val = ncf.get_variable( filename, 'ICON-UNC', group='icon' )
            icon_unc = { s:v for s,v in zip( spcs_list, icon_unc_val ) }
        emis_dict = ncf.get_variable( filename, spcs_list, group='emis' )
        emis_unc = ncf.get_variable( filename, unc_list, group='emis' )
        bcon_dict = ncf.get_variable( filename, spcs_list, group='bcon' )
        bcon_unc = ncf.get_variable( filename, unc_list, group='bcon' )
        for spc in spcs_list:
            emis_unc[ spc ] = emis_unc.pop( unc( spc ) )
            bcon_unc[ spc ] = bcon_unc.pop( unc( spc ) )
        
        #ensure parameters from file are valid
        msg = 'invalid start date'
        assert sdate == dt.replace_date( '<YYYYDDD>', dt.start_date ), msg
        msg = 'invalid end date'
        assert edate == dt.replace_date( '<YYYYDDD>', dt.end_date ), msg
        
        emis_shape = [ e.shape for e in emis_dict.values() ]
        for eshape in emis_shape[1:]:
            assert eshape == emis_shape[0], 'all emis spcs must have the same shape.'
        bcon_shape = [ b.shape for b in bcon_dict.values() ]
        for bshape in bcon_shape[1:]:
            assert bshape == bcon_shape[0], 'all bcon spcs must have the same shape.'
        estep, elays, erows, ecols = emis_shape[0]
        bstep, bregion = bcon_shape[0]
        
        if inc_icon is True:
            icon_lay = ncf.get_attr( template.icon, 'NLAYS' )
            sense_lay = ncf.get_attr( template.sense_conc, 'NLAYS' )
            assert icon_lay == sense_lay, 'Must get conc sensitivities for all layers'
        
        assert max(daysec,tsec_bcon) % min(daysec,tsec_bcon) == 0, 'tsec_bcon must be a factor or multiple of No. seconds in a day.'
        assert len(dt.get_datelist()) == tday_emis*estep, 'invalid emission tstep/tday'
        for spc in spcs_list:
            msg = 'Uncertainty values are invalid for this data.'
            if inc_icon is True:
                assert icon_unc[ spc ].shape == icon_dict[ spc ].shape, msg
                assert ( icon_unc[ spc ] > 0 ).all(), msg
            assert emis_unc[ spc ].shape == emis_dict[ spc ].shape, msg
            assert ( emis_unc[ spc ] > 0 ).all(), msg
            assert bcon_unc[ spc ].shape == bcon_dict[ spc ].shape, msg
            assert ( bcon_unc[ spc ] > 0 ).all(), msg
        
        #assign new param values.
        par_name = ['tday_emis','nstep_emis','nlays_emis','nrows','ncols','spcs',
                    'emis_unc','bcon_region','tsec_bcon','nstep_bcon',
                    'bcon_up_lay','bcon_unc']
        par_val = [tday_emis, estep, elays, erows, ecols, spcs_list,
                   emis_unc, bregion, tsec_bcon, bstep, bcon_up_lay, bcon_unc]
        par_mutable = ['emis_unc','bcon_unc']
        if inc_icon is True:
            par_name += [ 'icon_unc' ]
            par_val += [ icon_unc ]
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
                    assert np.array_equal( old_val, val ), msg
            #set this abstract classes attribute, not calling child!
            setattr( PhysicalAbstractData, name, val )
        
        if inc_icon is False:
            icon_dict = None
        return cls( icon_dict, emis_dict, bcon_dict )
    
    @classmethod
    def assert_params( cls ):
        """
        extension: assert that all needed physical parameters are valid.
        input: None
        output: None
        
        notes: method raises assertion error if None valued parameter is found.
        """
        par_name = ['tday_emis','nstep_emis','nlays_emis','nrows','ncols','spcs',
                    'emis_unc','bcon_region','tsec_bcon','nstep_bcon',
                    'bcon_up_lay','bcon_unc']
        if inc_icon is True:
            par_name += [ 'icon_unc' ]
        for param in par_name:
            msg = 'missing definition for {0}.{1}'.format( cls.__name__, param )
            assert getattr( cls, param ) is not None, msg
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
