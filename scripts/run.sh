#!/bin/bash
# This script is provided for users to run simulation on HPC
# Please copy it to your simulation work directory

if [[ ! -f "$1" ]]; then
  echo "Usage: $0 <hpcsim image (.sif)>"
  exit 1
fi

for dir in `pwd`/*
do
  if [[ ! -d "${dir}" ]]; then
    continue
  fi

  command="singularity run --bind ${dir}:/hpc-sim/task/ --cleanenv $1"
  sbatch --job-name=sim_$(basename ${dir}) --cpus-per-task=8 --mem-per-cpu=6G --time=12:00:00 \
         --output=%x-%j.SLURMout --error=%x-%j.SLURMerr\
         --wrap "${command}"
  echo "start job with command [${command}]"
done

