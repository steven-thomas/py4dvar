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
#PBS -N py4dvar_test
#PBS -l walltime=12:00:00
#PBS -l mem=2GB
#PBS -l ncpus=1
#PBS -q express
#PBS -l wd
#PBS -l jobfs=5GB

module use /g/data3/hh5/public/modules
module load conda/analysis27

python test_grad_verbose.py >& output_grad_verbose.txt
