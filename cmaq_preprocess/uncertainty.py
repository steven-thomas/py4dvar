
import numpy as np

import _get_root

def icon_unc( val_dict, attr_dict, **kwargs ):
    unc_dict = { k: np.ones(v.shape) for k,v in val_dict.items() }
    return unc_dict

def emis_unc( val_dict, attr_dict, **kwargs ):
    unc_dict = { k: np.ones(v.shape) for k,v in val_dict.items() }
    return unc_dict
