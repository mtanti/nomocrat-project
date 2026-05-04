#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

# ------------------------
# Paths
# ------------------------
pred_mask_dir = r"D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/predicted_masks_v5_yolov11n"
gt_mask_dir   = r"D:/Emma_Fenech_RSO/NOMOCRAT/Datasets/NOMOCRAT/NOMOCRAT_masks_v5_checked"

CLASS_NAMES = [
    "Caption", "Footnote", "Formula", "List-item", "Page-footer",
    "Page-header", "Picture", "Section-header", "Table", "Text", "Title"
]
NUM_CLASSES = len(CLASS_NAMES)

# ------------------------
# Metrics
# ------------------------
def compute_dice(y_true, y_pred, cls):
    """Standard Dice coefficient."""
    y_true_cls = (y_true == cls).astype(np.uint8)
    y_pred_cls = (y_pred == cls).astype(np.uint8)
    intersection = np.logical_and(y_true_cls, y_pred_cls).sum()
    denominator = y_true_cls.sum() + y_pred_cls.sum()
    return (2 * intersection) / denominator if denominator > 0 else np.nan, y_true_cls.sum()  # use GT pixels for weighting

def compute_distance_weighted_dice(y_true, y_pred, cls, sigma=5.0):
    """
    Distance-weighted Dice: gives more weight to pixels near GT boundaries.
    """
    y_true_cls = (y_true == cls).astype(np.uint8)
    y_pred_cls = (y_pred == cls).astype(np.uint8)

    if y_true_cls.sum() == 0 and y_pred_cls.sum() == 0:
        return np.nan, 0

    # Distance transform from GT mask (distance to foreground)
    dist_true = distance_transform_edt(1 - y_true_cls)
    dist_pred = distance_transform_edt(1 - y_pred_cls)

    # Weight both GT and prediction by distance
    weights_true = np.exp(-dist_true / sigma)
    weights_pred = np.exp(-dist_pred / sigma)

    weighted_intersection = np.sum(weights_true * weights_pred)
    weighted_denominator = np.sum(weights_true**2) + np.sum(weights_pred**2)

    dw_dice = (2 * weighted_intersection) / weighted_denominator if weighted_denominator > 0 else np.nan
    return dw_dice, np.sum(weights_true**2)  # use weighted GT pixels for aggregation

def compute_accuracy(y_true, y_pred):
    return (y_true == y_pred).sum() / y_true.size

# ------------------------
# Evaluation
# ------------------------
dices = np.zeros(NUM_CLASSES)
dw_dices = np.zeros(NUM_CLASSES)
class_pixel_counts = np.zeros(NUM_CLASSES)
accs = []
num_images = 0

for mask_name in os.listdir(pred_mask_dir):
    pred_path = os.path.join(pred_mask_dir, mask_name)
    gt_path   = os.path.join(gt_mask_dir, mask_name)

    pred_mask = cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE)
    gt_mask   = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)

    if pred_mask is None or gt_mask is None or pred_mask.shape != gt_mask.shape:
        continue

    num_images += 1
    accs.append(compute_accuracy(gt_mask, pred_mask))

    for cls in range(NUM_CLASSES):
        dice, dice_pixels = compute_dice(gt_mask, pred_mask, cls)
        dw_dice, dw_pixels = compute_distance_weighted_dice(gt_mask, pred_mask, cls)

        if not np.isnan(dice):
            dices[cls] += dice * dice_pixels
            dw_dices[cls] += dw_dice * dw_pixels
            class_pixel_counts[cls] += dice_pixels  # keep GT pixel counts for normalization

# ------------------------
# Weighted mean across dataset
# ------------------------
valid = class_pixel_counts > 0
dices[valid] /= class_pixel_counts[valid]
dw_dices[valid] /= class_pixel_counts[valid]
acc = np.mean(accs)

# ------------------------
# Print results
# ------------------------
print("==== Segmentation Evaluation ====")
for cls, name in enumerate(CLASS_NAMES):
    if valid[cls]:
        print(f"{name:12s} | Dice={dices[cls]:.4f} | DW-Dice={dw_dices[cls]:.4f}")
    else:
        print(f"{name:12s} | (no samples)")

weighted_mean_dice = np.nansum(dices * class_pixel_counts) / np.sum(class_pixel_counts)
weighted_mean_dw_dice = np.nansum(dw_dices * class_pixel_counts) / np.sum(class_pixel_counts)

print("\n==== Overall Results ====")
print(f"Weighted Mean Dice:      {weighted_mean_dice:.4f}")
print(f"Weighted Mean DW-Dice:   {weighted_mean_dw_dice:.4f}")
print(f"Overall Accuracy:        {acc:.4f}")



import winsound

# Beep at 1000 Hz for 500 milliseconds
winsound.Beep(1000, 500)

