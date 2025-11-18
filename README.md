This document details the steps needed to run the script to amend the CellViT detection and segmentation outputs based on broadly annotated regions where the misclassifications need to be corrected.

## Set-Up
1. Navigate to a location on the cluster where you'd like to run the script
2. Clone the repository as follows:
```bash
git clone https://github.com/shivsakthivel/cellvit_annotations.git
```
3. Move the manual annotations and CellViT outputs into the directory and the resultant structure should be as follows:

📂 cellvit_annotations \

┣ 📂 annotations \
┃ ┗ 📜 wsi1_good10.geojson \
┃ ┗ 📜 wsi2_good5_ts5.geojson \
┃ ┗ ... \

┣ 📂 cellvit_pp_outputs \
┃ ┗ 📜 wsi1_cell_detection.geojson \
┃ ┗ 📜 wsi1_cells.geojson \
┃ ┗ 📜 wsi2_cell_detection.geojson \
┃ ┗ 📜 wsi2_cells.geojson \
┃ ┗ ... \

📜 classifier_changes.sh \
📜 environment.yml \
📜 process_changes.py \

## Running the Script
1. Create the conda environment as follows:
```bash
conda env create -f environment.yml
```
2. Submit the slurm script after changing all the arguments that have the placeholder <directory> to the correct folder names:
```bash
sbatch classifier_changes.sh
```

## Outputs
The script is meant to take a folder of annotations and outputs and run the annotation changes in parallel. The outputs for each WSI will be as follows and by default will save to a new directory called `processed_annotations`:

1. `<wsi_id>_annotated_nuclei.csv`: An intermediate output csv file with 4 columns, `detection_x` [The x-coordinate of the detection point], `detection_y` [The y-coordinate of the detection point], `contour` [The full segmentation contour for the matched detected nucleus] and `Classification` which is the changed classification of that nucleus using the manual annotation. All the nuclei not included in the manual annotations will still be included with their classification unchanged.
   
2. `<wsi_id>_cell_detection.geojson`: Detection geojson file

3. `<wsi_id>_cells.geojson`: Segmentation geojson file
