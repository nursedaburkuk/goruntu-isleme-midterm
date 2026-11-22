"""Bölüm 12: Nihai pipeline'ın kilitlenmesi ve test tahminlerinin kaydedilmesi.

Bu betik test referans etiketlerini OKUMAZ. Yalnızca final_pipeline.json içindeki
nihai pipeline ve baseline konfigürasyonlarını test görüntülerine uygular ve sonuçları test_predictions_locked.csv
dosyasına yazar. Konfigürasyonların SHA-256 özetleri dosyaya eklenir; test
değerlendirmesi aynı özeti doğrulayarak yapılır.
"""
import sys
sys.path.insert(0, "src")
import os
import json
import hashlib
from datetime import datetime, timezone
import pandas as pd
from evaluation import predict_frames

D = "data/Fluo-N2DH-GOWT1"
OUT = "test_predictions_locked.csv"

if os.path.exists(OUT):
    raise FileExistsError(f"{OUT} zaten var. Kilitli tahminler yeniden üretilmez.")

final = json.load(open("final_pipeline.json"))
config = final["config"]
baseline_config = final["baseline"]["config"]
sha = lambda c: hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()

sel = pd.read_csv("selected_frames.csv", dtype={"sequence": str})
test = sel[sel["group"] == "test"][["sequence", "block", "frame", "filename"]].reset_index(drop=True)

# Bölüm 12.3-12.5: nihai pipeline ve baseline aynı test görüntülerinde çalıştırılır.
pb = predict_frames(D, test, baseline_config).rename(
    columns={"predicted_count": "baseline_predicted_count", "time_s": "baseline_time_s"})
pf = predict_frames(D, test, config).rename(
    columns={"predicted_count": "final_predicted_count", "time_s": "final_time_s"})
out = test.merge(pb[["frame", "baseline_predicted_count", "baseline_time_s"]], on="frame") \
          .merge(pf[["frame", "final_predicted_count", "final_time_s"]], on="frame")
out["final_pipeline"] = final["pipeline"] + " (" + final["source_experiment"] + ")"
out["final_config_sha256"] = sha(config)
out["baseline_config_sha256"] = sha(baseline_config)
out["locked_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out.to_csv(OUT, index=False)
print(out[["block", "frame", "filename", "baseline_predicted_count",
           "final_predicted_count"]].to_string(index=False))
print("final_config_sha256:", sha(config))
print("baseline_config_sha256:", sha(baseline_config))
