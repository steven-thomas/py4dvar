
import numpy as np

import context
import fourdvar.util.file_handle as fh
from fourdvar.params.input_defn import prior_file

params = np.array([1.,1.,0.2,0.1])
s0 = 0.01
x0 = np.array([0.,0.])
uncertainty = 0.1 * params

datalist = [ params, s0, x0, uncertainty ]
fh.save_list( datalist, prior_file )
