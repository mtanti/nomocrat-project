#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import re
from jiwer import cer, wer


# -------------------------
# OPTIONAL NORMALISATION
# -------------------------
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------
# GT TEXT (UPDATED)
# -------------------------
def build_gt_text(json_data):
    lines = []

    for page in json_data["data"]:
        channels = page.get("channels", {})

        # ---- MAIN TEXT ----
        for region in channels.get("Text", []):
            t = region.get("transcription", "")
            if t:
                lines.append(t.strip())

        # ---- FOOTNOTE ----
        for region in channels.get("Footnote", []):
            t = region.get("transcription", "")
            if t:
                lines.append(t.strip())

        # ---- CAPTION ----
        for region in channels.get("Caption", []):
            t = region.get("transcription", "")
            if t:
                lines.append(t.strip())

        # page separator
        lines.append("")

    return "\n".join(lines)


# -------------------------
# PRED TEXT (UNCHANGED)
# -------------------------
def build_pred_text(pred_json_data):
    lines = []

    for page in pred_json_data["data"]:
        texts = page.get("texts", [])

        for t in texts:
            if t and t.strip():
                lines.append(t.strip())

        lines.append("")

    return "\n".join(lines)


# -------------------------
# RUN
# -------------------------
gt_json_path = r"D:\Emma_Fenech_RSO\NOMOCRAT\Datasets\NOMOCRAT\pipeline_data_no_tables.json"
pred_json_path = r"D:\Emma_Fenech_RSO\NOMOCRAT\Datasets\NOMOCRAT\baseline_manual.json"

with open(gt_json_path, "r", encoding="utf-8") as f:
    gt_json = json.load(f)

with open(pred_json_path, "r", encoding="utf-8") as f:
    pred_json = json.load(f)

gt_text = build_gt_text(gt_json)
pred_text = build_pred_text(pred_json)

# optional normalization
gt_eval = normalize_text(gt_text)
pred_eval = normalize_text(pred_text)

# -------------------------
# METRICS
# -------------------------
print("\nRESULTS norm:")
print({
    "CER": cer(gt_eval, pred_eval),
    "WER": wer(gt_eval, pred_eval),
})

print("\nRESULTS base:")
print({
    "CER": cer(gt_text, pred_text),
    "WER": wer(gt_text, pred_text)
})

