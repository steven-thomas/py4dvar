'''Get the eigen values and eigen vectors that py4dvar needs
'''
import numpy as np 
from netCDF4 import Dataset
from scipy import linalg as scilinalg
from covariance_matrix_land_ocean import cov_matrix
from covariance_matrix_land_ocean import corr_matrix
import matplotlib.pyplot as plt
import cPickle as pickle
from gzippickle import save
import datetime
import pandas as pd
import sys


sfile = '/short/w22/yc3714/fourdvar/AUStest/CMAQ/constant/surfzone_d01.nc'
cmaq_file = '/home/563/yc3714/4DVAR/AUStest/fourdvar/data/template/conc_template.ncf'
croFile = '/short/w22/yc3714/MCIP/AUS3/2015-03-01/d01/GRIDCRO2D_test3'
ctmDir = '/short/w22/yc3714/CTM/AUS4/uncertainties'


# open conexion with croFile file and read the land water mask variable 
with Dataset(croFile, 'r') as f:
    surfzone = f.variables['LWMASK'][0,0,:,:]


#open conexion with cmaq file                                                                                                                                                   
nc = Dataset( cmaq_file, 'r')

# Get the points that are over ocean and land in CMAQ domain                                                                                  

surfzone_list = surfzone.flatten()
#print surfzone_list


# Extract input from cmaq file that are necessary to calculate the correlation                                                                                                   

YCELL = nc.YCELL/1000.
XCELL = nc.XCELL/1000.

# Getting the numbers of rows and columns of CMAQ domaul 
conc = nc.variables['CO2'][0,0,:,:]
nrows = conc.shape[0]
ncols = conc.shape[1]

# set up correlation length 
L_land = 500.
L_ocean = 1000.


#Getting the points list that function cov_matrix needs 
points_list = []
for i in range(nrows):
    for j in range(ncols):
        points_list.append((i,j))
        

doms = ['d01']

print 'define date range'

daterange = pd.date_range(start = datetime.datetime(2015, 01, 01), end = datetime.datetime(2016, 01, 01), freq='M')
#print daterange

stringdates = [d.strftime("%Y-%m-%d")for d in daterange]
#print stringdates
dates = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in stringdates]
#print dates
ndates = len(dates)
print 'dates', ndates


cov_list = []
for date in dates:
    yyymmddhh = date.strftime('%Y%m%d%H')
    yyymmdd = date.strftime('%Y-%m-%d')
    yyymmdd_dashed = date.strftime('%Y-%m-%d')
    
    for idom, dom in enumerate(doms):
        uncdir = '{}/{}/{}'.format(ctmDir, yyymmdd_dashed, dom)
        FFDASEmisUncFile = '{}/FFDAS_land_ocean_reassigned_unc_emis_{}.nc'.format(uncdir, dom)
        CableCamsEmisUncFile = '{}/cable_cams_reassigned_unc_emiss_{}.nc'.format(uncdir, dom)
        GFEDEmisEmisUncFile = '{}/GFED_reassigned_unc_emiss_{}.nc'.format(uncdir, dom)
        print FFDASEmisUncFile
        print CableCamsEmisUncFile

        # Open conexion with prior file in order to extract the uncertainties                                                                                                            
	with Dataset( FFDASEmisUncFile, 'r') as f:
    	    FFDASUnc = f.variables['CO2'][:]
    	    FFDASUnc = FFDASUnc.squeeze()
            
        with Dataset(CableCamsEmisUncFile, 'r') as f:
            CableCamsUnc = f.variables['CO2'][:]
            CableCamsUnc = CableCamsUnc.squeeze()
	
        with Dataset(GFEDEmisEmisUncFile, 'r') as f:
            GFEDUnc = f.variables['CO2'][:]
            GFEDUnc = GFEDUnc.squeeze()

        
        print 'Calculate CABLE and CAMS covariance matrix', date
        CableCams_unc_list = [ CableCamsUnc[i,j] for (i,j) in points_list]
        CableCams_cov_matrix = cov_matrix(points_list, CableCams_unc_list, YCELL, XCELL, L_land, L_ocean, surfzone_list)
        
        print 'Calculate GFED covariance matrix', date
        GFED_unc_list = [ GFEDUnc[i,j] for (i,j) in points_list]
        GFED_cov_matrix = cov_matrix(points_list,GFED_unc_list , YCELL, XCELL, L_land, L_ocean, surfzone_list)
        
        
        print 'Calculate FFDAS covariance matrix', date
        # Assume that FFDAS uncertainties are independent, so just need to use the diagonal matrix.  
        
        FFDAS_unc_flatten = FFDASUnc.flatten()
        FFDAS_unc_square = np.square(FFDAS_unc_flatten)
        FFDAS_cov_matrix = np.diag(FFDAS_unc_square)
        #print 'sum FFDAS unc', FFDAS_unc_flatten.sum()
        #print 'sum FFDAS unc square', FFDAS_cov_matrix.sum()
        
        
        print  'Adding three covariance matrices', date 

        total_covariance = FFDAS_cov_matrix + CableCams_cov_matrix + GFED_cov_matrix
        #print 'total covariance shape', total_covariance.shape
        #print 'sum total covariance', total_covariance.sum()

        
        print 'Eigenvalues and eigenvectors from the covariance matrix', date

        eig_vals, eig_vecs = scilinalg.eigh(total_covariance)
        #print('Eigenvectors \n%s' %eig_vecs)
        #print('Eigenvalues \n%s' %eig_vals)
            
        # Make a list of (eigenvalue, eigenvector) tuples
        eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]

        # sort the (eigenvalue, eigenvector) tuples from high to low
        eig_pairs.sort(key =lambda x: x[0], reverse = True)


        # Visually confirm that the list is correctly sorted by decreasing eigenvalues
        print('Eigenvalues in descending order:')
        for i in eig_pairs:
            print(i[0])

        print 'Principal component Analysis (PCA)'
        # Since we want to reduce the dimensionality of our dataset by compressing it onto a new feature subspace, we only select the subset of the eignvectors(principal components) that contains most of the information (variance).

        total = sum(eig_vals)
        var_exp = [(i / total)*100 for i in sorted(eig_vals, reverse=True)]
        #print var_exp


        cum_var_exp = np.cumsum(var_exp)
        #cum_var_exp_restricted = np.cumsum(var_exp_restricted)
        cum_var_exp_restricted = cum_var_exp[cum_var_exp <= 99.] 
        #print ('cum_variance_restricted:')
        #print cum_var_exp_restricted.shape
        print len(cum_var_exp_restricted)   

        # After determing which  are the number of eigenvalues that cotainst 99% of the variance, we need to extract that eigenvalues and the eignvector associated with those eigenvalues. 
        # we need to save them as pickle file to generate the prior file that is requiered by 4DVAR).    
        principal_eig_vals = np.array([eig_pairs[i][0] for i in range(len(cum_var_exp_restricted))])
        principal_eig_vecs = np.array([eig_pairs[i][1] for i in range(len(cum_var_exp_restricted))]).transpose()
        #print 'principal_eig_vals'
        #print principal_eig_vals
        #print principal_eig_vals.shape
            
        #print 'principal_eig_vecs'
        #print principal_eig_vecs
        #print principal_eig_vecs.shape
                                                                 
        sqrt_principal_eig_vals = np.sqrt(principal_eig_vals)
        #print ('square root of the principal eigvalues:')
        #print sqrt_principal_eig_vals


        # Saving principal components and eigvalues in pickel file

        save(sqrt_principal_eig_vals, '{}/principal_eig_vals_{}.pickle.zip'.format(uncdir, yyymmdd))
        save(principal_eig_vecs, '{}/principal_components_eig_vecs_{}.pickle.zip'.format(uncdir, yyymmdd))

        # Plotting principal components

        #x = [ i for i in range(len(var_exp_restricted))]

        #plt.bar( range(len(var_exp_restricted)), var_exp_restricted, alpha = 0.5, align = 'center',
        #label = 'Individual explained variance')
        #plt.step(range(len(var_exp_restricted)), cum_var_exp_restricted, where = 'mid', label = 'cumulative explained variance')
        #plt.xlabel('Principal components')
        #plt.ylabel('Explained variance ratio')
        #plt.legend(loc='best')
        #plt.show()
        #plt.savefig('principal_components_restricted_2.png')





