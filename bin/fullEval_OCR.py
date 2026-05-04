#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import json
import re
from jiwer import cer, wer


# -------------------------
# NORMALIZATION
# -------------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------
# GT TEXT (UNCHANGED FROM YOUR VERSION)
# -------------------------
def build_gt_text(json_data):
    full_text = ""

    for page in json_data["data"]:
        channels = page.get("channels", {})

        # ---- MAIN TEXT ----
        for region in channels.get("Text", []):
            t = region.get("transcription", "").strip()
            if t:
                full_text += t + "\n"

        # ---- FOOTNOTE ----
        for region in channels.get("Footnote", []):
            t = region.get("transcription", "").strip()
            if t:
                full_text += t + "\n"

        # ---- CAPTION ----
        for region in channels.get("Caption", []):
            t = region.get("transcription", "").strip()
            if t:
                full_text += t + "\n"

        full_text += "\n"

    return full_text


# -------------------------
# HELPERS
# -------------------------
def extract_index(filename):
    match = re.search(r"_(\d+)_", filename)
    return int(match.group(1)) if match else 10**9


def read_and_sort_files(files, folder):
    files = sorted(files, key=extract_index)
    lines = []

    for f in files:
        path = os.path.join(folder, f)
        with open(path, "r", encoding="utf-8") as file:
            t = file.read().strip()
            if t:
                lines.append(t)

    return lines


# -------------------------
# PRED TEXT (FIXED)
# -------------------------
def build_pred_text(base_folder, json_data):
    full_text = ""

    for page in json_data["data"]:
        fname = page["page"]["page_fname"]
        page_id = os.path.splitext(fname)[0]

        page_folder = os.path.join(base_folder, page_id)

        if not os.path.exists(page_folder):
            print(f"Missing folder: {page_folder}")
            continue

        all_files = os.listdir(page_folder)

        # ---- TEXT ----
        text_files = [
            f for f in all_files
            if f.endswith(".txt") and "_text" in f
        ]

        # ---- FOOTNOTE / FOOTER ----
        footer_files = [
            f for f in all_files
            if f.endswith(".txt") and ("_page-footer" in f)
        ]

        # ---- CAPTION ----
        caption_files = [
            f for f in all_files
            if f.endswith(".txt") and "_caption" in f
        ]

        # read in correct order
        text_lines = read_and_sort_files(text_files, page_folder)
        footer_lines = read_and_sort_files(footer_files, page_folder)
        caption_lines = read_and_sort_files(caption_files, page_folder)

        # append in same order as GT
        for t in text_lines:
            full_text += t + "\n"

        for t in footer_lines:
            full_text += t + "\n"

        for t in caption_lines:
            full_text += t + "\n"

        full_text += "\n"  # page break

    return full_text


# -------------------------
# RUN
# -------------------------
json_path = r"D:\Emma_Fenech_RSO\NOMOCRAT\Datasets\NOMOCRAT\pipeline_data.json"
pred_folder = r"D:\Emma_Fenech_RSO\NOMOCRAT\Datasets\NOMOCRAT\tuned_tesseract_output_raw_v3"

with open(json_path, "r", encoding="utf-8") as f:
    gt_json = json.load(f)

gt_text = build_gt_text(gt_json)
pred_text = build_pred_text(pred_folder, gt_json)


# -------------------------
# NORMALIZED METRICS
# -------------------------
gt_eval = normalize_text(gt_text)
pred_eval = normalize_text(pred_text)

print("\nRESULTS norm:")
print({
    "CER": cer(gt_eval, pred_eval),
    "WER": wer(gt_eval, pred_eval),
})

# -------------------------
# RAW METRICS
# -------------------------
print("\nRESULTS base:")
print({
    "CER": cer(gt_text, pred_text),
    "WER": wer(gt_text, pred_text)
})

