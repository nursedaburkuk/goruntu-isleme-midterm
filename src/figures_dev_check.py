"""Bölüm 10.6: baseline ve aday pipeline'ların bütün geliştirme görüntülerinde görsel incelemesi."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from methods import read_gray, run_pipeline
from references import read_tra
from viz import overlay_labels


def fig_dev_all(data_dir, frames, cfg, title, out):
    fig, ax = plt.subplots(2, 5, figsize=(25, 11.8))
    for a, f in zip(ax.ravel(), frames):
        img = read_gray(data_dir, "01", f)
        ref = read_tra(data_dir, "01", f)
        c, st = run_pipeline(img, cfg, return_steps=True)
        n_ref = len(np.unique(ref)) - 1
        a.imshow(overlay_labels(img, st["labels"], ref))
        a.set_title(f"01/t{f:03d}: tahmin {c}, referans {n_ref}, hata {c - n_ref:+d}", fontsize=11)
        a.axis("off")
    fig.suptitle(title + "  (yeşil: tespit edilen nesne, kırmızı: referans hücre)", fontsize=13)
    plt.tight_layout(rect=(0, 0, 1, 0.95), h_pad=3.0); plt.savefig(out, dpi=55); plt.close()
