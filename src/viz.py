"""Görselleştirme yardımcıları."""
import cv2
import numpy as np
from skimage.segmentation import find_boundaries


def display_stretch(img, p=99.7):
    hi = max(np.percentile(img, p), 1)
    return np.clip(img.astype(np.float32) / hi, 0, 1)


def overlay_labels(img, labels, ref_labels=None):
    """Tespit edilen nesnelerin sınırları yeşil; referans TRA işaretleri kırmızı nokta."""
    base = display_stretch(img)
    rgb = np.dstack([base, base, base])
    b = find_boundaries(labels, mode="outer")
    rgb[b] = [0, 1, 0]
    if ref_labels is not None:
        for i in np.unique(ref_labels)[1:]:
            ys, xs = np.where(ref_labels == i)
            cy, cx = int(ys.mean()), int(xs.mean())
            cv2.circle(rgb, (cx, cy), 6, (1, 0, 0), -1)
    return rgb
