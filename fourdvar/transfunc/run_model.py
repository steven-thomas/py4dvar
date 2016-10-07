
import numpy as np

import _get_root
from fourdvar.datadef import ModelInputData, ModelOutputData
from fourdvar.libshare.lorenz_63 import model
from fourdvar.util.dim_defn import x_len

def run_model( model_input ):
    #run the forward model
    assert model_input.data.shape == (x_len, ), 'invalid model input'
    out_data = model( model_input.data )
    return ModelOutputData( out_data, 'model_output.ndarray' )

