"""Bölüm 6-9 karşılaştırma şekilleri (geliştirme görüntüsü üzerinde)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from methods import read_gray, run_pipeline
from references import read_tra
from viz import display_stretch, overlay_labels


def _cfgs():
    return json.load(open("experiment_configs.json"))


def fig_intensity(data_dir, frame, ids, out):
    cfgs, ex = _cfgs(), pd.read_csv("experiments.csv").set_index("Deney ID")
    img = read_gray(data_dir, "01", frame)
    ref = read_tra(data_dir, "01", frame)
    fig, ax = plt.subplots(3, len(ids), figsize=(4.2 * len(ids), 12.5))
    for j, eid in enumerate(ids):
        c, st = run_pipeline(img, cfgs[eid], return_steps=True)
        name = ex.loc[eid, "Deney"].replace("Yoğunluk: ", "")
        ax[0, j].imshow(st["intensity"], cmap="gray", vmin=0, vmax=255)
        ax[0, j].set_title(f"{eid}: {name}\n{ex.loc[eid, 'Param.']}", fontsize=9)
        ax[1, j].hist(st["intensity"].ravel(), bins=256, range=(0, 256), log=True, color="0.3")
        ax[1, j].set_title("Histogram (log ölçek)", fontsize=9)
        ax[2, j].imshow(overlay_labels(img, st["labels"], ref))
        ax[2, j].set_title(f"Sayım {c} / referans {len(np.unique(ref)) - 1} "
                           f"(dev MAE={ex.loc[eid, 'Count MAE']:.2f})", fontsize=9)
        ax[0, j].axis("off"); ax[2, j].axis("off")
    fig.suptitle(f"Yoğunluk dönüşümleri, 01/t{frame:03d}. Ortak zincir: dönüşüm -> Gaussian 5x5 -> "
                 f"Otsu -> delik doldurma -> opening 5x5 -> min alan 300 px", fontsize=11)
    plt.tight_layout(); plt.savefig(out, dpi=70); plt.close()


def fig_grid(data_dir, frame, ids, out, show="segmentation", title=""):
    cfgs, ex = _cfgs(), pd.read_csv("experiments.csv").set_index("Deney ID")
    img = read_gray(data_dir, "01", frame)
    ref = read_tra(data_dir, "01", frame)
    n = len(ids)
    fig, ax = plt.subplots(2, n, figsize=(4.2 * n, 10.0))
    for j, eid in enumerate(ids):
        c, st = run_pipeline(img, cfgs[eid], return_steps=True)
        name = ex.loc[eid, "Deney"].split(": ", 1)[-1]
        if show == "filtered":
            ax[0, j].imshow(st["filtered"], cmap="gray", vmin=0, vmax=255)
        else:
            ax[0, j].imshow(st[show], cmap="gray")
        ax[0, j].set_title(f"{eid}: {name}", fontsize=9)
        ax[1, j].imshow(overlay_labels(img, st["labels"], ref))
        ax[1, j].set_title(f"Sayım {c} / ref {len(np.unique(ref)) - 1} "
                           f"(dev MAE={ex.loc[eid, 'Count MAE']:.2f})", fontsize=9)
        ax[0, j].axis("off"); ax[1, j].axis("off")
    fig.suptitle(title, fontsize=11)
    plt.tight_layout(rect=(0, 0, 1, 0.96), h_pad=2.5); plt.savefig(out, dpi=70); plt.close()


def fig_parameter_effects(out):
    ex = pd.read_csv("experiments.csv").set_index("Deney ID")
    panels = [
        ("Gaussian kernel boyutu (S2)", ["E08", "E09", "E10", "E11"], [1, 3, 5, 9], "kernel (1 = filtre yok)"),
        ("Sabit eşik T (S3, HE ölçeği)", ["E17", "E18", "E19", "E20"], [100, 140, 180, 220], "T"),
        ("Erosion yapılandırma elemanı (S4)", ["E27", "E28", "E29"], [1, 3, 7], "boyut (1 = işlem yok)"),
        ("Opening yapılandırma elemanı (S4)", ["E27", "E32", "E33", "E34"], [1, 3, 5, 9], "boyut (1 = işlem yok)"),
        ("Minimum alan (S6)", ["E43", "E44", "E45", "E46", "E47"], [50, 150, 300, 500, 800], "piksel"),
    ]
    fig, ax = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 3.8))
    for a, (t, ids, xs, xl) in zip(ax, panels):
        a.plot(xs, ex.loc[ids, "Count MAE"], "o-", label="MAE")
        a.plot(xs, ex.loc[ids, "Bias"], "s--", label="Bias")
        a.axhline(0, color="0.7", lw=0.8)
        a.set_title(t, fontsize=10); a.set_xlabel(xl); a.set_xticks(xs)
        a.legend(fontsize=8)
    ax[0].set_ylabel("Geliştirme kümesi (10 kare)")
    plt.tight_layout(); plt.savefig(out, dpi=80); plt.close()
