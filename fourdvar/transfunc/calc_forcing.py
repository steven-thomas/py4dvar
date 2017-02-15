"""
application: calculate the adjoint forcing values from the weighted residual of observations
like all transform in transfunc this is referenced from the transform function
eg: transform( observation_instance, datadef.AdjointForcingData ) == calc_forcing( observation_instance )
"""

import numpy as np

import _get_root
from fourdvar.datadef import ObservationData, AdjointForcingData, ModelOutputData
import fourdvar.libshare.obs_handle as oh

def calc_forcing( w_residual ):
    """
    application: calculate the adjoint forcing values from the weighted residual of observations
    input: ObservationData  (weighted residuals)
    output: AdjointForcingData
    """
    
    obs_by_date = oh.get_obs_by_date( w_residual )
    kwargs = AdjointForcingData.get_kwargs_dict()
    carryover = {}
    
    ymdlist = sorted( obs_by_date.keys(), reverse=True )
    for ymd in ymdlist:
        obslist = obs_by_date[ ymd ]
        spcs_dict = kwargs[ 'force.'+ymd ]
        
        for loc, tot in carryover.items():
            spc,lay,row,col = loc
            spcs_dict[spc][-2,lay,row,col] += tot
        carryover = {}
        
        for obs in obslist:
            for coord,weight in obs.weight_grid.items():
                if str( coord[0] ) == ymd:
                    conc_step,lay,row,col,spc = coord[1:]
                    w_val = obs.value * weight
                    #forcing slices are offset from conc slices
                    frc_step = conc_step - 1
                    if frc_step == -1:
                        cur_tot = carryover.get( (spc,lay,row,col), 0 )
                        carryover[ (spc,lay,row,col) ] = cur_tot + w_val
                    else:
                        spcs_dict[spc][frc_step,lay,row,col] += w_val
    return AdjointForcingData( **kwargs )
