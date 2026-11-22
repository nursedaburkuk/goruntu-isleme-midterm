"""Referans hücre sayıları (Ödev Bölüm 4).

TRA takip etiketi görüntüsünde 0 (arka plan) hariç farklı pozitif hücre
kimlikleri sayılır. Test referansları ancak test_predictions_locked.csv
kaydedildikten sonra okunabilir.
"""
import os
import cv2
import numpy as np
import pandas as pd

LOCKED_PREDICTIONS_FILE = "test_predictions_locked.csv"


def tra_path(data_dir, sequence, frame):
    return os.path.join(data_dir, f"{sequence}_GT", "TRA", f"man_track{frame:03d}.tif")


def read_tra(data_dir, sequence, frame):
    return cv2.imread(tra_path(data_dir, sequence, frame), cv2.IMREAD_UNCHANGED)


def reference_count(data_dir, sequence, frame):
    labels = read_tra(data_dir, sequence, frame)
    ids = np.unique(labels)
    return int(np.sum(ids > 0))


def reference_counts(data_dir, selected, group):
    """selected: selected_frames.csv içeriği. group: development / validation / test."""
    if group == "test" and not os.path.exists(LOCKED_PREDICTIONS_FILE):
        raise PermissionError(
            "Test referansları, test_predictions_locked.csv kaydedilmeden okunamaz.")
    sub = selected[selected["group"] == group].copy()
    sub["reference_count"] = [
        reference_count(data_dir, f"{int(s):02d}" if not isinstance(s, str) else s, int(f))
        for s, f in zip(sub["sequence"], sub["frame"])
    ]
    return sub
