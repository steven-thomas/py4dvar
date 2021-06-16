#!/bin/bash
#PBS -P w22
#PBS -q normal
#PBS -l walltime=20:00,mem=16GB
#PBS -l ncpus=16
#PBS -v NJOBS,NJOB,NEWSTART
#PBS -l wd

# USE EXAMPLE:
# qsub -v NJOBS=5,NEWSTART=0 loop_sub.sh

# load needed modules for cmaq & py4dvar
source /home/563/spt563/mods/module_p4d.sh

#
# These variables are assumed to be set:
#   NJOBS is the total number of jobs in a sequence of jobs (defaults to 1)
#   NJOB is the number of the previous job in the sequence (defaults to 0)
#   NEWSTART 1=begin with runscript, 0=begin with restart_script (defaults to 1)
#

ECHO=/bin/echo
  
if [ X$NJOBS == X ]; then
    $ECHO "NJOBS (total number of jobs in sequence) is not set - defaulting to 1"
    export NJOBS=1
fi
  
if [ X$NJOB == X ]; then
    $ECHO "NJOB (previous job number in sequence) is not set - defaulting to 0"
    export NJOB=0
fi

if [ X$NEWSTART == X ]; then
    $ECHO "NEWSTART (begin with runscript) is not set - defaulting to 1"
    export NEWSTART=1
fi

#
# Quick termination of job sequence - look for a specific file 
#  (the filename could be a qsub -v argument)
#
if [ -f STOP_SEQUENCE ]; then
    $ECHO  "Terminating sequence after $NJOB jobs"
    exit 0
fi

#
# Increment the counter to get current job number
#
NJOB=$(($NJOB+1))

#
# Are we in an incomplete job sequence - more jobs to run ?
#
if [ $NJOB -lt $NJOBS ]; then
    #
    # Now submit the next job
    # (Assumes -N option not used to change job name.)
    #
    NEXTJOB=$(($NJOB+1))
    $ECHO "Submitting job number $NEXTJOB in sequence of $NJOBS jobs"
    qsub -z -W depend=afterany:$PBS_JOBID $PBS_JOBNAME
else
    $ECHO "Running last job in sequence of $NJOBS jobs"
fi

#
# Py4dvar called here.
#
if [ $NJOB -eq 1 -a $NEWSTART -eq 1 ]; then
    # call the base run script
    python runscript.py >& output_init.txt
else
    #call the restart script
    python restart_script.py >& output_N${NJOB}.txt
fi

# If optimiser finishes, kill any future job submissions.
touch STOP_SEQUENCE
  
#
# Not expected to reach this point in general but if we do, check that all 
# is OK.  If the job command exited with an error, terminate the job
#
errstat=$?
if [ $errstat -ne 0 ]; then
    # A brief nap so PBS kills us in normal termination. Prefer to 
    # be killed by PBS if PBS detected some resource excess
    sleep 5  
    $ECHO "Job number $NJOB returned an error status $errstat - stopping job sequence."
    touch STOP_SEQUENCE
    exit $errstat
fi
