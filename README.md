# Fluo-N2DH-GOWT1 Veri Setinde Klasik Görüntü İşleme ile Hücre Sayımı

Bu depo, Sayısal Görüntü İşleme dersi yüksek lisans ara sınav ödevi kapsamında hazırlanmıştır. Hazırlayan: Nurseda Akgül (244329048).

## Çalışmanın Amacı

Bu çalışmada floresan mikroskopi görüntülerindeki hücre çekirdeklerinin yalnızca klasik görüntü işleme yöntemleri kullanılarak sayılması amaçlanmıştır. Yoğunluk dönüşümleri, filtreler, segmentasyon yöntemleri ve morfolojik işlemler geliştirme kümesinde kontrollü deneylerle karşılaştırılmıştır. Bu deneyler sonucunda belirlenen üç aday pipeline doğrulama kümesinde değerlendirilmiş ve nihai yöntem doğrulama sonuçlarına göre seçilmiştir. Nihai yöntem ile baseline yöntemi, test referanslarına erişilmeden önce kilitlenmiş ve ardından bağımsız test kümesinde değerlendirilmiştir.

## Veri Seti

Çalışmada Cell Tracking Challenge kapsamında yayımlanan Fluo-N2DH-GOWT1 eğitim veri seti kullanılmıştır. Veri seti aşağıdaki resmî bağlantıdan indirilebilir:

https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DH-GOWT1.zip

Veri setine ait görüntüler ve referans etiketleri bu depoya yüklenmemiştir. Veri seti görüntülerinden üretilen şekiller de depoda yer almamakta olup teknik raporda sunulmuştur. İndirilen arşivin depo klasörü içinde `data/` klasörüne açılması gerekmektedir. Beklenen klasör yapısı aşağıda verilmiştir:

```
data/Fluo-N2DH-GOWT1/01/t000.tif ... t091.tif
data/Fluo-N2DH-GOWT1/01_GT/TRA/man_track000.tif ...
data/Fluo-N2DH-GOWT1/02/ ...
data/Fluo-N2DH-GOWT1/02_GT/TRA/ ...
```

## Rastgele Seçim ve Seed Değeri

Görüntü seçiminde kullanılan seed değeri, öğrenci numarasının son beş hanesine 2026 eklenerek 31074 olarak hesaplanmıştır. Bu değerle seçilen geliştirme kareleri 01 sekansının 0, 2, 29, 32, 44, 52, 54, 55, 81 ve 87 numaralı kareleridir. Doğrulama kareleri aynı sekansın 12, 21, 62, 70 ve 72 numaralı kareleridir. Test kümesi ise 02 sekansından alınan ve her biri ardışık beş kareden oluşan üç bloktan meydana gelmektedir: 17–21, 35–39 ve 72–76. Seçimin tüm ayrıntıları `selected_frames.csv` dosyasında yer almaktadır.

## Yazılım Gereksinimleri

Uygulamalar Python 3.13 ile gerçekleştirilmiştir. Kullanılan kütüphaneler ve sürümleri `requirements.txt` dosyasında listelenmiştir ve aşağıdaki komutla kurulabilir:

```
pip install -r requirements.txt
```

## Çalıştırma

Jupyter ortamında çalıştırmak için aşağıdaki adımlar izlenmelidir:

```
git clone https://github.com/nursedaburkuk/goruntu-isleme-midterm.git
cd goruntu-isleme-midterm
pip install -r requirements.txt
mkdir data && unzip Fluo-N2DH-GOWT1.zip -d data/
jupyter notebook main.ipynb
```

Google Colab ortamında ise aşağıdaki komutlar çalıştırıldıktan sonra `main.ipynb` açılmalı ve hücreler sırasıyla çalıştırılmalıdır:

```
!git clone https://github.com/nursedaburkuk/goruntu-isleme-midterm.git
%cd goruntu-isleme-midterm
!pip install -r requirements.txt
!wget https://data.celltrackingchallenge.net/training-datasets/Fluo-N2DH-GOWT1.zip
!mkdir -p data && unzip -q Fluo-N2DH-GOWT1.zip -d data/
```

`main.ipynb` not defteri, ödevdeki tüm adımları sırasıyla yeniden üretmektedir. Not defteri hesaplamaları `src/` klasöründeki modüllerden ve kök klasördeki betiklerden çağırmaktadır. Aynı adımlar betikler aracılığıyla da şu sırayla çalıştırılabilir: görüntü seçimi için `src/data_selection.py`, kontrollü deneyler için `run_experiments.py`, aday pipeline'ların doğrulanması için `run_validation.py`, kilitli test tahminlerinin üretilmesi için `run_test_predictions.py` ve test değerlendirmesi için `run_test_evaluation.py`. Test tahmin betiği test referanslarını okumamaktadır. Ayrıca `test_predictions_locked.csv` dosyası mevcut olduğunda bu dosyayı yeniden üretmemektedir. Kilitli tahminlerin bağımsız olarak yeniden üretilmesi isteniyorsa bu dosyanın başka bir klasöre taşınması yeterlidir. Bu durumda aynı tahminler elde edilmektedir.

## Nihai Yöntem

Nihai pipeline sırasıyla histogram eşitleme, 9×9 Gaussian filtre, Otsu eşiklemesi, 7×7 eliptik yapılandırma elemanıyla erosion, delik doldurma, 300 pikselden küçük bileşenlerin kaldırılması ve 8-komşuluklu bağlı bileşen analizinden oluşmaktadır. Baseline yöntemi ise gri seviyeli görüntüye Otsu eşiklemesi ve 8-komşuluklu bağlı bileşen analizi uygulanmasıyla, 50 pikselden küçük bileşenler sayılmadan oluşturulmuştur. Her iki yöntemin tüm parametreleri `final_pipeline.json` dosyasında kayıtlıdır.

## Sonuçların Özeti

Doğrulama kümesinde (5 kare) baseline yönteminin ortalama mutlak hatası (MAE) 3,20, nihai pipeline'ın ise 1,20 olarak bulunmuştur. Bağımsız test kümesinde (15 kare) baseline yöntemi 7,47, nihai pipeline ise 2,87 MAE değerine ulaşmıştır. Nihai pipeline test kümesinde tüm karelerde gerçek sayının altında tahmin üretmiştir. Bu durum, daha karanlık olan 02 sekansındaki arka plana çok yakın yoğunluktaki çekirdeklerin tespit edilememesiyle açıklanmaktadır. Ayrıntılı sonuçlar ve tartışma teknik raporda yer almaktadır.

| Küme | Yöntem | MAE | RMSE | Bias |
|---|---|---|---|---|
| Doğrulama (5 kare) | Baseline | 3,20 | 5,14 | −2,80 |
| Doğrulama (5 kare) | Nihai pipeline | 1,20 | 1,27 | +0,80 |
| Test (15 kare) | Baseline | 7,47 | 8,45 | −7,47 |
| Test (15 kare) | Nihai pipeline | 2,87 | 3,04 | −2,87 |

## Test Güvenliği ve Commit Geçmişi

Ödevde istenen test güvenliği koşulu, commit geçmişi aracılığıyla belgelenmiştir. İlk commit veri seçimini, deneyleri, doğrulamayı ve nihai yöntemin belirlenmesini içermektedir. İkinci commit, nihai pipeline ile baseline yönteminin kilitlendiğini ve test tahminlerinin referanslar okunmadan kaydedildiğini göstermektedir. Test değerlendirmesi ve sonraki analizler bu commit'ten sonra eklenmiştir. `test_predictions_locked.csv` dosyası her iki yöntemin konfigürasyonuna ait SHA-256 özetlerini içermektedir. `run_test_evaluation.py` betiği bu özetleri `final_pipeline.json` dosyasıyla karşılaştırmakta ve bir uyuşmazlık bulunduğunda değerlendirmeyi durdurmaktadır.

## Dosyalar

| Dosya | Açıklama |
|---|---|
| `main.ipynb` | Tüm adımları sırasıyla yeniden üreten not defteridir. Veri seti görüntülerinden üretilen gömülü çıktılar temizlenmiştir. |
| `selected_frames.csv` | Seçilen kareleri, veri gruplarını, test bloklarını, seed değerini ve seçim deneme sayılarını içerir. |
| `dev_val_references.csv` | Geliştirme ve doğrulama karelerinin referans hücre sayılarını içerir. |
| `baseline_min_area_dev.csv` | Baseline yöntemi için minimum alan eşiğinin geliştirme kümesinde belirlenmesine ait sonuçları içerir. |
| `experiments.csv` | 47 kontrollü deneyin yöntemlerini, parametrelerini ve geliştirme kümesi metriklerini içerir. |
| `experiment_configs.json` | Her deneyin tam konfigürasyonunu içerir. |
| `experiments_log.txt` | Deneylerin çalıştırılmasına ait çıktı kaydıdır. |
| `dev_visual_review.md` | Geliştirme görüntülerinin görsel incelemesine ait notları içerir. |
| `validation_results.csv` | Baseline ve üç aday pipeline'ın doğrulama metriklerini ve seçim sonucunu içerir. |
| `validation_per_frame.csv` | Doğrulama kareleri için kare bazında tahminleri içerir. |
| `final_pipeline.json` | Nihai pipeline ile baseline yönteminin konfigürasyonlarını ve seçim kuralını içerir. |
| `test_predictions_locked.csv` | Test referansları okunmadan kaydedilen baseline ve nihai pipeline tahminlerini içerir. |
| `test_results.csv` | Test kümesine ait kare bazında sonuçları, özet metrikleri ve blok bazında metrikleri içerir. |
| `temporal_analysis.csv` | Test bloklarında ardışık kareler arasındaki sayım değişimlerini içerir. |
| `error_analysis.csv` | Tespit edilemeyen, birleşmiş ve sahte nesnelere ait hata analizini içerir. |
| `figures/` | Veri seti görüntüsü içermeyen şekilleri (akış diyagramı, zamansal grafik ve parametre etkileri) içerir. |
| `src/` | Görüntü seçimi, referans okuma, görüntü işleme yöntemleri, değerlendirme, deneyler ve şekil üretimine ait modülleri içerir. |

Not defteri çalıştırıldığında veri seti görüntülerinden üretilen diğer şekiller yerel `figures/` klasörüne kaydedilmektedir. Bu şekiller `.gitignore` dosyası aracılığıyla depo dışında tutulmuştur.
