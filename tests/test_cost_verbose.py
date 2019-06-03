import os
import time
import numpy as np
import cPickle as pickle

import context
import fourdvar.user_driver as user
import fourdvar.datadef as d
from fourdvar._transform import transform
import fourdvar.util.archive_handle as archive
import fourdvar.params.archive_defn as archive_defn
import fourdvar.util.cmaq_handle as cmaq

archive_defn.experiment = 'tmp_cost_verbose'
archive_defn.desc_name = ''

archive_path = archive.get_archive_path()
print 'saving results in:\n{}'.format(archive_path)

print 'get observations in ObservationData format'
st = time.time()
observed = user.get_observed()
print 'completed in {}s'.format( int(time.time() - st) )
observed.archive( 'observed.pickle' )
print 'archived.'

print 'get prior in PhysicalData format'
st = time.time()
prior_phys = user.get_background()
print 'completed in {}s'.format( int(time.time() - st) )
prior_phys.archive( 'prior.ncf' )
print 'archived.'

print 'convert prior into UnknownData format'
st = time.time()
prior_unknown = transform( prior_phys, d.UnknownData )
print 'completed in {}s'.format( int(time.time() - st) )

print 'get unknowns in vector form.'
st = time.time()
prior_vector = prior_unknown.get_vector()
print 'completed in {}s'.format( int(time.time() - st) )

print 'perturb vector to produce mock input for cost_func'
st = time.time()
test_vector = prior_vector + np.random.normal( 0.0, 1.0, prior_vector.shape )
print 'completed in {}s'.format( int(time.time() - st) )

print '\ncopy logic of least squares cost function.\n'

print 'convert input vector into UnknownData format'
st = time.time()
unknown = d.UnknownData( test_vector )
print 'completed in {}s'.format( int(time.time() - st) )

print 'convert new unknowns into PhysicalData format'
st = time.time()
physical = transform( unknown, d.PhysicalData )
print 'completed in {}s'.format( int(time.time() - st) )
physical.archive( 'new_physical.ncf' )
print 'archived.'

print 'convert physical into ModelInputData'
st = time.time()
model_in = transform( physical, d.ModelInputData )
print 'completed in {}s'.format( int(time.time() - st) )
model_in.archive( 'forward_model_input' )
print 'archived.'

print 'run forward model (get concentrations)'
st = time.time()
model_out = transform( model_in, d.ModelOutputData )
print 'completed in {}s'.format( int(time.time() - st) )
model_out.archive( 'forward_model_output' )
print 'archived.'

print 'get simulated observations from concentrations'
st = time.time()
simulated = transform( model_out, d.ObservationData )
print 'completed in {}s'.format( int(time.time() - st) )
simulated.archive( 'simulated_observations.pickle' )
print 'archived.'

print 'calculate residual of observations'
st = time.time()
residual = d.ObservationData.get_residual( observed, simulated )
print 'completed in {}s'.format( int(time.time() - st) )
residual.archive( 'observation_residuals.pickle' )
print 'archived.'

print 'weight residual by inverse error covariance'
st = time.time()
weighted = d.ObservationData.error_weight( residual )
print 'completed in {}s'.format( int(time.time() - st) )
weighted.archive( 'weighted_residuals.pickle' )
print 'archived.'

print 'calculate and show least squares cost'
st = time.time()
cost = 0.5*np.sum( (test_vector - prior_vector)**2 )
cost += 0.5*np.sum( residual.get_vector() * weighted.get_vector() )
print 'success in {}s. cost = {}'.format( int(time.time()-st), cost )

print 'cleanup files produced by CMAQ'
cmaq.wipeout_fwd()

print 'FINISHED!'
