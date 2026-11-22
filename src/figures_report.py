"""Rapor için kompakt şekiller (Şekil 2, 3, 6). Yöntem ve sonuçlar değişmez;
yalnızca sayfa yerini azaltmak için paneller birleştirilmiştir."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from methods import read_gray, run_pipeline
from references import read_tra
from viz import overlay_labels


def _load():
    return json.load(open("experiment_configs.json")), pd.read_csv("experiments.csv").set_index("Deney ID")


def fig2_compact(data_dir, frame, ids, out):
    cfgs, ex = _load()
    img = read_gray(data_dir, "01", frame)
    fig, ax = plt.subplots(2, len(ids), figsize=(3.0 * len(ids), 5.4),
                           gridspec_kw={"height_ratios": [3, 1.6]})
    for j, eid in enumerate(ids):
        c, st = run_pipeline(img, cfgs[eid], return_steps=True)
        name = ex.loc[eid, "Deney"].replace("Yoğunluk: ", "")
        p = ex.loc[eid, "Param."].replace("; min_area=300", "").replace("min_area=300", "")
        ax[0, j].imshow(st["intensity"], cmap="gray", vmin=0, vmax=255)
        ax[0, j].set_title(f"{eid}: {name}" + (f"\n{p}" if p else "\n") +
                           f"\nsayım {c}, dev MAE {ex.loc[eid, 'Count MAE']:.1f}", fontsize=8.5)
        ax[0, j].axis("off")
        ax[1, j].hist(st["intensity"].ravel(), bins=128, range=(0, 256), log=True, color="0.3")
        ax[1, j].tick_params(labelsize=7)
    plt.tight_layout(h_pad=0.3, w_pad=0.3); plt.savefig(out, dpi=110); plt.close()


def fig3_compact(data_dir, frame, seg_ids, morph_ids, out):
    cfgs, ex = _load()
    img = read_gray(data_dir, "01", frame)
    n = max(len(seg_ids), len(morph_ids))
    fig, ax = plt.subplots(2, n, figsize=(3.0 * n, 7.0))
    for r, (ids, key) in enumerate([(seg_ids, "segmentation"), (morph_ids, "cleaned")]):
        for j in range(n):
            ax[r, j].axis("off")
            if j >= len(ids):
                continue
            eid = ids[j]
            c, st = run_pipeline(img, cfgs[eid], return_steps=True)
            name = ex.loc[eid, "Deney"].split(": ", 1)[-1]
            ax[r, j].imshow(st[key], cmap="gray")
            ax[r, j].set_title(f"{eid}: {name}\nsayım {c}, dev MAE {ex.loc[eid, 'Count MAE']:.1f}", fontsize=8.5)
    plt.tight_layout(h_pad=2.2, w_pad=0.3); plt.savefig(out, dpi=110); plt.close()


def fig6_compact(data_dir, items, cfg, baseline_cfg, out):
    fig, ax = plt.subplots(1, len(items), figsize=(3.6 * len(items), 4.4))
    for a, (label, seq, f, crop) in zip(ax, items):
        img = read_gray(data_dir, seq, f)
        ref = read_tra(data_dir, seq, f)
        n_ref = len(np.unique(ref)) - 1
        cb = run_pipeline(img, baseline_cfg)
        c, st = run_pipeline(img, cfg, return_steps=True)
        ov = overlay_labels(img, st["labels"], ref)
        if crop:
            y0, y1, x0, x1 = crop
            ov = ov[y0:y1, x0:x1]
        a.imshow(ov); a.axis("off")
        a.set_title(f"{label}\n{seq}/t{f:03d}: ref {n_ref}, nihai {c} ({c - n_ref:+d}),\nbaseline {cb} ({cb - n_ref:+d})",
                    fontsize=8.5)
    plt.tight_layout(w_pad=0.4); plt.savefig(out, dpi=110); plt.close()


def fig3_one_row(data_dir, frame, items, out):
    """Şekil 3 tek satır: items = (deney ID, gösterilecek adım) listesi."""
    cfgs, ex = _load()
    img = read_gray(data_dir, "01", frame)
    fig, ax = plt.subplots(1, len(items), figsize=(2.9 * len(items), 3.7))
    for a, (eid, key) in zip(ax, items):
        c, st = run_pipeline(img, cfgs[eid], return_steps=True)
        name = ex.loc[eid, "Deney"].split(": ", 1)[-1]
        a.imshow(st[key], cmap="gray"); a.axis("off")
        a.set_title(f"{eid}: {name}\nsayım {c}, dev MAE {ex.loc[eid, 'Count MAE']:.1f}", fontsize=8.5)
    plt.tight_layout(pad=1.0, w_pad=0.3, rect=(0, 0, 1, 0.97)); plt.savefig(out, dpi=110); plt.close()
