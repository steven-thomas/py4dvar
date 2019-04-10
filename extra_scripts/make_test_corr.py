
import os
import numpy as np
import gzip
import cPickle as pickle

import context
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template

print 'set up params'
nstep = 2
unc_fac = 0.02 #make uncertainty 2% of max emission value (+unit conversion)

data_path = os.path.realpath( '../cmaq_preprocess' )
eigen_vectors_fname = [ os.path.join( data_path, 'eigen_vectors_{:02}.pic.gz'.format(i+1))
                        for i in range( nstep ) ]
eigen_values_fname = [ os.path.join( data_path, 'eigen_values_{:02}.pic.gz'.format(i+1))
                        for i in range( nstep ) ]

efile = dt.replace_date( template.emis, dt.start_date )
nlay = int( ncf.get_attr( efile, 'NLAYS' ) )
nrow = int( ncf.get_attr( efile, 'NROWS' ) )
ncol = int( ncf.get_attr( efile, 'NCOLS' ) )

xcell = int( ncf.get_attr( efile, 'XCELL' ) )
ycell = int( ncf.get_attr( efile, 'YCELL' ) )
unc_val = unc_fac * ncf.get_variable( efile, 'CO2' ).max() / float(xcell*ycell)

for d in range( nstep ):
    print 'make domain uncertainties for day {:}'.format( d )
    edge = d % 2
    domain = np.zeros((nlay,nrow,ncol))
    r0,r1 = (nrow//3)+edge, (2*nrow//3)-edge
    c0,c1 = (ncol//3)+edge, (2*ncol//3)-edge
    domain[ 0, r0:r1, c0:c1 ] = unc_val
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
    with gzip.GzipFile( eigen_vectors_fname[d], 'wb' ) as f:
        pickle.dump( principal_eig_vecs, f )
    with gzip.GzipFile( eigen_values_fname[d], 'wb' ) as f:
        pickle.dump( sqrt_eig_vals, f )
