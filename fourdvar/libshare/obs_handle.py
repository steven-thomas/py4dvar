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

def get_obs_by_date( obs_set ):
    """
    extension: get dictionary of single obs with keys YYYYMMDD
    input: ObservationData
    output: { str(YYYYMMDD) : list( SingleObs ) }
    
    notes: a SingleObs can appear in multiple different days.
    a SingleObs belongs to a day if that day appears in its weight_grid.
    Only days within the model's run are included.
    Obs with days that are outside the model are set to valid=False
    """
    #ensure only obs within the domain are 'valid'
    obs_set.make_valid( global_config.get_datelist() )    
    valid_obs = [ o for o in obs_set.dataset if o.valid is True ]
    obs_by_date = {}
    for obs in valid_obs:
        dates = set( str(coord[0]) for coord in obs.weight_grid.keys() )
        for d in dates:
            obs_by_date[d] = obs_by_date.get( d, [] ) + [obs]
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
