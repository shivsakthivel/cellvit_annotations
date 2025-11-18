#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH -t 12:00:00
#SBATCH -p epyc
#SBATCH -J classifier_changes
#SBATCH -o /mnt/scratchc/fmlab/sakthi01/logs/classifier_changes.log
#SBATCH -e /mnt/scratchc/fmlab/sakthi01/logs/classifier_changes.error

conda run -n classifier_changes python process_changes.py \
--num_workers 4 \
--detection_dir /mnt/scratchc/fmlab/sakthi01/classifier_training_project/cellvit_pp_outputs \
--segmentation_dir /mnt/scratchc/fmlab/sakthi01/classifier_training_project/cellvit_pp_outputs \
--annotation_dir /mnt/scratchc/fmlab/sakthi01/classifier_training_project/annotations \
--output_dir /mnt/scratchc/fmlab/sakthi01/classifier_training_project/processed_annotations
