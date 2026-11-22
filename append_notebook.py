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
