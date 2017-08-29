
import numpy as np

import _get_root

def icon_unc( val_dict, attr_dict, **kwargs ):
    """
    Set the uncertainty for all inital concentrations (in ppm)
    """
    #use a constant uncertainty for all values
    unc_val = 1.0 #ppm
    unc_dict = { k: np.ones(v.shape)*unc_val for k,v in val_dict.items() }
    return unc_dict

def emis_unc( val_dict, attr_dict, **kwargs ):
    """
    Set the uncertainty for all emissions ( in mol/(s*m^2) )
    """
    unc_val = 1.32e-5 #mol/(s*m^2), == 3g Carbon/(day*m^2)
    unc_dict = { k: np.ones(v.shape)*unc_val for k,v in val_dict.items() }
    return unc_dict
