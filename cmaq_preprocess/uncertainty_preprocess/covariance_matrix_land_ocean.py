import numpy as np 
from netCDF4 import Dataset
from numpy import linalg




def corr_matrix(points_list, YCELL, XCELL, L_land, L_ocean, surfzone_list):
    ncells = len(points_list)
    corr_matrix = np.zeros((ncells, ncells))
    for i in range(len(points_list)):
        for j in range(len(points_list)):
            y_dist = YCELL * abs(points_list[i][0] - points_list[j][0])
            x_dist = XCELL * abs(points_list[i][1] - points_list[j][1])
            total_dist = np.sqrt( y_dist**2 + x_dist**2 )
            if surfzone_list[i] == 1 and surfzone_list[j] == 1:
                corr_matrix[i,j] = np.exp(-total_dist/L_land)
            elif surfzone_list[i] == 0 and surfzone_list[j] == 0:
                corr_matrix[i,j] = np.exp(-total_dist/L_ocean)
            elif surfzone_list[i] != surfzone_list[j]:
		corr_matrix[i,j] = 0
    return corr_matrix    



def cov_matrix(points_list, sig, YCELL, XCELL, L_land, L_ocean, surfzone_list):
    ncells = len( points_list )
    cov = np.zeros((ncells, ncells))
    for i in range(len(points_list)):
        for j in range(len(points_list)):
            y_dist = YCELL * abs(points_list[i][0] - points_list[j][0])
            x_dist = XCELL * abs(points_list[i][1] - points_list[j][1])
            total_dist = np.sqrt( y_dist**2 + x_dist**2 )
            if surfzone_list[i] == 1 and surfzone_list[j] == 1:
                cov[i,j] = sig[i] * sig[j] * np.exp(-total_dist/L_land)
            elif surfzone_list[i] == 0 and surfzone_list[j] == 0:
                cov[i,j] = sig[i] * sig[j] * np.exp(-total_dist/L_ocean)
            elif surfzone_list[i] != surfzone_list[j]:
                cov[i,j] = sig[i] * sig[j] * 0
    return cov



#cov_matrix = cov_matrix(points_list, unc_list, YCELL, XCELL, L_land, L_ocean, surfzone_list)
#print cov_matrix
#if __name__ == '__main__':



#f = open('cov_correlation_matrix.pickle', 'w')
#pickle.dump(cov_matrix, f)
#f.close()

#OPEN CORRELATION PICKLE FORM 

#file_corr =  open('correlation_matrix.pickle', 'r')
#correlation_matrix = pickle.load(file_corr)
#file_corr.close()
#print correlation_matrix[0]
#print correlation_matrix[0].shape

# PLOT 
#plt.imshow(correlation_matrix, interpolation='nearest', cmap = 'Blues')
#plt.colorbar()
#plt.savefig('correlation_matrix_first_row.png')












































#print cov_matrix(points, sigmas, YCELL, XCELL, L)
#cov = cov_matrix(points, sigmas, YCELL, XCELL, L)

# Eigenvalues and eigenvectors from the covariance matrix                                                                     

#eig_vals, eig_vecs = np.linalg.eig(cov)

#print('Eigenvectors \n%s' %eig_vecs)                                                                                         
#print('\nEigenvalues \n%s' %eig_vals)                                                                                        

# Make a list of (eigenvalue, eigenvector) tuples                                                                             
#eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]

# sort the (eigenvalue, eigenvector) tuples from high to low                                                                  
#eig_pairs.sort()
#eig_pairs.reverse()

# Visually confirm that the list is correctly sorted by decreasing eigenvalues                                                
#print('Eigenvalues in descending order:')
#for i in eig_pairs:
#    print(i[0])

#Principal analysis Componentes (PAC)                                                                                         
#Seleccting principal Componentes (PC)                                                                                        

#total = sum(eig_vals)
#var_exp = [(i / total)*100 for i in sorted(eig_vals, reverse=True)]
#var_exp_restricted = [i for i in var_exp if i >=50. ]
#print var_exp_restricted
#print (len(var_exp_restricted))
#count = 0
#for i in var_exp:
#    if i >= 50.:
#        count += 1
#print count
    
#print var_exp
#x = [ i for i in range(len(var_exp))]
#print x
#cum_var_exp = np.cumsum(var_exp)

#plt.bar( x, var_exp)

#plt.show()
#plt.savefig('play_2.png')

