"""Bölüm 11: doğrulama karelerinde seçilen pipeline'ın çıktıları."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from methods import read_gray, run_pipeline
from references import read_tra
from viz import overlay_labels


def fig_validation(data_dir, frames, cfg, title, out):
    fig, ax = plt.subplots(1, len(frames), figsize=(4.6 * len(frames), 5.2))
    for a, f in zip(ax, frames):
        img = read_gray(data_dir, "01", f)
        ref = read_tra(data_dir, "01", f)
        c, st = run_pipeline(img, cfg, return_steps=True)
        n_ref = len(np.unique(ref)) - 1
        a.imshow(overlay_labels(img, st["labels"], ref))
        a.set_title(f"01/t{f:03d}: tahmin {c}, referans {n_ref}, hata {c - n_ref:+d}", fontsize=10)
        a.axis("off")
    fig.suptitle(title + "  (yeşil: tespit edilen nesne sınırı, kırmızı: referans hücre)", fontsize=11)
    plt.tight_layout(rect=(0, 0, 1, 0.94)); plt.savefig(out, dpi=75); plt.close()
