#!/bin/bash

#PBS -N CMAQ4dvar
#PBS -l walltime=12:00:00
#PBS -l mem=32GB
#PBS -l ncpus=16
#PBS -q express
#PBS -l wd
#PBS -l jobfs=5GB

module load dot
module load intel-fc
module load intel-cc
module load openmpi
# include netcdf and tools to interact with it
module load netcdf
module load nco
#include setuptools for python setup
module load python/2.7.6
module use ~access/modules
module load pythonlib/netCDF4
module load pythonlib/matplotlib
module load hdf5

python test_minim.py >& test_minim_output.txt

