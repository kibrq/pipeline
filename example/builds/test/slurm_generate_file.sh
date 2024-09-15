#!/bin/bash

#SBATCH --mem=1gb
#SBATCH --output=/home/kibrq/Workspace/pipeline/example/builds/test/logs/stdout_generate_file_%a.log
#SBATCH --error=/home/kibrq/Workspace/pipeline/example/builds/test/logs/stderr_generate_file_%a.log
#SBATCH --array=1-1
#SBATCH --reservation=reservation
#SBATCH --time=0-01:00:00
#SBATCH --job-name=super_generate_file

ml R python

# Take SLURM_ARRAY_TASK_ID line from .sh script
command=$(cat /home/kibrq/Workspace/pipeline/example/builds/test/${SLURM_JOB_NAME}.sh | sed -n "${SLURM_ARRAY_TASK_ID}p")

echo "Executing ${command}"
echo "Started at $(date)"

eval ${command}

echo "Finished at $(date)"


