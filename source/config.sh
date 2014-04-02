#!/bin/bash

mkdir -p ../Output

#PBS -l arch=x86_64
#PBS -l ncpus=1
#PBS -m ea
#PBS -e ../Output/1.err
#PBS -o ../Output/1.out
#PBS -M rvadlapu@sfu.ca
#PBS -l walltime=10:00:00
#PBS -l mem=6gb

python process.py ../Data/transformrules.txt ../Data/latesttestCharParts/1 ../Output/1
