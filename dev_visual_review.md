# Geliştirme Görüntülerinin Görsel İncelemesi

Ödevin 10.6. bölümü gereğince baseline yöntemi ile üç aday pipeline (A: E45, B: E41, C: E21) on geliştirme karesinin tamamında çalıştırılmış ve elde edilen çıktılar görsel olarak incelenmiştir. İncelemede kullanılan şekiller not defteri çalıştırıldığında `figures/fig_dev_check_*.png` dosyalarına kaydedilmektedir. Bu şekiller veri seti görüntülerinden üretildiği için ödevin 18.5. bölümü gereğince depoya yüklenmemiştir.

## Kare Bazında Sayımlar

| Kare | Referans | Baseline | A | B | C |
|---|---|---|---|---|---|
| 0 | 23 | 9 | 23 | 23 | 22 |
| 2 | 23 | 11 | 23 | 23 | 23 |
| 29 | 24 | 21 | 24 | 24 | 25 |
| 32 | 24 | 24 | 23 | 23 | 25 |
| 44 | 24 | 20 | 24 | 23 | 24 |
| 52 | 21 | 19 | 22 | 22 | 22 |
| 54 | 21 | 25 | 22 | 22 | 21 |
| 55 | 21 | 27 | 22 | 22 | 24 |
| 81 | 20 | 26 | 22 | 22 | 22 |
| 87 | 21 | 21 | 22 | 22 | 23 |

## Değerlendirme

Baseline yöntemi ilk karelerde (0 ve 2) soluk çekirdeklerin büyük bölümünü tespit edememiştir. Sonraki karelerde ise bazı çekirdekleri parçalara bölerek gerçek sayıdan fazla sayım yapmıştır. Bu iki hata türü birbirini kısmen dengelediği için baseline yönteminin ortalama mutlak hatası, yöntemin gerçek başarısından daha iyi görünmektedir.

A ve B adaylarının 52 ile 87 arasındaki karelerde gerçek sayıdan bir fazla sayım yapmasının temel nedeni, görüntünün sol kenarında kısmen görünen ve referansta işaretlenmemiş bir çekirdeğin nesne olarak sayılmasıdır. Aynı adaylarda 0, 32 ve 44 numaralı karelerde çok soluk bir çekirdeğin tespit edilemediği, buna karşılık sağ bölgedeki soluk ve birbirine yakın iki çekirdeğin düzensiz sınırlarla segmente edildiği gözlenmiştir. Bu iki etki bazı karelerde birbirini dengelemektedir.

B adayında uygulanan distance transform ve watershed ile nesne ayırma, A adayından yalnızca 44 numaralı karede farklı sonuç vermiştir. Geliştirme karelerinde birbirine temas eden çekirdek sayısı az olduğu için ayırma işleminin etkisi sınırlı kalmıştır.

C adayında kullanılan adaptif eşikleme, soluk çekirdeklerin çevresinde halka biçimli bölgeler oluşturmuş ve bu çekirdeklerin sınırları çift kontur olarak görülmüştür. C adayının 55, 81 ve 87 numaralı karelerde yaptığı iki ve üç hücrelik fazla sayımlar bu halka yapılarıyla birlikte gözlenmektedir.

87 numaralı karede referansta 45 piksellik küçük bir parça hücre olarak işaretlenmiştir. Bu parça 300 piksellik minimum alan eşiğinin altında kaldığı için adayların hiçbiri tarafından sayılmamıştır.
