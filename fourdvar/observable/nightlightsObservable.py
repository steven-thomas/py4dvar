import baseObservable
class NightlightsObservable( baseObservable.BaseObservable):
    def __init__( self): pass
    def makePrior( self):
        self.prior = np.array([1.,2.,3.])
