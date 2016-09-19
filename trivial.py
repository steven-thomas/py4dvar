# original code provided by Peter Rayner to describe trival model

def trivial_fwd( c0, e, deltat):
    return deltat*e.cumsum(axis=1) + c0.reshape((c0.size,1))

def trivial_bkwd( deltat, forcing):
    dc0 = forcing.sum(axis=1)
    de = deltat*forcing[:,::-1].cumsum(axis=1)[:,::-1]
    return dc0, de

def obsop( c, i):
    return c[:,i-1:i+2].mean()

def make_forcing( c, resid, obslist):
    result = zeroslike( c):
    for num, val in zip( obslist, resid):
        result[:, num-1:num+2] += val*1./c[:,num-1:num+2].size

