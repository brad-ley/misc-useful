#!/bin/bash
#PBS -l nodes=1:ppn=10
#PBS -l walltime=1:00:00
#PBS -m abe
#PBS -M bdprice@ucsb.edu
# serial job on knot
cd $PBS_O_WORKDIR

python3.7 residualDipolarSim.py 
