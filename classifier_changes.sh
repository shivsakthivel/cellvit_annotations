#!/bin/bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH -t 12:00:00
#SBATCH -p epyc
#SBATCH -J classifier_changes
#SBATCH -o <directory>/logs/classifier_changes.log
#SBATCH -e <directory>/logs/classifier_changes.error

conda run -n classifier_changes python process_changes.py \
--num_workers 4 \
--detection_dir <directory>/cellvit_pp_outputs \
--segmentation_dir <directory>/cellvit_pp_outputs \
--annotation_dir <directory>/annotations \
--output_dir <directory>/processed_annotations
