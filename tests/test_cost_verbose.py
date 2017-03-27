import os
import numpy as np
import cPickle as pickle

import _get_root
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
observed = user.get_observed()
observed.archive( 'observed.pickle' )
print 'success.'

print 'get prior in PhysicalData format'
prior_phys = user.get_background()
prior_phys.archive( 'prior.ncf' )
print 'success.'

print 'convert prior into UnknownData format'
prior_unknown = transform( prior_phys, d.UnknownData )
print 'success.'

print 'get unknowns in vector form.'
prior_vector = np.array( prior_unknown.get_vector() )
print 'success.'

print 'perturb vector to produce mock input for cost_func'
test_vector = prior_vector + np.random.normal( 0.0, 1.0, prior_vector.shape )
print 'success.'

print '\ncopy logic of least squares cost function.\n'

print 'convert input vector into UnknownData format'
unknown = d.UnknownData( test_vector )
print 'success.'

print 'convert new unknowns into PhysicalData format'
physical = transform( unknown, d.PhysicalData )
physical.archive( 'new_physical.ncf' )
print 'success.'

print 'convert physical into ModelInputData'
model_in = transform( physical, d.ModelInputData )
model_in.archive( 'forward_model_input' )
print 'success.'

print 'run forward model (get concentrations)'
model_out = transform( model_in, d.ModelOutputData )
model_out.archive( 'forward_model_output' )
print 'success.'

print 'get simulated observations from concentrations'
simulated = transform( model_out, d.ObservationData )
simulated.archive( 'simulated_observations.pickle' )
print 'success.'

print 'calculate residual of observations'
residual = d.ObservationData.get_residual( observed, simulated )
residual.archive( 'observation_residuals.pickle' )
print 'success.'

print 'weight residual by inverse error covariance'
weighted = d.ObservationData.error_weight( residual )
weighted.archive( 'weighted_residuals.pickle' )
print 'success.'

print 'calculate and record least squares cost'
cost = 0.5*np.sum( (test_vector - prior_vector)**2 )
cost += 0.5*np.sum( np.array(residual.get_vector())*np.array(weighted.get_vector()) )
print 'success. cost = {}'.format( cost )

print 'cleanup files produced by CMAQ'
cmaq.wipeout()

print 'FINISHED!'
