#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import cv2
import json
import numpy as np
import random

# Paths
json_path = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/layout_data_v3.json"
image_folder = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_orig_all"
output_image_folder = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_orig_v3"
output_mask_folder = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_masks_v3"
mapping_file = "D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/label_mapping_v3.txt"

os.makedirs(output_image_folder, exist_ok=True)
os.makedirs(output_mask_folder, exist_ok=True)

# Load JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)["data"]

# Create label-to-id mapping
label_to_id = {}
current_id = 1
for entry in data:
    for poly in entry["polygons"]:
        label = poly["label"]
        if label not in label_to_id:
            label_to_id[label] = current_id
            current_id += 1

# Save label mapping to text file
with open(mapping_file, "w", encoding="utf-8") as f:
    for label, idx in label_to_id.items():
        f.write(f"{label}: {idx}\n")

# Resize settings
target_size = (256, 256)

# Generate images and masks
for entry in data:
    fname = entry["page"]["page_fname"]
    image_path = os.path.join(image_folder, fname)

    if not os.path.exists(image_path):
        continue

    img = cv2.imread(image_path)
    if img is None:
        continue

    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for poly in entry["polygons"]:
        points = np.array([[p["x"], p["y"]] for p in poly["polygon"]], np.int32).reshape((-1, 1, 2))
        label = poly["label"]
        label_id = label_to_id[label]
        cv2.fillPoly(mask, [points], color=label_id)

    # Resize to target size
    #img_resized = cv2.resize(img, target_size)
    #mask_resized = cv2.resize(mask, target_size, interpolation=cv2.INTER_NEAREST)

    base = os.path.splitext(fname)[0]
    cv2.imwrite(f"{output_image_folder}/{base}.png", img)
    cv2.imwrite(f"{output_mask_folder}/{base}.png", mask)

print("Preprocessing done. Label mapping saved to:", mapping_file)

