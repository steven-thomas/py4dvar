#!/bin/bash

#PBS -N PyDVAR_test
#PBS -l walltime=12:00:00
#PBS -l mem=2GB
#PBS -l ncpus=1
#PBS -q express
#PBS -l wd
#PBS -l jobfs=5GB

module use /g/data3/hh5/public/modules
module load conda/analysis27

python test_grad_verbose.py >& output_grad_verbose.txt
