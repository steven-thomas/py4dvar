#"monte carlo" test
import numpy as np

import _get_root
import fourdvar._main_driver as md
import fourdvar.user_driver as ud
import fourdvar.datadef as d
from fourdvar._transform import transform

#target = np.arange(3, dtype='float64') + 1
truth = np.random.uniform(1,5,3)
sample_size = 500
bg_sigma = 1
obs_sigma = 1

np_wiggle = lambda sig: np.random.normal(0,sig) if sig>0 else 0

bg_wiggle = lambda x: x + np_wiggle( bg_sigma )
obs_wiggle = lambda x: x + np_wiggle( obs_sigma )

true_modin = d.ModelInputData( truth )
true_modout = transform( true_modin, d.ModelOutputData )
true_obs = transform( true_modout, d.ObservationData )
true_modout.cleanup()

keyset = ['value','kind','time']
obslen = len( true_obs.dataset )
attrlist = [ true_obs.get_vector( key ) for key in keyset ]
true_arglist = []
for j in range( obslen ):
    true_arglist.append( { name: attrlist[i][j] for i,name in enumerate( keyset ) } )

passlist = []
faillist = []
startlist = []
for sample in range(sample_size):
    icon = np.array( [ bg_wiggle(x) for x in truth ] )
    md.bg_unknown = d.UnknownData( icon )
    obs_arglist = [ a.copy() for a in true_arglist ]
    for argdict in obs_arglist:
        argdict['value'] = obs_wiggle( argdict['value'] )
    md.observed = d.ObservationData( obs_arglist )
    ud.setup()
    output = ud.minim( md.cost_func, md.gradient_func, np.array( md.bg_unknown.get_vector() ) )
    ud.cleanup()
    if output[2]['warnflag'] == 0:
        passlist.append( output[0] )
        startlist.append( icon )
    else:
        icon_grad = md.gradient_func( icon )
        faillist.append( {'icon':icon, 'icongrad':icon_grad,'outval':output[0],'outgrad':output[2]['grad']} )

for f in faillist:
    print f['icon'], f['outval']
    print f['outgrad']/f['icongrad']
print '{} out of {} tests failed'.format( len(faillist), sample_size )
print 'truth       = {:}'.format(', '.join([ '{:2.5}'.format(x) for x in truth ]))
print 'mean        = {:}'.format(', '.join([ '{:2.5}'.format(x) for x in np.mean(passlist,0) ]))
print 'start mean  = {:}'.format(', '.join([ '{:2.5}'.format(x) for x in np.mean(startlist,0) ]))
print 'var         = {:}'.format(', '.join([ '{:2.5}'.format(x) for x in np.var(passlist,0) ]))
print 'start var   = {:}'.format(', '.join([ '{:2.5}'.format(x) for x in np.var(startlist,0) ]))

