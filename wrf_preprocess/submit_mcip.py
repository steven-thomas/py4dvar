#!/bin/bash

#PBS -N qsub_mcip
#PBS -l walltime=4:00:00
#PBS -l mem=2GB
#PBS -l ncpus=1
#PBS -q copyq
#PBS -l wd
#PBS -l other=mdss

#module use /g/data3/hh5/public/modules
#module load conda/analysis27

python run_mcip.py >& output.txt
