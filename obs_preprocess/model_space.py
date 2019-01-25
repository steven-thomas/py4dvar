
from __future__ import absolute_import

from copy import deepcopy
import datetime as dt
from netCDF4 import Dataset
import numpy as np
import pyproj

from .ray_trace import Grid
import fourdvar.params.cmaq_config as cmaq_config
import fourdvar.params.template_defn as template_defn
import fourdvar.util.date_handle as date_handle

#convert HHMMSS into sec
tosec = lambda t: 3600*(int(t)//10000) + 60*( (int(t)//100) % 100 ) + (int(t)%100)
#No.seconds in a day
daysec = tosec( 240000 )
#radius of the Earth, in meters
earth_rad = 6370000

class ModelSpace( object ):
    
    gridmeta_keys = [ 'STIME', 'TSTEP', 'GDTYP', 'P_ALP', 'P_BET', 'P_GAM',
                      'XCENT', 'YCENT', 'XORIG', 'YORIG', 'XCELL', 'YCELL',
                      'NROWS', 'NCOLS', 'NLAYS', 'VGTYP', 'VGTOP', 'VGLVLS',
                      'NVARS', 'VAR-LIST' ]
    
    @classmethod
    def create_from_fourdvar( cls ):
        sdate = date_handle.start_date
        edate = date_handle.end_date
        METCRO3D = date_handle.replace_date( cmaq_config.met_cro_3d, sdate )
        METCRO2D = cmaq_config.met_cro_2d
        CONC = template_defn.conc
        date_range = [ sdate, edate ]
        return cls( METCRO3D, METCRO2D, CONC, date_range )
    
    def __init__( self, METCRO3D, METCRO2D, CONC, date_range ):
        """
        METCRO3D = path to any single METCRO3D file
        METCRO2D = path to any single METCRO2D file
        CONC = path to any concentration file output by CMAQ
        date_range = [ start_date, end_date ] (as datetime objects)
        """
        #read netCDF files
        self.gridmeta = {}
        with Dataset( CONC, 'r' ) as f:
            for key in self.gridmeta_keys:
                self.gridmeta[ key ] = f.getncattr( key )
        with Dataset( METCRO3D, 'r' ) as f:
            zf = f.variables['ZF'][:].mean( axis=(0,2,3) )
            layer_height = np.append( np.zeros(1), zf )
        
        self.psurf_file = METCRO2D
        self.psurf_date = None
        self.psurf_arr = None
        
        #date co-ords are int YYYYMMDD format
        self.sdate = int( date_range[0].strftime('%Y%m%d') )
        self.edate = int( date_range[1].strftime('%Y%m%d') )
        
        #Only works on one type of vertical projection
        assert ( self.gridmeta[ 'VGTYP' ] == 7 ), 'Invalid VGTYP'
        
        #record dimensional data
        self.ncol = self.gridmeta[ 'NCOLS' ]
        self.nrow = self.gridmeta[ 'NROWS' ]
        self.nlay = self.gridmeta[ 'NLAYS' ]
        self.spcs = self.gridmeta[ 'VAR-LIST' ].split()
        tsec = tosec( self.gridmeta[ 'TSTEP' ] )
        assert daysec % tsec == 0, 'invalid TSTEP in {}'.format(ncf_path)
        self.nstep = ( daysec // tsec ) + 1
        self.max_height = layer_height[ self.nlay ]
        
        #construct grid for ray-tracing
        xoffset = self.gridmeta[ 'XORIG' ]
        yoffset = self.gridmeta[ 'YORIG' ]
        zoffset = 0.
        xspace = self.gridmeta[ 'XCELL' ] * np.ones( self.ncol )
        yspace = self.gridmeta[ 'YCELL' ] * np.ones( self.nrow )
        zspace = np.diff( layer_height[:self.nlay+1] )
        offset = ( xoffset, yoffset, zoffset )
        spacing = ( xspace, yspace, zspace )
        self.grid = Grid( offset, spacing )
        
        #construct projection for lat-lon conversion
        #assumes/forces use of LCC projection
        assert ( self.gridmeta[ 'GDTYP' ] == 2 ), 'Invalid GDTYP'
        alp = float( self.gridmeta[ 'P_ALP' ] )
        bet = float( self.gridmeta[ 'P_BET' ] )
        gam = float( self.gridmeta[ 'P_GAM' ] )
        ycent = float( self.gridmeta[ 'YCENT' ] )
        proj_str = '+proj=lcc +lat_1={0} +lat_2={1} +lat_0={3} +lon_0={2} +a={4} +b={4}'
        self.proj = pyproj.Proj( proj_str.format( alp, bet, gam, ycent, earth_rad ) )
        return None
    
    def valid_coord( self, coord ):
        """return True if a coord is within the grid"""
        date,step,lay,row,col,spc = coord
        if not (self.sdate <= date <= self.edate): return False
        #fourdvar doesn't allow obs at t0 (move to previous day instead)
        if not (1 <= step < self.nstep): return False
        if not (0 <= lay < self.nlay): return False
        if not (0 <= row < self.nrow): return False
        if not (0 <= col < self.ncol): return False
        if spc not in self.spcs: return False
        return True
    
    def get_step( self, (cdate, ctime) ):
        #convert ctime (HHMMSS) into timestep index
        stime = self.gridmeta[ 'STIME' ]
        tstep = self.gridmeta[ 'TSTEP' ]
        step = ( tosec(ctime) - tosec(stime) ) // tosec( tstep )
        if step <= 0:
            #move step to previous day
            cdate = int( ( dt.datetime.strptime(str(cdate),'%Y%m%d') -
                           dt.timedelta(days=1) ).strftime('%Y%m%d') )
            step = ( daysec // tosec(tstep) ) - step
        return (cdate, step)
    
    def get_step_pos( self, ctime ):
        #return ctime's position with its step (.0=start, .5=halfway, etc)
        stime = self.gridmeta[ 'STIME' ]
        tstep = self.gridmeta[ 'TSTEP' ]
        return ( float(tosec(ctime)-tosec(stime)) / tosec(tstep) ) % 1
    
    def next_step( self, (cdate, cstep) ):
        assert (0 <= cstep < self.nstep), 'invalid step'
        cstep = cstep + 1
        if cstep == self.nstep:
            cstep = 1
            cdate = int( ( dt.datetime.strptime(str(cdate),'%Y%m%d') +
                           dt.timedelta(days=1) ).strftime('%Y%m%d') )
        return (cdate, cstep)
    
    def update_psurf( self, date_int ):
        #replace the psurf array with the new file
        new_date = dt.datetime.strptime(str(date_int),'%Y%m%d')
        new_file = date_handle.replace_date( self.psurf_file, new_date )
        with Dataset( new_file, 'r' ) as f:
            self.psurf_arr = f.variables['PRSFC'][:,0,:,:]
        self.psurf_date = date_int
        return None
    
    def pressure_convert( self, obs_pressure, obs_value, target_coord ):
        #convert obs_value array into model layers using pressure values (in Pa)
        obs_p = np.array( obs_pressure )
        obs_v = np.array( obs_value )
        
        date = target_coord[0]
        time = target_coord[1]
        row = target_coord[3]
        col = target_coord[4]
        
        if date != self.psurf_date:
            self.update_psurf( date )
        vgbot = self.psurf_arr[time,row,col]
        vglvl = np.array( self.gridmeta[ 'VGLVLS' ] )
        vgtop = float( self.gridmeta[ 'VGTOP' ] )
        
        cbound = ( vglvl[::-1]*(vgbot-vgtop) + vgtop ).reshape((1,-1))
        obound = np.concatenate(( obs_p[:1],
                                  0.5*(obs_p[:-1] + obs_p[1:]),
                                  obs_p[-1:] )).reshape((-1,1))
        cbound[0,0] = min( cbound[0,0], obound[0,0] )
        obound[0,0] = min( cbound[0,0], obound[0,0] )
        cbound[0,-1] = max( cbound[0,-1], obound[-1,0] )
        obound[-1,0] = max( cbound[0,-1], obound[-1,0] )
        
        osize = np.diff( obound, axis=0 )
    
        mask = np.zeros(( obound.size-1, cbound.size-1, ))
        lower = np.maximum( mask+cbound[:,:-1], mask+obound[:-1,:] )
        upper = np.minimum( mask+cbound[:,1:], mask+obound[1:,:] )
    
        convert_matrix = np.clip( ((upper-lower) / osize), 0, None )[:,::-1]
        return np.matmul( obs_v, convert_matrix )
    
    def get_xy( self, lat, lon ):
        return self.proj( lon, lat )
    
    def get_ray_top( self, start, zenith, azimuth ):
        """get the (x,y,z) point where a ray leaves the top of the model
        start = (x,y,z) start point
        zenith = zenith angle (radians)
        azimuth = azimuth angle (angle east of north) (radians)
        
        notes: function does not care about the horizontal domain of the model
        """
        assert 0 <= zenith < (0.5*np.pi), 'invalid zenith angle (must be radians)'
        assert 0 <= azimuth <= (2*np.pi), 'invalid azimuth angle (must be radians)'
        x0,y0,z0 = start
        assert 0 <= z0 < self.max_height, 'invalid vertical start coordinate'
        v_dist = self.max_height - z0
        h_dist = v_dist * np.tan( zenith )
        xd = h_dist * np.sin( azimuth )
        yd = h_dist * np.cos( azimuth )
        top_point = ( x0+xd, y0+yd, self.max_height )
        return top_point
    
    def get_domain( self ):
        domain = deepcopy( self.gridmeta )
        domain['SDATE'] = self.sdate
        domain['EDATE'] = self.edate
        return domain
