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

archive_defn.experiment = 'tmp_grad_verbose'
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

print 'perturb vector to produce mock input for gradient_func'
st = time.time()
test_vector = prior_vector + np.random.normal( 0.0, 1.0, prior_vector.shape )
print 'completed in {}s'.format( int(time.time() - st) )

print '\ncopy logic of gradient function.\n'

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

print 'calculate adjoint forcing from weighted residuals'
st = time.time()
adj_frc = transform( weighted, d.AdjointForcingData )
print 'completed in {}s'.format( int(time.time() - st) )
adj_frc.archive( 'adjoint_model_input' )
print 'archived.'

print 'run adjoint model (get sensitivities)'
st = time.time()
sensitivity = transform( adj_frc, d.SensitivityData )
print 'completed in {}s'.format( int(time.time() - st) )
sensitivity.archive( 'adjoint_model_output' )
print 'archived.'

print 'convert sensitivities into PhysicalAdjointData format'
st = time.time()
phys_sens = transform( sensitivity, d.PhysicalAdjointData )
print 'completed in {}s'.format( int(time.time() - st) )
phys_sens.archive( 'physical_sensitivity.ncf' )
print 'archived.'

print 'convert sensitivity into gradient vector'
st = time.time()
gradient = transform( phys_sens, d.UnknownData ).get_vector()
print 'completed in {}s'.format( int(time.time() - st) )

print 'calculate and record least squares cost gradient'
st = time.time()
gradient += (test_vector - prior_vector)
fname = os.path.join( archive_path, 'gradient.pickle' )
with open( fname, 'w' ) as f:
    pickle.dump( gradient, f )
print 'success in {}s. gradient saved in {}'.format( int(time.time()-st), fname )

print 'cleanup files produced by CMAQ'
cmaq.wipeout_fwd()

print 'FINISHED!'
