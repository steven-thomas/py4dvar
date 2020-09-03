"""
baseSector.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import numpy as np
from scipy.sparse import csr_matrix
class BaseSector( object):
    """ basic sector class:
    it's key data structures are:
      val: list of arrays of values
      unc: prior uncertainties, conformable with val
      prior: prior value for val, conformable with val
      bas: list of sparse matrices with shape=(ngrid, nval) where ngrid is number of ffdas spatial points and nval is conformable with val
           if bas[i] is None then there isn't a basis function for that state variable and it is expected to have length ngrid"""
    def __init__( self):
        self.val = []
        self.unc = []
        self.pri = []
        self.bas = []
        return
    def valFromVector( self, vector):
        """populates the val list from an input vector, returns the input vector with sum([x.len for x in self.val]) removed from front"""
        v = vector
        for i in xrange(len(self.val)): # assign and trim
            self.val[i] = v[0:self.val[i].size]
            v = np.delete(v, np.s_[0:self.val[i].size])
        return v
    

    def makeBasis( self):
        raise NotImplementedError()
        return
       
    def makePrior( self):
        raise NotImplementedError()
        return
    
    def makeGrid( self):
        raise NotImplementedError()
        return
    
