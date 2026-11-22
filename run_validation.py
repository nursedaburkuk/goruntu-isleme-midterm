"""Bölüm 11: Aday pipeline'ların doğrulama kümesinde karşılaştırılması.

Adaylar, geliştirme kümesinde her yöntem ailesinin en iyi konfigürasyonudur:
    A: global eşikleme (E45)
    B: global eşikleme + distance transform/watershed ayırma (E41)
    C: adaptif (yerel) eşikleme (E21)
Seçim kuralı (Ödev Bölüm 11):
    1) en düşük doğrulama MAE, 2) eşitlikte en düşük doğrulama RMSE,
    3) eşitlikte en düşük ortalama işlem süresi, 4) eşitlikte daha az işlem adımı
    (pipeline karmaşıklığı).
Baseline (E01) yalnızca karşılaştırma için raporlanır, aday değildir.
"""
import sys
sys.path.insert(0, "src")
import json
import pandas as pd
from evaluation import evaluate
from experiments import n_steps, describe_intensity, describe_filters, \
    describe_segmentation, describe_morphology

D = "data/Fluo-N2DH-GOWT1"
CANDIDATES = {"A": "E45", "B": "E41", "C": "E21"}

cfgs = json.load(open("experiment_configs.json"))
ex = pd.read_csv("experiments.csv").set_index("Deney ID")
r = pd.read_csv("dev_val_references.csv", dtype={"sequence": str})
val = r[r.group == "validation"]

summary_rows, frame_rows = [], []
for name, eid in [("Baseline", "E01")] + list(CANDIDATES.items()):
    cfg = cfgs[eid]
    s, pred = evaluate(D, val, cfg)
    summary_rows.append({
        "Pipeline": name, "Deney ID": eid, "Aday": name != "Baseline",
        "Yoğunluk": describe_intensity(cfg["intensity"]),
        "Filtre": describe_filters(cfg["filters"]),
        "Segment.": describe_segmentation(cfg["segmentation"]),
        "Morfoloji": describe_morphology(cfg),
        "min_area": cfg["min_area"],
        "Dev MAE": ex.loc[eid, "Count MAE"],
        "Val MAE": round(s["MAE"], 3), "Val RMSE": round(s["RMSE"], 3),
        "Val Bias": round(s["Bias"], 3), "Val Exact Acc": round(s["ExactAcc"], 3),
        "Ort. süre (s)": round(s["mean_time_s"], 4), "n_steps": n_steps(cfg),
    })
    for _, p in pred.iterrows():
        frame_rows.append({"Pipeline": name, "Deney ID": eid, "frame": p["frame"],
                           "reference_count": p["reference_count"],
                           "predicted_count": p["predicted_count"],
                           "error": p["predicted_count"] - p["reference_count"]})

summary = pd.DataFrame(summary_rows)
cand = summary[summary["Aday"]].sort_values(
    ["Val MAE", "Val RMSE", "Ort. süre (s)", "n_steps"])
chosen = cand.iloc[0]
summary["Seçildi"] = summary["Pipeline"] == chosen["Pipeline"]
summary.to_csv("validation_results.csv", index=False)
pd.DataFrame(frame_rows).to_csv("validation_per_frame.csv", index=False)

final = {
    "pipeline": chosen["Pipeline"],
    "source_experiment": chosen["Deney ID"],
    "selection_rule": "en düşük doğrulama MAE; eşitlikte doğrulama RMSE, ortalama işlem süresi, işlem adımı sayısı",
    "validation_MAE": float(chosen["Val MAE"]),
    "development_MAE": float(chosen["Dev MAE"]),
    "config": cfgs[chosen["Deney ID"]],
    # Bölüm 11: baseline yöntemi de doğrulama sonunda sabitlenir.
    "baseline": {"source_experiment": "E01", "config": cfgs["E01"]},
}
json.dump(final, open("final_pipeline.json", "w"), indent=2, ensure_ascii=False)

print(summary.drop(columns=["Yoğunluk", "Filtre", "Morfoloji"]).to_string(index=False))
print()
print(pd.DataFrame(frame_rows).pivot(index="frame", columns="Pipeline", values="predicted_count")
      .join(val.set_index("frame")["reference_count"]).to_string())
print("\nSeçilen:", chosen["Pipeline"], chosen["Deney ID"])
