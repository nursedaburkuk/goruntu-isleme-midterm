"""main.ipynb dosyasını oluşturur. Bölüm 12-13 hücreleri ayrı aşamalarda eklenir."""
import sys
import nbformat as nbf

STAGE = sys.argv[1] if len(sys.argv) > 1 else "validation"

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
cells = [
    md("# Sayısal Görüntü İşleme Midterm Ödevi: Fluo-N2DH-GOWT1 Hücre Sayımı\n\n"
       "Öğrenci numarası: 244329048. Seed = 29048 + 2026 = 31074.\n\n"
       "Bu not defteri ödevdeki bütün adımları sırasıyla yeniden üretir. Veri seti "
       "`data/Fluo-N2DH-GOWT1/` klasöründe bulunmalıdır (bkz. README.md).\n\n"
       "**Not (Bölüm 18.5):** Veri seti görüntülerinden üretilen şekiller GitHub'a yüklenmez. "
       "Not defterinin repodaki sürümünde gömülü görüntü çıktıları temizlenmiştir. Şekiller "
       "not defteri çalıştırıldığında `figures/` klasörüne yeniden üretilir ve raporda sunulmuştur."),
    code("import sys, json\nsys.path.insert(0, 'src')\nimport numpy as np, pandas as pd\n"
         "import cv2, skimage, scipy, matplotlib\n"
         "from IPython.display import Image, display\n"
         "D = 'data/Fluo-N2DH-GOWT1'\n"
         "print('OpenCV', cv2.__version__, '| scikit-image', skimage.__version__, '| SciPy', scipy.__version__,\n"
         "      '| NumPy', np.__version__, '| pandas', pd.__version__, '| Matplotlib', matplotlib.__version__)"),

    md("## 1-2. Veri seti inceleme\n\nİki sekansın kare sayısı, görüntü boyutu, veri tipi ve yoğunluk "
       "istatistikleri hesaplanır. Bu aşamada referans etiketleri kullanılmaz."),
    code("import glob\nrows = []\nfor s in ['01', '02']:\n"
         "    fs = sorted(glob.glob(f'{D}/{s}/t*.tif'))\n"
         "    ims = [cv2.imread(f, cv2.IMREAD_UNCHANGED) for f in fs]\n"
         "    a = np.stack(ims).astype(float)\n"
         "    rows.append(dict(sequence=s, n_frames=len(fs), shape=ims[0].shape, dtype=str(ims[0].dtype),\n"
         "                     min=a.min(), max=a.max(), mean_range=(round(a.mean((1,2)).min(),2), round(a.mean((1,2)).max(),2)),\n"
         "                     p99_mean=round(float(np.percentile(a.reshape(len(fs),-1), 99, axis=1).mean()),1)))\n"
         "pd.DataFrame(rows)"),
    code("display(Image('figures/fig0_data_inspection.png'))"),

    md("## 3. Seed ile görüntü seçimi\n\n\"En az 5 karelik boşluk\", iki kare arasında en az 5 kare "
       "bulunması (kare numarası farkı ≥ 6) olarak uygulanmıştır. Koşullar sağlanmadığında aynı RNG "
       "ile yeniden çekim yapılır; deneme sayıları kaydedilir."),
    code("from data_selection import select_frames, SEED\nsel = select_frames(D)\n"
         "sel.to_csv('selected_frames.csv', index=False)\nprint('Seed:', SEED)\n"
         "sel.groupby('group')['frame'].apply(list)"),

    md("## 4. Referans hücre sayıları (geliştirme ve doğrulama)\n\nTRA etiket görüntüsünde 0 dışındaki "
       "farklı hücre kimlikleri sayılır. Test referansları kilitli tahminler kaydedilmeden okunamaz."),
    code("from references import reference_counts\nsel = pd.read_csv('selected_frames.csv', dtype={'sequence': str})\n"
         "refs = pd.concat([reference_counts(D, sel, 'development'), reference_counts(D, sel, 'validation')])\n"
         "refs[['group','sequence','frame','filename','reference_count']].to_csv('dev_val_references.csv', index=False)\n"
         "refs[['group','frame','reference_count']]"),
    code("try:\n    reference_counts(D, sel, 'test')\nexcept PermissionError as e:\n    print('Koruma çalışıyor:', e)"),
    code("for f in ['figures/fig_ref_check_dev.png', 'figures/fig_ref_check_small.png', 'figures/fig_ref_check_remaining.png']:\n"
         "    display(Image(f))"),

    md("## 5. Baseline\n\nGri seviye → Otsu → 8-komşuluklu bağlı bileşen analizi → sayım. Minimum alan "
       "eşiği geliştirme kümesinde 12 değer arasından en düşük MAE ile seçilmiştir (50 px)."),
    code("from methods import BASELINE_TEMPLATE, with_changes\nfrom evaluation import evaluate\n"
         "dev = refs[refs.group == 'development']\nrows = []\n"
         "for a in [0, 10, 25, 50, 100, 200, 300, 400, 500, 600, 800, 1000]:\n"
         "    s, _ = evaluate(D, dev, with_changes(BASELINE_TEMPLATE, min_area=a))\n"
         "    rows.append(dict(min_area=a, **{k: round(v, 4) for k, v in s.items()}))\n"
         "bl = pd.DataFrame(rows); bl.to_csv('baseline_min_area_dev.csv', index=False); bl"),
    code("display(Image('figures/fig_baseline_dev.png'))"),

    md("## 6-10. Kontrollü deneyler (yalnızca geliştirme kümesi)\n\nHer aşamada önceki aşamanın en iyi "
       "konfigürasyonu ebeveyn alınır ve yalnızca o aşamanın konusu değiştirilir. Sonuçlar "
       "`experiments.csv` dosyasına yazılır ve şekiller yeniden üretilir."),
    code("%run run_experiments.py\npd.read_csv('experiments.csv')[['Deney ID','Aşama','Deney','Count MAE','RMSE','Bias','Exact Acc','Ort. süre (s)']]"),
    code("for f in ['fig2_intensity', 'fig_filters', 'fig3a_segmentation', 'fig3b_morphology', 'fig_parameter_effects']:\n"
         "    display(Image(f'figures/{f}.png'))"),

    md("### 10.6. Bütün geliştirme görüntülerinin görsel incelemesi\n\nBaseline ve üç aday pipeline'ın "
       "10 geliştirme karesindeki çıktıları çizilir. İnceleme notları `dev_visual_review.md` dosyasındadır."),
    code("from figures_dev_check import fig_dev_all\ncfgs = json.load(open('experiment_configs.json'))\n"
         "dev_frames = refs[refs.group == 'development']['frame'].tolist()\n"
         "for n, e in [('Baseline', 'E01'), ('A', 'E45'), ('B', 'E41'), ('C', 'E21')]:\n"
         "    fig_dev_all(D, dev_frames, cfgs[e], f'Geliştirme kareleri, {n} ({e})', f'figures/fig_dev_check_{n}.png')\n"
         "    display(Image(f'figures/fig_dev_check_{n}.png'))"),

    md("## 11. Aday pipeline'ların doğrulanması ve nihai seçim\n\nSeçim kuralı (Bölüm 11): en düşük "
       "doğrulama MAE; eşitlikte doğrulama RMSE, ortalama işlem süresi ve pipeline karmaşıklığı (işlem adımı sayısı). "
       "Baseline yöntemi de bu aşamada `final_pipeline.json` içinde sabitlenir."),
    code("%run run_validation.py"),
    code("from figures_validation import fig_validation\nfp = json.load(open('final_pipeline.json'))\n"
         "fig_validation(D, [12, 21, 62, 70, 72], fp['config'], 'Doğrulama kareleri, Pipeline A (E45)', 'figures/fig4_validation.png')\n"
         "display(Image('figures/fig4_validation.png'))"),
]

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbf.write(nb, "main.ipynb")
print("main.ipynb yazıldı:", len(cells), "hücre")
