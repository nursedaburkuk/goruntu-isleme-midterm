"""Bölüm 13: Bağımsız test performansının ölçülmesi.

Bu betik test_predictions_locked.csv dosyasındaki kilitli tahminleri DEĞİŞTİRMEZ
ve yeniden hesaplamaz. Önce kilitli dosyadaki konfigürasyon özetlerinin
final_pipeline.json ile aynı olduğunu doğrular, sonra test referans sayılarını
okuyarak metrikleri hesaplar.
"""
import sys
sys.path.insert(0, "src")
import json
import hashlib
import pandas as pd
from references import reference_counts
from evaluation import mae, rmse, bias, exact_accuracy

D = "data/Fluo-N2DH-GOWT1"

locked = pd.read_csv("test_predictions_locked.csv", dtype={"sequence": str})
final = json.load(open("final_pipeline.json"))
sha = lambda c: hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()
assert (locked["final_config_sha256"] == sha(final["config"])).all(), "Nihai konfigürasyon değişmiş!"
assert (locked["baseline_config_sha256"] == sha(final["baseline"]["config"])).all(), "Baseline değişmiş!"
print("Kilitli konfigürasyon özetleri doğrulandı.")

# Test referansları yalnızca bu noktada okunur (kilitli dosya mevcut).
sel = pd.read_csv("selected_frames.csv", dtype={"sequence": str})
ref = reference_counts(D, sel, "test")[["frame", "reference_count"]]

res = locked.merge(ref, on="frame")
res["baseline_abs_error"] = (res["baseline_predicted_count"] - res["reference_count"]).abs()
res["final_abs_error"] = (res["final_predicted_count"] - res["reference_count"]).abs()
res["baseline_error"] = res["baseline_predicted_count"] - res["reference_count"]
res["final_error"] = res["final_predicted_count"] - res["reference_count"]

per_frame = res[["block", "sequence", "frame", "filename", "reference_count",
                 "baseline_predicted_count", "final_predicted_count",
                 "baseline_error", "final_error", "baseline_abs_error", "final_abs_error",
                 "baseline_time_s", "final_time_s"]].copy()
per_frame.insert(0, "row_type", "frame")

summary = []
for name, col, tcol in [("Baseline", "baseline_predicted_count", "baseline_time_s"),
                        ("Nihai pipeline", "final_predicted_count", "final_time_s")]:
    r, p = res["reference_count"], res[col]
    summary.append({"row_type": "summary", "method": name,
                    "MAE": round(mae(r, p), 4), "RMSE": round(rmse(r, p), 4),
                    "Bias": round(bias(r, p), 4), "ExactAcc": round(exact_accuracy(r, p), 4),
                    "mean_time_s": round(res[tcol].mean(), 4)})
    for b, g in res.groupby("block"):
        summary.append({"row_type": "summary_block", "method": name, "block": b,
                        "MAE": round(mae(g["reference_count"], g[col]), 4),
                        "RMSE": round(rmse(g["reference_count"], g[col]), 4),
                        "Bias": round(bias(g["reference_count"], g[col]), 4),
                        "ExactAcc": round(exact_accuracy(g["reference_count"], g[col]), 4),
                        "mean_time_s": round(g[tcol].mean(), 4)})
summary = pd.DataFrame(summary)

out = pd.concat([per_frame, summary], ignore_index=True)
out.to_csv("test_results.csv", index=False)

pd.set_option("display.width", 200)
print(per_frame[["block", "frame", "reference_count", "baseline_predicted_count",
                 "final_predicted_count", "baseline_abs_error", "final_abs_error"]].to_string(index=False))
print()
print(summary.drop(columns=["row_type"]).to_string(index=False))
