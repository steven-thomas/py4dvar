import baseSector
import numpy as np
class OtherSector( baseSector.BaseSector):
    def __init__( self, initval):
        baseSector.BaseSector.__init__( self)
        self.val = initval
        return
    
