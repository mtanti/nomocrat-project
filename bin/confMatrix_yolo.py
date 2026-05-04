#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import cv2
import numpy as np
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------
# Paths
# ------------------------
pred_mask_dir = r"D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/predicted_masks_v5_yolov11n"
gt_mask_dir   = r"D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_masks_v5_checked"

# ------------------------
# Class Mapping
# ------------------------
label_map = {
    "Caption": 0,
    "Footnote": 1,
    "Formula": 2,
    "List-item": 3,
    "Page-footer": 4,
    "Page-header": 5,
    "Picture": 6,
    "Section-header": 7,
    "Table": 8,
    "Text": 9,
    "Title": 10,
    "Background": 255
}

# Define groups (excluding background)
text_based = {"List-item", "Section-header", "Text", "Title"}
non_text = {"Caption", "Footnote", "Formula", "Page-footer", "Page-header", "Picture", "Table"}

# Build numeric mapping → 2-class IDs
fine_to_coarse = {}
for name, idx in label_map.items():
    if name in text_based:
        fine_to_coarse[idx] = 0  # Text-based
    elif name in non_text:
        fine_to_coarse[idx] = 1  # Non-text
    # Background intentionally skipped

# ------------------------
# Helper to map masks
# ------------------------
def map_to_coarse(arr, mapping):
    out = np.full_like(arr, 255)  # mark background/unmapped
    for k, v in mapping.items():
        out[arr == k] = v
    return out

# ------------------------
# Collect pixels from all images
# ------------------------
all_gt, all_pred = [], []

for mask_name in os.listdir(pred_mask_dir):
    if not mask_name.lower().endswith((".png", ".jpg", ".tif")):
        continue

    pred_path = os.path.join(pred_mask_dir, mask_name)
    gt_path   = os.path.join(gt_mask_dir, mask_name)

    pred_mask = cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE)
    gt_mask   = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)

    if pred_mask is None or gt_mask is None or pred_mask.shape != gt_mask.shape:
        print(f"Skipping {mask_name} due to missing or mismatched mask.")
        continue

    gt_coarse = map_to_coarse(gt_mask, fine_to_coarse)
    pred_coarse = map_to_coarse(pred_mask, fine_to_coarse)

    # Remove background pixels (255)
    valid_mask = (gt_coarse != 255) & (pred_coarse != 255)
    all_gt.extend(gt_coarse[valid_mask].flatten())
    all_pred.extend(pred_coarse[valid_mask].flatten())

all_gt = np.array(all_gt)
all_pred = np.array(all_pred)
print(f"Total valid pixels used: {len(all_gt):,}")

# ------------------------
# Compute 2-class confusion matrix
# ------------------------
class_names = ["Text-based", "Non-text"]
cm = confusion_matrix(all_gt, all_pred, labels=[0, 1])
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
cm_norm = np.nan_to_num(cm_norm)

# ------------------------
# Plot confusion matrices
# ------------------------
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted Label")
plt.ylabel("Ground Truth Label")
plt.title("Confusion Matrix (Raw Counts) — All Pages (No Background)")
plt.tight_layout()
plt.show()

plt.figure(figsize=(6, 5))
sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted Label")
plt.ylabel("Ground Truth Label")
plt.title("Normalized Confusion Matrix — All Pages (No Background)")
plt.tight_layout()
plt.show()

# ------------------------
# Print per-class accuracy
# ------------------------
acc_per_class = cm.diagonal() / cm.sum(axis=1)
for name, acc in zip(class_names, acc_per_class):
    print(f"{name} accuracy: {acc:.3f}")

