"""Ödev Bölüm 18.5: GitHub'a yüklenen not defterinde veri setinden üretilmiş
gömülü görüntü çıktıları bulunmamalıdır. Bu fonksiyon bütün görüntü çıktılarını
(image/png, image/jpeg) kaldırır; metin ve tablo çıktıları korunur."""


def strip_image_outputs(nb):
    removed = 0
    for cell in nb.cells:
        if cell.get("cell_type") != "code":
            continue
        kept = []
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if any(k.startswith("image/") for k in data):
                removed += 1
                continue
            kept.append(out)
        cell["outputs"] = kept
    return removed
