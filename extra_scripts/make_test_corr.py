
import os
import numpy as np
import gzip
import cPickle as pickle

import context
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.params.cmaq_config as c

print 'set up params'
data_path = os.path.realpath( '../SHORT_LN_YC/input' )
corr_matrix_fname = os.path.join( data_path, 'tmp_corr_matrix.pic.gz') 
unc_vector_fname = os.path.join( data_path, 'tmp_unc_vector.pic.gz' )

unc_fac = 0.02 #make uncertainty 2% of max emission value (+unit conversion)

nstep = 4

efile = dt.replace_date( template.emis, dt.start_date )
nlay = int( ncf.get_attr( efile, 'NLAYS' ) )
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )

xcell = int( ncf.get_attr( efile, 'XCELL' ) )
ycell = int( ncf.get_attr( efile, 'YCELL' ) )
unc_val = unc_fac * ncf.get_variable( efile, 'CO2' ).max() / float(xcell*ycell)

print 'make domain uncertainties'
domain = np.zeros((nstep,nlay,nrow,ncol))
domain[ :, 0, (nrow//3):(2*nrow//3), (ncol//3):(2*ncol//3) ] = unc_val
d_arr = (domain**2).flatten()
print 'make reduced eigen vector & value pairs'
reduced_pairs = []
for i,v in enumerate( d_arr ):
    if abs(v) > 0:
        vec = np.zeros( len( d_arr ) )
        vec[i] = 1
        reduced_pairs.append( (abs(v),vec,) )

print 'build output'
principal_eig_vals = np.array([ p[0] for p in reduced_pairs ])
principal_eig_vecs = np.array([ p[1] for p in reduced_pairs ]).transpose()
sqrt_eig_vals = np.sqrt( principal_eig_vals )
print 'Matrix shape = {:}'.format( principal_eig_vecs.shape )
del reduced_pairs

print 'save eigen vectors and values to files'
with gzip.GzipFile( corr_matrix_fname, 'wb' ) as f:
    pickle.dump( principal_eig_vecs, f )
with gzip.GzipFile( unc_vector_fname, 'wb' ) as f:
    pickle.dump( sqrt_eig_vals, f )
