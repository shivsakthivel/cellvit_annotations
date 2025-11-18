"""This script processes cell detection and segmentation GeoJSON files,
annotates them based on regions of interest (ROIs) from an annotation file,
and outputs new annotated GeoJSON files.
"""

# Modules to import
import json
import pandas as pd
import os
import shapely
from shapely.strtree import STRtree
import argparse
from tqdm import tqdm
import multiprocessing

parser = argparse.ArgumentParser(description = "Process and annotate cell detection and segmentation GeoJSON files.")
parser.add_argument('--num_workers', type=int, default=4, help='Number of parallel workers to use.')
parser.add_argument('--detection_dir', type=str, required=True, help='Path to the cell detection GeoJSON file.')
parser.add_argument('--segmentation_dir', type=str, required=True, help='Path to the cell segmentation GeoJSON file.')
parser.add_argument('--annotation_dir', type=str, required=True, help='Path to the annotation GeoJSON file.')
parser.add_argument('--output_dir', type=str, required=True, help='Directory to save the annotated GeoJSON files.')
args = parser.parse_args()

def process_files_star(args):
    """ Function to pass into the multiprocessor"""
    return process_files(*args)

def change_classification(current_class, label):
    """ Function to change the classifications based on the manual labels
    [Add more combinations of changes if necessary] """
    
    if label == 'good':
        return current_class
    
    elif label == 'tum_to_str':
        return 'Connective'
    
    elif label == 'tumepi_to_imm':
        return 'Inflammatory'

def process_files(detection_file, segmentation_file, annotation_file, output_dir, unique_id):
    """ Processes the files for one WSI to make the necessary changes """
    
    try:
        # Load the GeoJSON files
        with open(detection_file, "r") as f:
            detection_data = json.load(f)
        with open(segmentation_file, "r") as f:
            seg_data = json.load(f)
        with open(annotation_file, "r") as f:
            annotation_data = json.load(f)

        print(f"Processing files for ID: {unique_id}")

        # Create ROIs DataFrame
        rois = {}
        columns = ['Polygon', 'Classification']
        for i in range(len(annotation_data['features'])):
            current_tile = annotation_data['features'][i]
            polygon = shapely.Polygon(current_tile['geometry']['coordinates'][0])
            label = current_tile['properties']['classification']['name']
            rois[i] = [polygon, label]
        rois_df = pd.DataFrame.from_dict(rois, orient='index', columns=columns)

        print("Annotating nuclei based on ROIs...")

        # Build spatial index once
        polygons = rois_df['Polygon'].tolist()
        spatial_index = STRtree(polygons)

        annotated_nuclei = {}
        columns = ['detection_x', 'detection_y', 'contour', 'Classification']
        index = 0

        print("Matching detections to ROIs...")
        for i in range(len(detection_data)):
            current_points = detection_data[i]
            current_class = current_points['properties']['classification']['name']
            for j in range(len(current_points['geometry']['coordinates'])):
                current_point = current_points['geometry']['coordinates'][j]
                current_x = current_point[0]
                current_y = current_point[1]
                point = shapely.Point(current_x, current_y)
                
                # Use spatial index for fast lookup
                candidates = spatial_index.query(point)
                for candidate_idx in candidates:
                    if polygons[candidate_idx].contains(point):
                        roi_label = rois_df.iloc[candidate_idx]['Classification']
                        new_class = change_classification(current_class, roi_label)
                        annotated_nuclei[index] = [current_x, current_y, seg_data[i]['geometry']['coordinates'][j], new_class]
                        index += 1
                        break

        annotated_nuclei_df = pd.DataFrame.from_dict(annotated_nuclei, orient='index', columns=columns)

        # Save annotated nuclei to CSV
        annotated_csv = rf"{output_dir}/{unique_id}_annotated_nuclei.csv"
        annotated_nuclei_df.to_csv(annotated_csv, index=False)
        print(f"Annotated nuclei saved to: {annotated_csv}")

        # Create new detection and segmentation data with annotations
        # Group by classification
        print("Creating new annotated GeoJSON files...")
        grouped = annotated_nuclei_df.groupby('Classification')

        # Define colors for each class from original file
        colors = {'Neoplastic': [255, 0, 0],
        'Inflammatory': [34, 221, 77],
        'Connective': [35, 92, 236],
        'Dead': [254, 255, 0],
        'Epithelial': [255, 159, 68]}

        # Create new detection file (MultiPoint features)
        new_detection_data = []

        for classification, group in grouped:
            coordinates = group[['detection_x', 'detection_y']].values.tolist()
            feature = {
            "type": "Feature",
            "geometry": {
                "type": "MultiPoint",
                "coordinates": coordinates
            },
            "properties": {
                "objectType": "annotation",
                "classification": {
                    "name": classification,
                    "color": colors[classification]
                }
            }
        }
            new_detection_data.append(feature)

        # Write detection file
        output_detection = rf"{output_dir}/{unique_id}_cell_detection.geojson"
        with open(output_detection, "w") as f:
            json.dump(new_detection_data, f, indent=2)

        # Create new segmentation file (MultiPolygon features)
        new_seg_data = []

        for classification, group in grouped:
            # Wrap each contour as a polygon in the multipolygon
            coordinates = group['contour'].tolist()
            feature = {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": coordinates
            },
            "properties": {
                "objectType": "annotation",
                "classification": {
                    "name": classification,
                    "color": colors[classification]
                }
            }
        }
            new_seg_data.append(feature)

        # Write segmentation file
        output_seg = rf"{output_dir}/{unique_id}_cells.geojson"
        with open(output_seg, "w") as f:
            json.dump(new_seg_data, f, indent=2)

        print(f"Detection file saved to: {output_detection}")
        print(f"Segmentation file saved to: {output_seg}")
        print(f"Classifications found: {list(grouped.groups.keys())}")
    
    except Exception as e:
        print(f"[ERROR] Failed to process {unique_id}: {e}")

def main():
    num_workers = args.num_workers
    detection_dir = args.detection_dir
    segmentation_dir = args.segmentation_dir
    annotation_dir = args.annotation_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    detection_files = [f for f in os.listdir(detection_dir) if f.endswith('_cell_detection.geojson')]
    segmentation_files = [f for f in os.listdir(segmentation_dir) if f.endswith('_cells.geojson')]
    annotation_files = [f for f in os.listdir(annotation_dir)]

    # Prepare jobs
    jobs = []
    for det_file in detection_files:
        unique_id = det_file.split('_cell_detection.geojson')[0]
        seg_file = f"{unique_id}_cells.geojson"
        ann_file = next((ann for ann in annotation_files if ann.startswith(unique_id)), None)
        if seg_file in segmentation_files and ann_file in annotation_files:
            jobs.append((
                os.path.join(detection_dir, det_file),
                os.path.join(segmentation_dir, seg_file),
                os.path.join(annotation_dir, ann_file),
                output_dir,
                unique_id
            ))

    with multiprocessing.Pool(processes=num_workers) as pool:
        for _ in tqdm(pool.imap_unordered(process_files_star, jobs), total=len(jobs), desc="Processing files"):
            pass

if __name__ == "__main__":

    main()
    
