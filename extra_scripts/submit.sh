#!/bin/bash

#PBS -N qsub_pert_input
#PBS -l walltime=12:00:00
#PBS -l mem=32GB
#PBS -l ncpus=16
#PBS -q express
#PBS -l wd
#PBS -l jobfs=5GB

python make_pert_input.py >& output_pert_input.txt
