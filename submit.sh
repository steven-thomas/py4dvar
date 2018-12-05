#!/bin/bash

#PBS -N py4dvar
#PBS -l walltime=12:00:00
#PBS -l mem=2GB
#PBS -l ncpus=1
#PBS -q express
#PBS -l wd
#PBS -l jobfs=5GB

module use /g/data3/hh5/public/modules
module load conda/analysis27

module unload openmpi
module load openmpi

python runscript.py >& output.txt
