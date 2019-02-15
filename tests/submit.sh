#!/bin/bash

#SBATCH --partition=normal
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=16
#SBATCH --mem=32000
#SBATCH --output=p4d_test.%J.stdout.txt
#SBATCH --error=p4d_test.%J.stderr.txt
#SBATCH --time=12:00:00
#SBATCH --job-name=fourdvar_test
#SBATCH --chdir=/home/sthomas/4DVAR/py4dvar/tests

module purge
module load netCDF-Fortran/4.4.4-iomkl-2018a

python test_grad_verbose.py >& output_grad_verbose.txt
