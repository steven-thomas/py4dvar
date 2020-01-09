#!/bin/bash

#SBATCH --partition=physical
#SBATCH --ntasks=12
#SBATCH --mail-type=END                                                                                                                                                              
#SBATCH --mail-user=yvillalobos@student.unimelb.edu.au
#SBATCH --time=0-02:00:00
#SBATCH --job-name=fourdvar_main

module purge
module load netCDF
module load netCDF-Fortran
module load OpenMPI/3.1.0-iccifort-2018.u4-GCC-8.2.0-cuda9-ucx
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/easybuild/software/netCDF/4.5.0-spartan_intel-2017.u2/lib64"


cd /home/yvillalobos/OSSEs/201509_r1/cmaq_preprocess
#module list &> modlist.txt
python make_template.py >& output_make_template.txt
