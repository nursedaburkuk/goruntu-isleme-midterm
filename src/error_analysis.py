"""Bölüm 13/15: hata ayrıştırması (yalnızca analiz; pipeline değiştirilmez).
Her referans hücrenin TRA işaretinin piksellerinden en çok örtüştüğü tahmin
nesnesi bulunur. Kaçırılan = hiçbir nesneyle örtüşmeyen referans; birleşmiş =
birden fazla referans içeren nesne; sahte = hiçbir referans içermeyen nesne."""
import numpy as np
import pandas as pd
from methods import read_gray, run_pipeline
from references import read_tra


def decompose(data_dir, sequence, frame, cfg):
    img = read_gray(data_dir, sequence, frame)
    ref = read_tra(data_dir, sequence, frame)
    _, st = run_pipeline(img, cfg, return_steps=True)
    lab = st["labels"]
    ref_ids = [i for i in np.unique(ref) if i > 0]
    obj_ids = [i for i in np.unique(lab) if i > 0]
    assigned = {}
    missed = 0
    for r in ref_ids:
        ov = lab[ref == r]
        ov = ov[ov > 0]
        if ov.size == 0:
            missed += 1
            continue
        assigned.setdefault(int(np.bincount(ov).argmax()), []).append(r)
    merged_objects = sum(1 for v in assigned.values() if len(v) > 1)
    merged_extra = sum(len(v) - 1 for v in assigned.values() if len(v) > 1)
    false_pos = sum(1 for o in obj_ids if o not in assigned)
    mean_int = {r: float(img[ref == r].mean()) for r in ref_ids}
    missed_int = [round(mean_int[r], 1) for r in ref_ids
                  if not (lab[ref == r] > 0).any()]
    return dict(sequence=sequence, frame=frame, reference=len(ref_ids), predicted=len(obj_ids),
                missed=missed, merged_objects=merged_objects, merged_lost=merged_extra,
                false_positive=false_pos, missed_mean_intensity=missed_int)


def decompose_set(data_dir, frames, cfg, sequence):
    return pd.DataFrame([decompose(data_dir, sequence, f, cfg) for f in frames])
