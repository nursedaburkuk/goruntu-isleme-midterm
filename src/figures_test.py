"""Bölüm 13-14 ve zorunlu Şekil 1, 4, 5, 6.
Bu şekiller kilitli tahminler kaydedildikten SONRA üretilir; pipeline değiştirilmez."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from methods import read_gray, run_pipeline
from references import read_tra
from viz import display_stretch, overlay_labels


def fig_temporal(results_csv, out):
    """Şekil 5: üç test bloğu için kare numarasına karşı hücre sayısı."""
    df = pd.read_csv(results_csv)
    df = df[df["row_type"] == "frame"]
    blocks = sorted(df["block"].unique())
    fig, ax = plt.subplots(1, len(blocks), figsize=(5.2 * len(blocks), 4.2), sharey=True)
    for a, b in zip(ax, blocks):
        g = df[df["block"] == b].sort_values("frame")
        a.plot(g["frame"], g["reference_count"], "o-", color="black", label="Gerçek (TRA)")
        a.plot(g["frame"], g["baseline_predicted_count"], "s--", color="tab:orange", label="Baseline")
        a.plot(g["frame"], g["final_predicted_count"], "^-", color="tab:blue", label="Nihai pipeline")
        a.set_title(f"Blok {b} (02/t{int(g['frame'].min()):03d}–t{int(g['frame'].max()):03d})")
        a.set_xlabel("Kare numarası"); a.set_xticks(g["frame"].astype(int))
        a.grid(alpha=0.3)
    ax[0].set_ylabel("Hücre sayısı"); ax[0].legend(fontsize=9)
    plt.tight_layout(); plt.savefig(out, dpi=110); plt.close()


def fig_stages(data_dir, sequence, frame, cfg, out):
    """Şekil 4: nihai pipeline'ın aşama aşama çıktıları."""
    img = read_gray(data_dir, sequence, frame)
    c, st = run_pipeline(img, cfg, return_steps=True)
    ref = read_tra(data_dir, sequence, frame)
    panels = [
        (display_stretch(img), "gray", f"1) Orijinal {sequence}/t{frame:03d}\n(görüntüleme için gerilmiş)"),
        (st["intensity"], "gray", "2) Histogram eşitleme"),
        (st["filtered"], "gray", "3) Gaussian 9×9"),
        (st["segmentation"], "gray", f"4) Otsu eşikleme (T={st['threshold']:.0f})"),
        (st["morphology"], "gray", "5) Delik doldurma + erosion 7×7 (elips)"),
        (st["cleaned"], "gray", "6) Min. alan 300 px"),
        (overlay_labels(img, st["labels"], ref), None,
         f"7) 8-komşuluk CCL ve sayım: {c}\n(referans {len(np.unique(ref)) - 1})"),
    ]
    fig, ax = plt.subplots(1, len(panels), figsize=(3.6 * len(panels), 4.3))
    for a, (im, cmap, t) in zip(ax, panels):
        a.imshow(im, cmap=cmap) if cmap else a.imshow(im)
        a.set_title(t, fontsize=10); a.axis("off")
    plt.tight_layout(); plt.savefig(out, dpi=80); plt.close()


def fig_examples(data_dir, items, cfg, baseline_cfg, out):
    """Şekil 6: başarılı, hatalı ve zorlayıcı sayım örnekleri.
    items: (etiket, sekans, kare, (y0, y1, x0, x1) kırpma veya None)."""
    fig, ax = plt.subplots(2, len(items), figsize=(5.0 * len(items), 10.4))
    for j, (label, seq, f, crop) in enumerate(items):
        img = read_gray(data_dir, seq, f)
        ref = read_tra(data_dir, seq, f)
        n_ref = len(np.unique(ref)) - 1
        for i, (name, c_) in enumerate([("Baseline", baseline_cfg), ("Nihai", cfg)]):
            c, st = run_pipeline(img, c_, return_steps=True)
            ov = overlay_labels(img, st["labels"], ref)
            if crop:
                y0, y1, x0, x1 = crop
                ov = ov[y0:y1, x0:x1]
            ax[i, j].imshow(ov)
            ax[i, j].set_title(f"{label}\n{name}: {seq}/t{f:03d}, tahmin {c}, ref {n_ref} ({c - n_ref:+d})",
                               fontsize=10)
            ax[i, j].axis("off")
    plt.tight_layout(); plt.savefig(out, dpi=75); plt.close()


def fig_flowchart(out):
    """Şekil 1: nihai pipeline akış diyagramı (veri görüntüsü içermez)."""
    steps = [
        ("Giriş", "8-bit gri seviye görüntü\n(1024×1024)"),
        ("Yoğunluk dönüşümü", "Histogram eşitleme\n(cv2.equalizeHist)"),
        ("Yumuşatma", "Gaussian filtre 9×9\n(σ = 1,7; OpenCV ksize'dan)"),
        ("Segmentasyon", "Otsu global eşikleme"),
        ("Morfoloji", "Delik doldurma\n→ Erosion 7×7 (elips)"),
        ("Temizleme", "Alanı < 300 px olan\nbileşenleri kaldır"),
        ("Etiketleme", "Bağlı bileşen analizi\n(8-komşuluk)"),
        ("Çıkış", "Hücre sayısı\n= bileşen sayısı"),
    ]
    fig, ax = plt.subplots(figsize=(16, 2.9))
    ax.set_xlim(0, len(steps) * 2); ax.set_ylim(0, 2); ax.axis("off")
    for i, (h, t) in enumerate(steps):
        x = i * 2 + 0.1
        ax.add_patch(FancyBboxPatch((x, 0.35), 1.7, 1.3, boxstyle="round,pad=0.03",
                                    fc="#e8f0fb" if 0 < i < len(steps) - 1 else "#f2f2f2", ec="#1f4e8c"))
        ax.text(x + 0.85, 1.38, h, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(x + 0.85, 0.85, t, ha="center", va="center", fontsize=8.6)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.0, 1.0), xytext=(x + 1.8, 1.0),
                        arrowprops=dict(arrowstyle="->", color="#1f4e8c", lw=1.5))
    plt.tight_layout(); plt.savefig(out, dpi=130); plt.close()
