#!/bin/bash

#PBS -N qsub_make_prior
#PBS -l walltime=01:00:00
#PBS -l mem=32GB
#PBS -l ncpus=16
#PBS -q express
#PBS -l wd
#PBS -l jobfs=5GB

module use /g/data3/hh5/public/modules
module load conda/analysis27

module unload openmpi
module load openmpi

python make_prior.py >& output_make_prior.txt
