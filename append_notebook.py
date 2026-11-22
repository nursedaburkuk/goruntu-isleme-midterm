"""main.ipynb'ye yeni bölüm hücreleri ekler ve yalnızca kurulum hücresi ile yeni
hücreleri çalıştırır. Önceki hücreler yeniden çalıştırılmaz; böylece kilitli
aşamalardan önceki çıktılar değişmez.

Kullanım: python append_notebook.py lock   |   python append_notebook.py test
"""
import sys
import nbformat as nbf
sys.path.insert(0, 'src')
from notebook_utils import strip_image_outputs
from nbclient import NotebookClient

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

SECTIONS = {
    "lock": [
        md("## 12. Nihai pipeline'ın kilitlenmesi ve test tahminleri\n\n"
           "Nihai konfigürasyon `final_pipeline.json` dosyasından okunur ve SHA-256 özeti alınır. "
           "Test görüntüleri işlenir, tahminler `test_predictions_locked.csv` dosyasına yazılır. "
           "Bu hücre test referanslarını okumaz. Tahminler ayrı bir commit ile kaydedilmiştir; "
           "test değerlendirmesi (Bölüm 13) bu commit'ten sonra yapılmıştır."),
        code("%run run_test_predictions.py"),
    ],
    "test": [
        md("## 13. Bağımsız test performansı\n\nKilitli dosyadaki konfigürasyon özetleri `final_pipeline.json` ile "
           "karşılaştırılarak doğrulanır. Test referans sayıları yalnızca bu aşamada okunur. Kilitli tahminler "
           "değiştirilmez ve yeniden hesaplanmaz. Sonuçlar `test_results.csv` dosyasına yazılır."),
        code("%run run_test_evaluation.py"),
        md("## 14. Ardışık görüntülerde zamansal analiz ve zorunlu şekiller\n\n"
           "Şekil 1 (akış diyagramı) ve Şekil 5 (zamansal grafik) veri seti görüntüsü içermediği için repoda "
           "bulunur. Şekil 4 ve Şekil 6 veri seti görüntülerinden üretildiği için repoya yüklenmez."),
        code("from figures_test import fig_temporal, fig_flowchart, fig_stages, fig_examples\n"
             "fp = json.load(open('final_pipeline.json'))\n"
             "fig_flowchart('figures/fig1_flowchart.png')\n"
             "fig_stages(D, '01', 52, fp['config'], 'figures/fig4_stages.png')\n"
             "fig_temporal('test_results.csv', 'figures/fig5_temporal.png')\n"
             "items = [('(a) Başarılı: en düşük hata', '02', 17, None),\n"
             "         ('(b) Hatalı: en yüksek hata', '02', 75, None),\n"
             "         ('(c) Zorlayıcı: bölünen hücre ve düzensiz soluk çekirdek', '02', 35, (0, 350, 250, 900)),\n"
             "         ('(d) Zorlayıcı: çok soluk çekirdekler', '02', 72, (0, 480, 0, 420))]\n"
             "fig_examples(D, items, fp['config'], fp['baseline']['config'], 'figures/fig6_examples.png')\n"
             "for f in ['fig1_flowchart', 'fig4_stages', 'fig5_temporal', 'fig6_examples']:\n"
             "    display(Image(f'figures/{f}.png'))"),
        code("tr = pd.read_csv('test_results.csv'); fr = tr[tr.row_type == 'frame']\n"
             "rows = []\n"
             "for b, g in fr.groupby('block'):\n"
             "    g = g.sort_values('frame')\n"
             "    for col, name in [('reference_count', 'Gerçek'), ('baseline_predicted_count', 'Baseline'),\n"
             "                      ('final_predicted_count', 'Nihai')]:\n"
             "        d = g[col].diff().dropna()\n"
             "        rows.append(dict(blok=b, seri=name, sayımlar=g[col].astype(int).tolist(),\n"
             "                         ardışık_değişimler=d.astype(int).tolist(),\n"
             "                         ort_mutlak_değişim=round(d.abs().mean(), 2), en_büyük_sıçrama=int(d.abs().max())))\n"
             "temporal = pd.DataFrame(rows); temporal.to_csv('temporal_analysis.csv', index=False); temporal"),
    ],
    "analysis": [
        md("## 15. Hata ayrıştırması (yalnızca analiz)\n\nNihai pipeline değiştirilmeden, her referans hücre "
           "işaretinin hangi tahmin nesnesiyle örtüştüğü incelenir. Kaçırılan hücre, hiçbir nesneyle örtüşmeyen "
           "referanstır; birleşmiş nesne, birden fazla referans içeren nesnedir; sahte nesne, hiçbir referans "
           "içermeyen nesnedir. Sonuçlar `error_analysis.csv` dosyasına yazılır."),
        code("from error_analysis import decompose_set\nfp = json.load(open('final_pipeline.json'))\n"
             "ea = pd.concat([decompose_set(D, [12, 21, 62, 70, 72], fp['config'], '01').assign(group='validation'),\n"
             "                decompose_set(D, [17, 18, 19, 20, 21, 35, 36, 37, 38, 39, 72, 73, 74, 75, 76], fp['config'], '02').assign(group='test')])\n"
             "ea.to_csv('error_analysis.csv', index=False)\n"
             "ea.groupby('group')[['reference', 'predicted', 'missed', 'merged_lost', 'false_positive']].sum()"),
        code("# Şekil 1, 4 ve 6 düzeltilmiş etiketlerle yeniden üretilir (pipeline ve tahminler değişmez).\n"
             "from figures_test import fig_flowchart, fig_stages, fig_examples\n"
             "fig_flowchart('figures/fig1_flowchart.png')\n"
             "fig_stages(D, '01', 52, fp['config'], 'figures/fig4_stages.png')\n"
             "items = [('(a) Başarılı: en düşük hata', '02', 17, None),\n"
             "         ('(b) Hatalı: en yüksek hata', '02', 75, None),\n"
             "         ('(c) Zorlayıcı: bölünen hücre ve düzensiz soluk çekirdek', '02', 35, (0, 350, 250, 900)),\n"
             "         ('(d) Zorlayıcı: çok soluk çekirdekler', '02', 72, (0, 480, 0, 420))]\n"
             "fig_examples(D, items, fp['config'], fp['baseline']['config'], 'figures/fig6_examples.png')"),
    ],
    "report": [
        md("## 16. Rapor şekilleri\n\nRaporda sayfa yerini azaltmak için Şekil 2, 3 ve 6'nın kompakt sürümleri kullanılmıştır. "
           "Yöntem ve sonuçlar değişmez. Bu şekiller veri seti görüntüsü içerdiği için repoya yüklenmez."),
        code("from experiments import choose_hist_match_reference\n"
             "from figures_report import fig2_compact, fig3_compact, fig6_compact\n"
             "choose_hist_match_reference(D, refs[refs.group == 'development'] if 'refs' in dir() else "
             "pd.read_csv('dev_val_references.csv', dtype={'sequence': str}).query(\"group == 'development'\"))\n"
             "fp = json.load(open('final_pipeline.json'))\n"
             "fig2_compact(D, 52, ['E02', 'E03', 'E04', 'E05', 'E06', 'E07'], 'figures/report_fig2.png')\n"
             "fig3_compact(D, 52, ['E16', 'E18', 'E21', 'E24', 'E25'], ['E26', 'E29', 'E31', 'E34', 'E36'], 'figures/report_fig3.png')\n"
             "fig6_compact(D, [('(a) Başarılı', '02', 17, None), ('(b) Hatalı', '02', 75, None),\n"
             "                 ('(c) Zorlayıcı: bölünen hücre', '02', 35, (0, 440, 440, 900)),\n"
             "                 ('(d) Zorlayıcı: çok soluk çekirdekler', '02', 72, (0, 440, 0, 440))],\n"
             "             fp['config'], fp['baseline']['config'], 'figures/report_fig6.png')"),
    ],
}

stage = sys.argv[1]
nb = nbf.read("main.ipynb", as_version=4)
start = len(nb.cells)
nb.cells.extend(SECTIONS[stage])

client = NotebookClient(nb, timeout=1200, kernel_name="python3", resources={"metadata": {"path": "."}})
with client.setup_kernel():
    client.execute_cell(nb.cells[1], 1)  # kurulum hücresi (importlar); çıktısı aynı kalır
    for i in range(start, len(nb.cells)):
        client.execute_cell(nb.cells[i], i)
print("Kaldırılan görüntü çıktısı:", strip_image_outputs(nb))
nbf.write(nb, "main.ipynb")
print(f"{len(nb.cells) - start} hücre eklendi ve çalıştırıldı")
