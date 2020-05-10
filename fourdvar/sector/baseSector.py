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
    
