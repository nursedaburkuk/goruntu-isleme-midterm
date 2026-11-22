"""Performans metrikleri ve küme üzerinde değerlendirme."""
import numpy as np
import pandas as pd
from methods import count_image


def mae(ref, pred):
    return float(np.mean(np.abs(np.asarray(pred) - np.asarray(ref))))


def rmse(ref, pred):
    return float(np.sqrt(np.mean((np.asarray(pred) - np.asarray(ref)) ** 2)))


def bias(ref, pred):
    """Ortalama işaretli hata: tahmin - gerçek (pozitif = fazla sayım)."""
    return float(np.mean(np.asarray(pred) - np.asarray(ref)))


def exact_accuracy(ref, pred):
    return float(np.mean(np.asarray(pred) == np.asarray(ref)))


def predict_frames(data_dir, frames_df, config):
    """frames_df: sequence ve frame sütunları. Referans okumaz."""
    rows = []
    for s, f in zip(frames_df["sequence"], frames_df["frame"]):
        c, t = count_image(data_dir, str(s).zfill(2), int(f), config)
        rows.append(dict(sequence=str(s).zfill(2), frame=int(f), predicted_count=c, time_s=t))
    return pd.DataFrame(rows)


def evaluate(data_dir, ref_df, config):
    """ref_df: sequence, frame, reference_count sütunları."""
    pred = predict_frames(data_dir, ref_df, config)
    ref = ref_df["reference_count"].values
    p = pred["predicted_count"].values
    summary = dict(MAE=mae(ref, p), RMSE=rmse(ref, p), Bias=bias(ref, p),
                   ExactAcc=exact_accuracy(ref, p), mean_time_s=float(pred["time_s"].mean()))
    pred["reference_count"] = ref
    return summary, pred
