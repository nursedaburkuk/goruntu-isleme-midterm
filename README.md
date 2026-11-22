# Fluo-N2DH-GOWT1 Veri Setinde Klasik Görüntü İşleme ile Hücre Sayımı

Sayısal Görüntü İşleme dersi yüksek lisans midterm ödevi. Nurseda Akgül, öğrenci numarası 244329048.

## Projenin amacı

Bu projede floresan mikroskopi görüntülerindeki hücre çekirdekleri, yalnızca klasik görüntü işleme yöntemleri kullanılarak sayılmıştır. Yoğunluk dönüşümleri, filtreler, segmentasyon yöntemleri ve morfolojik işlemler geliştirme kümesinde kontrollü deneylerle karşılaştırılmıştır. Üç aday pipeline doğrulama kümesinde değerlendirilmiş ve nihai pipeline doğrulama sonucuna göre seçilmiştir. Nihai pipeline ve baseline, test referansları okunmadan önce kilitlenmiş ve bağımsız test kümesinde değerlendirilmiştir.

## Veri seti

- Veri seti: Cell Tracking Challenge, Fluo-N2DH-GOWT1 (GFP-GOWT1 fare embriyonik kök hücreleri), eğitim arşivi.
- Resmî indirme bağlantısı: https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DH-GOWT1.zip
- Veri setinin görüntüleri ve referans etiketleri bu repoya yüklenmemiştir. Veri setinden üretilen görüntü içeren şekiller de repoya yüklenmemiş, raporda sunulmuştur.

Zip dosyası indirilip repo klasöründe `data/` klasörüne açılmalıdır. Beklenen yapı şöyledir:

```
data/Fluo-N2DH-GOWT1/01/t000.tif ... t091.tif
data/Fluo-N2DH-GOWT1/01_GT/TRA/man_track000.tif ...
data/Fluo-N2DH-GOWT1/02/ ...
data/Fluo-N2DH-GOWT1/02_GT/TRA/ ...
```

## Random seed

Seed = öğrenci numarasının son 5 hanesi + 2026 = 29048 + 2026 = **31074**. Seçilen kareler `selected_frames.csv` dosyasındadır:

- Geliştirme (Sequence 01): 0, 2, 29, 32, 44, 52, 54, 55, 81, 87
- Doğrulama (Sequence 01): 12, 21, 62, 70, 72
- Test (Sequence 02): B1 = 17–21, B2 = 35–39, B3 = 72–76

## Yazılım gereksinimleri

Python 3.13 ile çalıştırılmıştır. Kütüphaneler ve sürümleri `requirements.txt` dosyasındadır:

```
pip install -r requirements.txt
```

## Çalıştırma

### Jupyter

```
git clone https://github.com/nursedaburkuk/goruntu-isleme-midterm.git
cd goruntu-isleme-midterm
pip install -r requirements.txt
mkdir data && unzip Fluo-N2DH-GOWT1.zip -d data/
jupyter notebook main.ipynb
```

### Google Colab

```
!git clone https://github.com/nursedaburkuk/goruntu-isleme-midterm.git
%cd goruntu-isleme-midterm
!pip install -r requirements.txt
!wget https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DH-GOWT1.zip
!mkdir -p data && unzip -q Fluo-N2DH-GOWT1.zip -d data/
```

Ardından `main.ipynb` açılır ve hücreler sırayla çalıştırılır.

### Çalıştırma sırası

`main.ipynb` bütün adımları sırasıyla çalıştırır. Aynı işlemler betiklerle şu sırada da yapılabilir:

1. `python src/data_selection.py`: görüntü seçimi, `selected_frames.csv`.
2. Not defterindeki Bölüm 4–5 hücreleri: geliştirme ve doğrulama referansları, baseline.
3. `python run_experiments.py`: 47 kontrollü deney, `experiments.csv` ve karşılaştırma şekilleri.
4. `python run_validation.py`: aday pipeline'ların doğrulaması, `validation_results.csv` ve `final_pipeline.json`.
5. `python run_test_predictions.py`: kilitli test tahminleri, `test_predictions_locked.csv`. Bu betik test referanslarını okumaz. Dosya zaten varsa yeniden üretmez.
6. `python run_test_evaluation.py`: test değerlendirmesi, `test_results.csv`.

Not: `test_predictions_locked.csv` repoda bulunduğu için 5. adım bu dosyayı yeniden üretmez. Kilitli tahminleri bağımsız olarak yeniden üretmek için dosya başka bir klasöre taşınıp 5. adım çalıştırılabilir. Tahminler aynı çıkar.

## Nihai pipeline

Histogram eşitleme → Gaussian 9×9 → Otsu eşikleme → delik doldurma → erosion 7×7 (elips) → 300 pikselden küçük bileşenlerin kaldırılması → 8-komşuluklu bağlı bileşen analizi ile sayım. Konfigürasyon `final_pipeline.json` dosyasındadır (deney E45, Pipeline A).

Baseline: gri seviye → Otsu → 8-komşuluklu bağlı bileşen analizi → 50 pikselden küçük bileşenlerin kaldırılması (deney E01).

## Sonuçların özeti

| Küme | Yöntem | MAE | RMSE | Bias |
|---|---|---|---|---|
| Doğrulama (5 kare) | Baseline | 3,20 | 5,14 | −2,80 |
| Doğrulama (5 kare) | Nihai pipeline | 1,20 | 1,27 | +0,80 |
| Test (15 kare) | Baseline | 7,47 | 8,45 | −7,47 |
| Test (15 kare) | Nihai pipeline | 2,87 | 3,04 | −2,87 |

## Commit geçmişi ve test güvenliği

1. Birinci commit: veri seçimi, deneyler, doğrulama ve nihai pipeline (Bölüm 1–11).
2. İkinci commit: nihai pipeline ve baseline kilitlendi, test tahminleri kaydedildi (Bölüm 12). Test referansları bu commit'e kadar okunmamıştır.
3. Üçüncü commit: test değerlendirmesi, zamansal analiz ve README (Bölüm 13–14).

`test_predictions_locked.csv` dosyası her iki yöntemin konfigürasyonunun SHA-256 özetini içerir. `run_test_evaluation.py` bu özetleri `final_pipeline.json` ile karşılaştırır ve eşleşmezse değerlendirmeyi durdurur.

## Dosyalar

| Dosya | İçerik |
|---|---|
| `main.ipynb` | Bütün adımları sırasıyla çalıştıran not defteri. Gömülü görüntü çıktıları temizlenmiştir (Bölüm 18.5). |
| `selected_frames.csv` | Seçilen kareler, veri grupları, test blokları, seed ve deneme sayıları. |
| `dev_val_references.csv` | Geliştirme ve doğrulama karelerinin referans hücre sayıları. |
| `baseline_min_area_dev.csv` | Baseline minimum alan eşiğinin geliştirme kümesinde seçimi. |
| `experiments.csv` | 47 kontrollü deneyin yöntemleri, parametreleri ve geliştirme metrikleri (MAE, RMSE, Bias, tam doğru oran, süre). |
| `experiment_configs.json` | Her deneyin tam konfigürasyonu. |
| `experiments_log.txt` | Deney çalıştırmasının çıktı kaydı. |
| `dev_visual_review.md` | Bütün geliştirme görüntülerinin görsel inceleme notları. |
| `validation_results.csv` | Baseline ve üç aday pipeline'ın doğrulama metrikleri ve seçim. |
| `validation_per_frame.csv` | Doğrulama kareleri için kare bazında tahminler. |
| `final_pipeline.json` | Nihai pipeline ve baseline konfigürasyonları, seçim kuralı. |
| `test_predictions_locked.csv` | Test referansları okunmadan kaydedilen baseline ve nihai pipeline tahminleri. |
| `test_results.csv` | Kare bazında test sonuçları, özet metrikler ve blok bazında metrikler. |
| `temporal_analysis.csv` | Test bloklarında ardışık karelerdeki sayım değişimleri. |
| `figures/fig1_flowchart.png` | Şekil 1: nihai pipeline akış diyagramı. |
| `figures/fig5_temporal.png` | Şekil 5: test bloklarında gerçek ve tahmin edilen hücre sayıları. |
| `figures/fig_parameter_effects.png` | Parametrelerin geliştirme MAE ve Bias üzerindeki etkisi. |
| `src/` | Seçim, referans, yöntem, değerlendirme, deney ve şekil modülleri. |

Not defteri çalıştırıldığında veri seti görüntülerinden üretilen diğer şekiller (Şekil 2, 3, 4, 6 ve kontrol şekilleri) yerel `figures/` klasörüne yazılır. Bu şekiller `.gitignore` ile repodan hariç tutulmuştur.
