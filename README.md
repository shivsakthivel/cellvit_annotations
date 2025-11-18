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
