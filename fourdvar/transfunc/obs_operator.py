"""
application: simulate set of observations from output of the forward model
like all transform in transfunc this is referenced from the transform function
eg: transform( model_output_instance, datadef.ObservationData ) == obs_operator( model_output_instance )
"""

import numpy as np

from fourdvar.datadef import ModelOutputData, ObservationData
import fourdvar.util.netcdf_handle as ncf

def obs_operator( model_output ):
    """
    application: simulate set of observations from output of the forward model
    input: ModelOutputData
    output: ObservationData
    """
    
    ObservationData.assert_params()
    
    val_list = [ o for o in ObservationData.offset_term ]
    for ymd, ilist in ObservationData.ind_by_date.items():
        conc_file = model_output.file_data['conc.'+ymd]['actual']
        var_dict = ncf.get_variable( conc_file, ObservationData.spcs )
        for i in ilist:
            for coord, weight in ObservationData.weight_grid[i].items():
                if str( coord[0] ) == ymd:
                    step,lay,row,col,spc = coord[1:]
                    conc = var_dict[spc][step,lay,row,col]
                    val_list[i] += (weight * conc)
    
    return ObservationData( val_list )
