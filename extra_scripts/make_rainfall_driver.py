"""
make_rainfall_driver.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

import context
import fourdvar.params.model_data as md
import fourdvar.util.file_handle as fh

def markov(nx, x0, sx, tx):
    """Produce a random markov chain for rd,
    rd = rainfall driver of model
    nx: number of timesteps, int
    x0: starting value, real
    sx: standard deviation, real
    tx: timestep size, real
    """
    xx = [x0]
    aa = np.exp(-1.0/tx)
    bb = np.sqrt(1.0-aa**2)
    for i in range(nx):
        xx.append(aa*xx[-1] + bb*sx*np.random.normal())
    rd = np.exp(np.array(xx[1:]))
    return rd

rainfall_driver = markov( md.rd_sample, md.rd_f0, md.rd_stand_dev, md.rd_timestep )

fh.save_list( list(rainfall_driver), md.rd_filename )
