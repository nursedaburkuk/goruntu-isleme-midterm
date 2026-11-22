import sys; sys.path.insert(0, "src")
import json, pandas as pd
from experiments import run_all, choose_hist_match_reference
D = "data/Fluo-N2DH-GOWT1"
r = pd.read_csv("dev_val_references.csv", dtype={"sequence": str})
dev = r[r.group == "development"]
print("Histogram eşleme referansı: dev t%03d" % choose_hist_match_reference(D, dev))
df, cfgs = run_all(D, dev)
df.to_csv("experiments.csv", index=False)
json.dump(cfgs, open("experiment_configs.json", "w"), indent=1, ensure_ascii=False)

# Şekiller (geliştirme karesi 01/t052)
from figures_stage3 import fig_intensity, fig_grid, fig_parameter_effects
F = 52
fig_intensity(D, F, ["E02", "E03", "E04", "E05", "E06", "E07"], "figures/fig2_intensity.png")
fig_grid(D, F, ["E08", "E09", "E11", "E12", "E14", "E15"], "figures/fig_filters.png", "filtered",
         "Filtre karşılaştırması (HE -> [filtre] -> Otsu -> delik doldurma -> opening 5x5 -> min alan 300). Üst: filtre çıktısı, alt: sayım.")
fig_grid(D, F, ["E16", "E18", "E21", "E24", "E25"], "figures/fig3a_segmentation.png", "segmentation",
         "Segmentasyon karşılaştırması (HE -> Gaussian 9x9 -> [segmentasyon] -> delik doldurma -> opening 5x5 -> min alan 300). Üst: ham ikili maske.")
fig_grid(D, F, ["E26", "E29", "E31", "E34", "E36", "E37", "E41"], "figures/fig3b_morphology.png", "morphology",
         "Morfoloji karşılaştırması (HE -> Gaussian 9x9 -> Otsu -> [morfoloji] -> min alan 300). Üst: morfoloji sonrası maske.")
fig_parameter_effects("figures/fig_parameter_effects.png")
