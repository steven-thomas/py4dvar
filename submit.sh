#!/bin/bash
# """
# submit.sh
# 
# Copyright 2016 University of Melbourne.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
# """
# 
#SBATCH --partition=normal
#SBATCH --exclusive
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=16
#SBATCH --mem=32000
#SBATCH --output=fourdvar.%J.stdout.txt
#SBATCH --error=fourdvar.%J.stderr.txt
#SBATCH --time=12:00:00
#SBATCH --job-name=fourdvar_main
#SBATCH --chdir=/home/sthomas/4DVAR/py4dvar

module purge
module load netCDF-Fortran/4.4.4-iomkl-2018a

python runscript.py
