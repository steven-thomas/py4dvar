#!/bin/bash
# """
# submit_make_template.sh
# 
# Copyright 2016 University of Melbourne.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
# """
# 
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
