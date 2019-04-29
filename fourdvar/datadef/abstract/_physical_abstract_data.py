"""
application: format used to store data on physical space of interest
parent of PhysicalData & PhysicalAdjointData classes,
the two child classes share almost all attributes
therefore most of their code is here.
"""
from __future__ import absolute_import

import numpy as np
import os

from fourdvar.datadef.abstract._fourdvar_data import FourDVarData
from fourdvar.params.input_defn import inc_icon
from fourdvar.util.archive_handle import get_archive_path
import fourdvar.util.date_handle as dt
import fourdvar.util.netcdf_handle as ncf
import fourdvar.params.template_defn as template
import setup_logging

logger = setup_logging.get_logger( __file__ )

class PhysicalAbstractData( FourDVarData ):
    """Parent for PhysicalData and PhysicalAdjointData
    """
    
    #Parameters
    tstep = None              #No. seconds per timestep
    nstep = None              #No. timesteps for emis data
    nlays_emis = None         #No. layers for emis_data
    nrows = None              #No. rows for all data
    ncols = None              #No. columns for all data
    spcs = None               #list of species for all data
    eigen_values = None       #list of vectors of emis uncertainty eigen values
    eigen_vectors = None      #list of matrices of emis uncertainty eigen vectors
    nall_cells = None         #No. emis cells
    nunknowns = None          #No. unknowns
    
    if inc_icon is True:
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
        #icon_dict: {var-name: scaling_value)
        #emis_dict: {var-name: np.array([time, layer, row, column])
        
        #params must all be set and not None (usally using cls.from_file)
        self.assert_params()
        
        if inc_icon is True:
            assert set( icon_dict.keys() ) == set( self.spcs ), 'invalid icon spcs.'
            self.icon = {}
        
        assert set( emis_dict.keys() ) == set( self.spcs ), 'invalid emis spcs.'
        self.emis = {}
        
        for spcs_name in self.spcs:
            if inc_icon is True:
                icon_data = icon_dict[ spcs_name ]
                self.icon[ spcs_name ] = icon_data
            
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
                      'EDATE': np.int32( dt.replace_date('<YYYYDDD>',dt.end_date) ) }
        if all([ t==self.tstep[0] for t in self.tstep ]):
            tstep_out = self.tstep[0]
        else:
            tstep_out = [ t for t in self.tstep ]
        attr_dict[ 'TSTEP' ] = tstep_out
        var_list =''.join( [ '{:<16}'.format( s ) for s in self.spcs ] )
        attr_dict[ 'VAR-LIST' ] = var_list
        dim_dict = { 'ROW': self.nrows, 'COL': self.ncols, 'TSTEP': None }
        
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
        
        emis_dim = { 'LAY': self.nlays_emis }
        emis_var = {}
        
        for spc in self.spcs:
            emis_var[ spc ] = ( 'f4', ('TSTEP','LAY','ROW','COL'),
                                self.emis[ spc ] )
        
        #convert uncertainty data into format for netCDF storage.
        max_unk = self.nunknowns.max()
        vec_storage = np.zeros(( self.nstep, self.nall_cells, max_unk ))
        val_storage = np.zeros(( self.nstep, max_unk ))
        for i in range( self.nstep ):
            unk_len = self.nunknowns[i]
            vec_storage[ i, :, :unk_len ] = self.eigen_vectors[i][:]
            val_storage[ i, :unk_len ] = self.eigen_values[i][:]

        corr_unc_dim = { 'ALL_CELLS': self.nall_cells, 'UNKNOWNS': max_unk }
        corr_unc_var = { 'EIGEN_VECTORS': ('f4',('TSTEP','ALL_CELLS','UNKNOWNS'),
                                           vec_storage),
                         'EIGEN_VALUES': ('f4',('TSTEP','UNKNOWNS',),
                                          val_storage) }
        corr_unc_attr = { 'UNKNOWNS': [np.int32(unk) for unk in self.nunknowns] }
        
        ncf.create( parent=root, name='emis', dim=emis_dim, var=emis_var,
                    is_root=False )
        ncf.create( parent=root, name='corr_unc', attr=corr_unc_attr,
                    dim=corr_unc_dim, var=corr_unc_var, is_root=False )
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
        tstep = ncf.get_attr( filename, 'TSTEP' )
        if np.isscalar( tstep ):
            nstep = (daysec*len(dt.get_datelist())) // int(tstep)
            tstep = [ int(tstep) ] * nstep
        else:
            tstep = [ int(i) for i in tstep ]
            nstep = len( tstep )
        #day, step = int(tstep[0]), int(tstep[1])
        #tsec = daysec*day + 3600*(step//10000) + 60*((step//100)%100) + (step)%100
        spcs_list = ncf.get_attr( filename, 'VAR-LIST' ).split()
        unc_list = [ unc( spc ) for spc in spcs_list ]
        
        if inc_icon is True:
            icon_val = ncf.get_variable( filename, 'ICON-SCALE', group='icon' )
            icon_dict = { s:v for s,v in zip(spcs_list,icon_val) }
            icon_unc_val = ncf.get_variable( filename, 'ICON-UNC', group='icon' )
            icon_unc = { s:v for s,v in zip(spcs_list,icon_unc_val) }
        emis_dict = ncf.get_variable( filename, spcs_list, group='emis' )
        e_vectors = ncf.get_variable( filename, 'EIGEN_VECTORS', group='corr_unc')
        e_values = ncf.get_variable( filename, 'EIGEN_VALUES', group='corr_unc')
        nunknowns = ncf.get_attr( filename, 'UNKNOWNS', group='corr_unc' )
        nall_cells = e_vectors.shape[1]

        eigen_vectors = []
        eigen_values = []
        for i,n in enumerate( nunknowns ):
            e_vec = e_vectors[i,:,:n]
            eigen_vectors.append( e_vec )
            e_val = e_values[i,:n]
            eigen_values.append( e_val )
                        
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
            icon_lay = ncf.get_attr( template.icon, 'NLAYS' )
            sense_lay = ncf.get_attr( template.sense_conc, 'NLAYS' )
            assert icon_lay == sense_lay, 'Must get conc_sense of all icon lays.'
        
        tsec_edge = np.cumsum( [0] + tstep )
        msg = 'timestep does not fit entire model run.'
        assert tsec_edge[-1] == daysec*len(dt.get_datelist()), msg
        ind_list = [ i for i,t in enumerate(tsec_edge) if t%daysec != 0 ]
        for i in ind_list:
            t = tsec_edge[i]
            day_start = daysec * (t // daysec )
            day_end = day_start + daysec
            msg = 'sub-day timestep cannot span multiple days.'
            assert tsec_edge[i-1] >= day_start, msg
            assert tsec_edge[i+1] <= day_end, msg
        assert len(tstep) == estep, 'tstep and emis nstep do not match'

        msg = 'Uncertainty values are invalid for this data.'
        assert all([ v.shape==(l,) for v,l in zip(eigen_values,nunknowns) ]), msg
        assert nall_cells == len(spcs_list)*elays*erows*ecols, msg
        
        #assign new param values.
        par_name = ['tstep','nstep','nlays_emis','nrows','ncols','spcs',
                    'eigen_vectors', 'eigen_values', 'nall_cells', 'nunknowns']
        par_val = [tstep, estep, elays, erows, ecols, spcs_list, eigen_vectors,
                   eigen_values, nall_cells, nunknowns]
        par_mutable = ['eigen_vectors, eigen_values']
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
        icon_val = 1.0
        emis_val = 0.0
        
        #params must all be set and not None (usally using cls.from_file)
        cls.assert_params()
        
        if inc_icon is True:
            icon_dict = { spc: icon_val for spc in cls.spcs }
        else:
            icon_dict = None
        
        emis_val += np.zeros((cls.nstep, cls.nlays_emis, cls.nrows, cls.ncols))
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
        par_name = ['tstep','nstep','nlays_emis','nrows','ncols','spcs',
                    'eigen_vectors','eigen_values','nall_cells','nunknowns']
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
