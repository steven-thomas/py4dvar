#!/bin/bash

#SBATCH --partition=physical
#SBATCH --ntasks=12
##SBATCH --ntasks=1
#SBATCH --time=20:00:00
#SBATCH --job-name=run_p4d_test

module purge
module load netCDF
module load netCDF-Fortran
module load OpenMPI/3.1.0-iccifort-2018.u4-GCC-8.2.0-cuda9-ucx
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/easybuild/software/netCDF/4.5.0-spartan_intel-2017.u2/lib64"

python test_grad_verbose.py >& output_test_grad_verbose.txt

python pert_pert_test.py >& output_pert_pert.txt
