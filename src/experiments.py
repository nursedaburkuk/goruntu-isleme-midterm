"""Kontrollü deneyler (Ödev Bölüm 6-10).

Deneyler aşamalı yürütülür. Her aşamada bir önceki aşamanın en iyi
konfigürasyonu (geliştirme MAE'si en düşük; eşitlikte RMSE, sonra daha az
işlem adımı, sonra deney sırası) "ebeveyn" olarak alınır ve yalnızca o
aşamanın konusu olan işlem / parametre değiştirilir.

Bütün deneyler yalnızca GELİŞTİRME görüntüleri üzerinde değerlendirilir.
"""
import copy
import json
import pandas as pd
from methods import with_changes, BASELINE_TEMPLATE
from evaluation import evaluate

BASELINE_MIN_AREA = 50  # Bölüm 5: geliştirme kümesinde belirlendi

# Histogram eşleme referansı: geliştirme kareleri içinde ortalama yoğunluğu
# medyan olan kare (yalnızca geliştirme kümesinden, Bölüm 6).
HIST_MATCH_REFERENCE_NAME = None


def choose_hist_match_reference(data_dir, dev_df):
    import numpy as np
    from methods import read_gray, set_histogram_matching_reference
    global HIST_MATCH_REFERENCE_NAME
    means = []
    for s, f in zip(dev_df["sequence"], dev_df["frame"]):
        means.append((float(read_gray(data_dir, str(s).zfill(2), int(f)).mean()), int(f)))
    means.sort()
    frame = means[len(means) // 2][1]
    HIST_MATCH_REFERENCE_NAME = f"dev_t{frame:03d}"
    set_histogram_matching_reference(HIST_MATCH_REFERENCE_NAME, read_gray(data_dir, "01", frame))
    return frame

# Aşama 1'in başlangıç konfigürasyonu: yoğunluk dönüşümleri bu ortak
# zincir içinde karşılaştırılır. Gaussian 5x5 hafif gürültü bastırma,
# delik doldurma nükleol boşlukları, opening 5x5 ince çıkıntılar ve
# min alan 300 px gürültü parçaları için konulmuştur; bu adımların her
# birinin etkisi sonraki aşamalarda ayrıca ölçülür.
STAGE1_BASE = {
    "intensity": {"method": "none"},
    "filters": [{"method": "gaussian", "ksize": 5}],
    "segmentation": {"method": "otsu"},
    "morphology": [{"op": "opening", "ksize": 5, "shape": "ellipse"}],
    "fill_holes": True,
    "separation": {"method": "none"},
    "min_area": 300,
}


# ----------------------------------------------------------------------------
# Tablo için okunabilir açıklamalar
# ----------------------------------------------------------------------------
def describe_intensity(c):
    m = c["method"]
    return {"none": "Yok (orijinal)", "contrast_stretching": "Contrast stretching",
            "histogram_equalization": "Histogram eşitleme", "clahe": "CLAHE",
            "histogram_matching": "Histogram eşleme"}[m]


def intensity_params(c):
    m = c["method"]
    if m == "contrast_stretching":
        return f"p{c['low_percentile']}-p{c['high_percentile']}"
    if m == "clahe":
        return f"clip={c['clip_limit']}, tile={c['tile_grid']}x{c['tile_grid']}"
    if m == "histogram_matching":
        return f"ref={c['reference']}"
    return ""


def describe_filters(fs):
    if not fs:
        return "Yok"
    out = []
    for f in fs:
        m = f["method"]
        if m == "gaussian":
            out.append(f"Gaussian {f['ksize']}x{f['ksize']}")
        elif m == "median":
            out.append(f"Median {f['ksize']}x{f['ksize']}")
        elif m == "unsharp_mask":
            out.append(f"Unsharp mask (G{f['ksize']}, a={f['amount']})")
        elif m == "laplacian_sharpen":
            out.append(f"Laplace keskinleştirme (a={f.get('amount', 1.0)})")
        elif m == "bilateral":
            out.append(f"Bilateral (d={f['d']})")
        else:
            out.append(m)
    return " + ".join(out)


def describe_segmentation(s):
    m = s["method"]
    if m == "fixed":
        return f"Sabit eşik (T={s['threshold']})"
    if m == "otsu":
        return "Otsu"
    if m == "triangle":
        return "Triangle"
    if m == "adaptive":
        return f"Adaptif {s.get('type', 'gaussian')} (blok={s['block_size']}, C={s['C']})"
    if m == "kmeans":
        return f"K-means (k={s.get('k', 2)})"
    return m


def describe_morphology(cfg):
    names = {"erosion": "Erosion", "dilation": "Dilation", "opening": "Opening",
             "closing": "Closing"}
    parts = [f"{names[o['op']]} {o['ksize']}x{o['ksize']}" for o in cfg.get("morphology", [])]
    if cfg.get("fill_holes"):
        parts.append("Delik doldurma")
    sep = cfg.get("separation", {}) or {}
    if sep.get("method") == "distance_watershed":
        parts.append(f"Distance transform + watershed (min_dist={sep['min_distance']})")
    return " -> ".join(parts) if parts else "Yok"


def n_steps(cfg):
    n = 1  # segmentasyon
    n += cfg["intensity"]["method"] != "none"
    n += len(cfg.get("filters", []))
    n += len(cfg.get("morphology", []))
    n += bool(cfg.get("fill_holes"))
    n += (cfg.get("separation", {}) or {}).get("method", "none") != "none"
    return n


# ----------------------------------------------------------------------------
# Aşama tanımları: (deney adı, değiştirilen öğe, ebeveyne uygulanacak değişiklik)
# ----------------------------------------------------------------------------
def stage_intensity(parent):
    return [
        ("Yoğunluk: orijinal", "intensity", with_changes(parent, intensity={"method": "none"})),
        ("Yoğunluk: contrast stretching", "intensity", with_changes(
            parent, intensity={"method": "contrast_stretching", "low_percentile": 1,
                               "high_percentile": 99.5})),
        ("Yoğunluk: histogram eşitleme", "intensity", with_changes(
            parent, intensity={"method": "histogram_equalization"})),
        ("Yoğunluk: CLAHE clip 2", "intensity", with_changes(
            parent, intensity={"method": "clahe", "clip_limit": 2.0, "tile_grid": 8})),
        ("Yoğunluk: CLAHE clip 4", "intensity.clip_limit", with_changes(
            parent, intensity={"method": "clahe", "clip_limit": 4.0, "tile_grid": 8})),
        ("Yoğunluk: histogram eşleme", "intensity", with_changes(
            parent, intensity={"method": "histogram_matching", "reference": HIST_MATCH_REFERENCE_NAME})),
    ]


def stage_filter(parent):
    return [
        ("Filtre: yok", "filters", with_changes(parent, filters=[])),
        ("Filtre: Gaussian 3x3", "filters.ksize", with_changes(
            parent, filters=[{"method": "gaussian", "ksize": 3}])),
        ("Filtre: Gaussian 5x5", "filters.ksize", with_changes(
            parent, filters=[{"method": "gaussian", "ksize": 5}])),
        ("Filtre: Gaussian 9x9", "filters.ksize", with_changes(
            parent, filters=[{"method": "gaussian", "ksize": 9}])),
        ("Filtre: Median 5x5", "filters", with_changes(
            parent, filters=[{"method": "median", "ksize": 5}])),
        ("Filtre: Median 9x9", "filters.ksize", with_changes(
            parent, filters=[{"method": "median", "ksize": 9}])),
        ("Filtre: Laplace keskinleştirme", "filters", with_changes(
            parent, filters=[{"method": "laplacian_sharpen", "amount": 1.0}])),
        ("Filtre: Gaussian 5x5 + unsharp mask", "filters", with_changes(
            parent, filters=[{"method": "gaussian", "ksize": 5},
                             {"method": "unsharp_mask", "ksize": 9, "amount": 1.0}])),
    ]


def stage_segmentation(parent):
    exps = [("Segmentasyon: Otsu", "segmentation", with_changes(
        parent, segmentation={"method": "otsu"}))]
    # Sabit eşik değerleri segmentasyona giren görüntünün ölçeğine göre seçilir.
    # Histogram eşitleme sonrasında ham 0 değeri 0'a, ham 3 değeri ~160'a
    # eşlendiği için eşikler 100-220 aralığında taranır (geliştirme kümesinde
    # Otsu eşiği 138-147 arasında bulunmuştur).
    for t in [100, 140, 180, 220]:
        exps.append((f"Segmentasyon: sabit eşik T={t}", "segmentation.threshold", with_changes(
            parent, segmentation={"method": "fixed", "threshold": t})))
    for bs, c in [(51, -20), (101, -20), (101, -40)]:
        exps.append((f"Segmentasyon: adaptif blok={bs} C={c}", "segmentation.adaptive",
                     with_changes(parent, segmentation={"method": "adaptive", "type": "gaussian",
                                                        "block_size": bs, "C": c})))
    exps.append(("Segmentasyon: triangle", "segmentation", with_changes(
        parent, segmentation={"method": "triangle"})))
    exps.append(("Segmentasyon: K-means k=2", "segmentation", with_changes(
        parent, segmentation={"method": "kmeans", "k": 2})))
    return exps


def stage_morphology(parent):
    op = lambda name, k: {"op": name, "ksize": k, "shape": "ellipse"}
    exps = [
        ("Morfoloji: yok (delik doldurma yok)", "morphology", with_changes(
            parent, morphology=[], fill_holes=False)),
        ("Morfoloji: yalnızca delik doldurma", "morphology", with_changes(
            parent, morphology=[], fill_holes=True)),
        ("Morfoloji: erosion 3x3", "morphology", with_changes(parent, morphology=[op("erosion", 3)])),
        ("Morfoloji: erosion 7x7", "morphology.ksize", with_changes(parent, morphology=[op("erosion", 7)])),
        ("Morfoloji: dilation 3x3", "morphology", with_changes(parent, morphology=[op("dilation", 3)])),
        ("Morfoloji: dilation 7x7", "morphology.ksize", with_changes(parent, morphology=[op("dilation", 7)])),
        ("Morfoloji: opening 3x3", "morphology.ksize", with_changes(parent, morphology=[op("opening", 3)])),
        ("Morfoloji: opening 5x5", "morphology.ksize", with_changes(parent, morphology=[op("opening", 5)])),
        ("Morfoloji: opening 9x9", "morphology.ksize", with_changes(parent, morphology=[op("opening", 9)])),
        ("Morfoloji: closing 5x5", "morphology", with_changes(parent, morphology=[op("closing", 5)])),
        ("Morfoloji: closing 9x9", "morphology.ksize", with_changes(parent, morphology=[op("closing", 9)])),
        ("Morfoloji: opening 5 -> closing 5", "morphology.order", with_changes(
            parent, morphology=[op("opening", 5), op("closing", 5)])),
        ("Morfoloji: closing 5 -> opening 5", "morphology.order", with_changes(
            parent, morphology=[op("closing", 5), op("opening", 5)])),
    ]
    return exps


def stage_separation(parent):
    return [
        ("Ayırma: yok", "separation", with_changes(parent, separation={"method": "none"})),
        ("Ayırma: distance + watershed min_dist=15", "separation.min_distance", with_changes(
            parent, separation={"method": "distance_watershed", "min_distance": 15})),
        ("Ayırma: distance + watershed min_dist=25", "separation.min_distance", with_changes(
            parent, separation={"method": "distance_watershed", "min_distance": 25})),
        ("Ayırma: distance + watershed min_dist=35", "separation.min_distance", with_changes(
            parent, separation={"method": "distance_watershed", "min_distance": 35})),
    ]


def stage_min_area(parent):
    return [(f"Min alan: {a} px", "min_area", with_changes(parent, min_area=a))
            for a in [50, 150, 300, 500, 800]]


STAGES = [
    ("S1 Yoğunluk", stage_intensity),
    ("S2 Filtre", stage_filter),
    ("S3 Segmentasyon", stage_segmentation),
    ("S4 Morfoloji", stage_morphology),
    ("S5 Nesne ayırma", stage_separation),
    ("S6 Min alan", stage_min_area),
]


def _row(exp_id, stage, name, changed, parent_id, cfg, summary):
    return {
        "Deney ID": exp_id, "Aşama": stage, "Deney": name, "Değişen": changed,
        "Ebeveyn": parent_id,
        "Yoğunluk": describe_intensity(cfg["intensity"]),
        "Filtre": describe_filters(cfg["filters"]),
        "Segment.": describe_segmentation(cfg["segmentation"]),
        "Morfoloji": describe_morphology(cfg),
        "Param.": "; ".join(p for p in [intensity_params(cfg["intensity"]),
                                         f"min_area={cfg['min_area']}"] if p),
        "Count MAE": round(summary["MAE"], 3), "RMSE": round(summary["RMSE"], 3),
        "Bias": round(summary["Bias"], 3), "Exact Acc": round(summary["ExactAcc"], 3),
        "Ort. süre (s)": round(summary["mean_time_s"], 4),
        "n_steps": n_steps(cfg), "config_json": json.dumps(cfg, ensure_ascii=False),
    }


def best_of(rows):
    return sorted(rows, key=lambda r: (r["Count MAE"], r["RMSE"], r["n_steps"],
                                       int(r["Deney ID"][1:])))[0]


def run_all(data_dir, dev_df, verbose=True):
    rows = []
    configs = {}
    counter = 1

    base = with_changes(BASELINE_TEMPLATE, min_area=BASELINE_MIN_AREA)
    s, _ = evaluate(data_dir, dev_df, base)
    eid = f"E{counter:02d}"
    configs[eid] = base
    rows.append(_row(eid, "S0 Baseline", "Baseline (Otsu + CCL)", "-", "-", base, s))
    counter += 1

    parent_id, parent_cfg = "S1 başlangıç", copy.deepcopy(STAGE1_BASE)
    for stage_name, builder in STAGES:
        stage_rows = []
        for name, changed, cfg in builder(parent_cfg):
            cfg = copy.deepcopy(cfg)
            cfg.pop("name", None)
            s, _ = evaluate(data_dir, dev_df, cfg)
            eid = f"E{counter:02d}"
            counter += 1
            configs[eid] = cfg
            r = _row(eid, stage_name, name, changed, parent_id, cfg, s)
            stage_rows.append(r)
            rows.append(r)
            if verbose:
                print(f"{eid} {name:45s} MAE={r['Count MAE']:.2f} RMSE={r['RMSE']:.2f} "
                      f"Bias={r['Bias']:+.2f}")
        best = best_of(stage_rows)
        parent_id, parent_cfg = best["Deney ID"], configs[best["Deney ID"]]
        if verbose:
            print(f"  -> {stage_name} en iyi: {parent_id}")
    return pd.DataFrame(rows), configs
