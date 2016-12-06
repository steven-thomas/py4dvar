"""
extension: functions used by both obs_operator and make_forcing tranforms
"""

import numpy as np

import _get_root
import fourdvar.datadef as datadef
from fourdvar.util.date_handle import replace_date
import fourdvar.util.file_handle as fh
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.global_config as global_config
import setup_logging

logger = setup_logging.get_logger( __file__ )

def get_valid_obsdata( obsmeta_path, grid_path ):
    """
    extension: get the obsmeta dict and ensure it's compatible with the grid
    input: string (path/to/obsmeta.pickle), string (path/to/template.ncf)
    output: dict OR None
    
    notes: returns the obsmeta dict IF it matches the provided grid
    if obsmeta griddata does not match it returns None instead
    """
    griddata = fh.load_obj( obsmeta_path, close=False )
    obsdata = fh.load_obj( obsmeta_path, close=True )
    
    valid = ncf.match_attr( grid_path, griddata, griddata.keys() )
    if valid is False:
        msg = '{0} incompatible with {1}.'.format( obsmeta_path, grid_path )
        logger.error( msg )
        return None
    return obsdata

def get_obs_by_date( obs_set ):
    """
    extension: get dictionary of single obs with keys YYYYMMDD
    input: ObservationData
    output: { int(YYYYMMDD) : list( SingleObs ) }
    
    notes: a SingleObs can appear in multiple different days.
    a SingleObs belongs to a day if that day appears in its weight_grid.
    Only days within the model's run are included.
    Obs with days that are outside the model are set to valid=False
    """
    valid_obs = [ o for o in obs_set.dataset if o.valid is True ]
    tag = '<YYYYMMDD>'
    valid_dates = set( replace_date(tag,d) for d in global_config.get_datelist() )
    obs_by_date = { d : [] for d in valid_dates }
    for obs in valid_obs:
        dates = set( str(coord[0]) for coord in o.weight_grid.keys() )
        if dates <= valid_dates:
            #'dates' is a subset of 'valid_dates'
            for d in dates:
                obs_by_date[ d ].append( obs )
        else:
            obs.valid = False
        
    return obs_by_date

def get_obs_spcs( obslist ):
    """
    extension: list all the spcs in a set of observations
    input: ObservationData <OR> list of ObservationSingle
    output: list of strings ( [spcs] )
    """
    
    if isinstance( obslist, datadef.ObservationData ):
        obslist = [ o for o in obslist.dataset if o.valid is True ]
    all_spcs = set()
    for obs in obslist:
        spcs = set( str( coord[-1] ) for coord in obs.weight_grid.keys() )
        all_spcs = all_spcs.union( spcs )
    return sorted( list( all_spcs ) )
