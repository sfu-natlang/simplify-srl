#!/bin/bash
#PBS -l arch=x86_64
#PBS -l ncpus=1
#PBS -m ea
#PBS -e /cs/natlang-user/ravikiran/Projects/TimeLine/Error
#PBS -o /cs/natlang-user/ravikiran/Projects/TimeLine/Output
#PBS -M rvadlapu@sfu.ca
#PBS -l walltime=00:15:00
#PBS -l mem=12gb

#cd /cs/natlang-user/ravikiran/Projects/TimeLine/experiments/classification/source

time python process.py ../Data/transformrules.txt cases/29 o > er
