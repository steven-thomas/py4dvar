"""
all_eigenvalues_eigenvecs_grouped.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np 
from netCDF4 import Dataset
from scipy import linalg as scilinalg
from covariance_matrix_land_ocean import cov_matrix
from covariance_matrix_land_ocean import corr_matrix
import matplotlib.pyplot as plt
import cPickle as pickle
from gzippickle import save
from gzippickle import load
import datetime
import pandas as pd
from scipy.linalg import block_diag
import sys

# Directory where we should find uncertainties         
ctmDir = '/short/w22/yc3714/CTM/AUS4/uncertainties'

doms = ['d01']

print 'define date range'

daterange = pd.date_range(start = datetime.datetime(2015, 01, 01), end = datetime.datetime(2015, 03, 01), freq='M')
print daterange

stringdates = [d.strftime("%Y-%m-%d")for d in daterange]
print stringdates
dates = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in stringdates]
print dates
ndates = len(dates)
print 'dates', ndates

eigen_vals_list = []
eigen_vector_list = []
for date in dates:
    yyyymmddhh = date.strftime('%Y%m%d%H')
    yyyymmdd = date.strftime('%Y-%m-%d')
    yyyymmdd_dashed = date.strftime('%Y-%m-%d')
    
    for idom, dom in enumerate(doms):
        uncdir = '{}/{}/{}'.format(ctmDir, yyyymmdd_dashed, dom)
        eig_vals_dir = '{}/principal_eig_vals_{}.pickle.zip'.format(uncdir, yyyymmdd_dashed )
        eig_vec_dir = '{}/principal_components_eig_vecs_{}.pickle.zip'.format(uncdir, yyyymmdd_dashed)
        print eig_vals_dir
        print eig_vec_dir

        #Open conexion with eigenvalues and eigenvectors                                                                                                                                                                                                                                       
        eig_vals = load(eig_vals_dir)
        eigen_vals_list.append(eig_vals)
        
        
        eig_vectors = load(eig_vec_dir)
        eigen_vector_list.append(eig_vectors)

print 'Concatenate eigen values list'
eigen_values_conc = np.concatenate(eigen_vals_list)


print 'Generate a matrix with eigen vectors in its diagonal'
block_eig_vecs = block_diag(*eigen_vector_list)


print 'Save all monthly  principal components (eigen vectors) and eigvalues in uncertainty directory'

save(eigen_values_conc, '{}/all_principal_eig_vals_2015.pickle.zip'.format(ctmDir)) 
save(block_eig_vecs, '{}/all_principal_components_eig_vecs_2015.pickle.zip'.format(ctmDir))







