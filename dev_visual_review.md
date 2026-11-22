# Geliştirme görüntülerinin görsel incelemesi (Ödev Bölüm 10.6)

Baseline (E01) ve üç aday pipeline (A: E45, B: E41, C: E21) 10 geliştirme karesinin tamamında çalıştırılmış ve çıktılar görsel olarak incelenmiştir. Şekiller not defteri çalıştırıldığında `figures/fig_dev_check_*.png` dosyalarına üretilir. Bölüm 18.5 gereği bu şekiller repoya yüklenmemiştir.

## Kare bazında sayımlar

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

## Gözlemler

1. Baseline, ilk karelerde (0 ve 2) soluk hücrelerin büyük bölümünü bulamamaktadır. Sonraki karelerde ise bazı hücreleri parçalara bölerek fazla saymaktadır. Bu iki hata türü birbirini kısmen dengelediği için baseline'ın MAE değeri gerçek başarısından daha iyi görünmektedir.
2. A ve B adaylarında 52–87 numaralı karelerdeki +1 hatanın ana nedeni, görüntünün sol kenarında kısmen görünen ve referansta işaretlenmemiş çekirdeğin bir nesne olarak sayılmasıdır.
3. A ve B adaylarında 0, 32 ve 44 numaralı karelerde, çok soluk bir hücre bulunamamakta, buna karşılık sağ taraftaki soluk ve birbirine yakın hücre çifti düzensiz sınırlarla segmente edilmektedir. Bu iki etki bazı karelerde birbirini dengelemektedir.
4. B adayındaki distance transform ve watershed ayırması, A adayından yalnızca 44 numaralı karede farklı sonuç vermiştir. Bu veride birbirine temas eden çekirdek sayısı az olduğu için ayırma işleminin etkisi sınırlıdır.
5. C adayında (adaptif eşikleme) soluk hücrelerin çevresinde halka biçimli bölgeler oluşmakta ve bu hücrelerin sınırları çift kontur olarak görünmektedir. C adayının 55, 81 ve 87 numaralı karelerdeki +2 ve +3 hataları bu halka yapılarıyla birlikte görülmektedir.
6. 87 numaralı karede referansta 45 piksellik küçük bir parça hücre olarak işaretlenmiştir. Bu parça minimum alan eşiğinin (300 piksel) altında kaldığı için hiçbir aday tarafından sayılmamaktadır.
