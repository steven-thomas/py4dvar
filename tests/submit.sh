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
#PBS -P q90
#PBS -q normal
#PBS -N run_test
#PBS -l walltime=20:00,mem=16GB
#PBS -l ncpus=16
#PBS -l wd

source /home/563/spt563/mods/module_p4d.sh

python3 pert_pert_test.py >& output_pert_pert.txt
