"""Klasik görüntü işleme yöntemleri ve konfigürasyonla çalışan pipeline.

Bir pipeline, aşağıdaki anahtarlara sahip bir sözlükle (config) tanımlanır:
    intensity    : yoğunluk dönüşümü        (Bölüm 6)
    filters      : sıralı filtre listesi     (Bölüm 7)
    segmentation : ikili segmentasyon        (Bölüm 8)
    morphology   : sıralı morfoloji listesi  (Bölüm 9)
    fill_holes   : ikili maskedeki deliklerin doldurulması (True/False)
    separation   : temas eden hücrelerin ayrılması (Bölüm 9)
    min_area     : bu alandan küçük bağlı bölgeler sayılmaz (piksel)
"""
import os
import time
import copy
import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage import exposure, segmentation as sk_seg, feature


# ----------------------------------------------------------------------------
# Okuma
# ----------------------------------------------------------------------------
def image_path(data_dir, sequence, frame):
    return os.path.join(data_dir, sequence, f"t{frame:03d}.tif")


def read_gray(data_dir, sequence, frame):
    """Gri seviyeli (uint8) görüntüyü okur."""
    return cv2.imread(image_path(data_dir, sequence, frame), cv2.IMREAD_GRAYSCALE)


# ----------------------------------------------------------------------------
# Bölüm 6: Yoğunluk dönüşümleri
# ----------------------------------------------------------------------------
_HIST_MATCH_REFERENCE = {}


def set_histogram_matching_reference(name, image):
    """Histogram eşleme referansı (yalnızca geliştirme kümesinden)."""
    _HIST_MATCH_REFERENCE[name] = image


def apply_intensity(img, cfg):
    method = cfg.get("method", "none")
    if method == "none":
        return img
    if method == "contrast_stretching":
        lo, hi = np.percentile(img, [cfg["low_percentile"], cfg["high_percentile"]])
        out = (img.astype(np.float32) - lo) / max(hi - lo, 1e-6)
        return (np.clip(out, 0, 1) * 255).astype(np.uint8)
    if method == "histogram_equalization":
        return cv2.equalizeHist(img)
    if method == "clahe":
        clahe = cv2.createCLAHE(clipLimit=cfg["clip_limit"],
                                tileGridSize=(cfg["tile_grid"], cfg["tile_grid"]))
        return clahe.apply(img)
    if method == "histogram_matching":
        ref = _HIST_MATCH_REFERENCE[cfg["reference"]]
        out = exposure.match_histograms(img, ref)
        return np.clip(out, 0, 255).astype(np.uint8)
    raise ValueError(method)


# ----------------------------------------------------------------------------
# Bölüm 7: Yumuşatma ve keskinleştirme
# ----------------------------------------------------------------------------
def apply_filter(img, cfg):
    method = cfg["method"]
    if method == "none":
        return img
    if method == "gaussian":
        k = cfg["ksize"]
        return cv2.GaussianBlur(img, (k, k), cfg.get("sigma", 0))
    if method == "median":
        return cv2.medianBlur(img, cfg["ksize"])
    if method == "bilateral":
        return cv2.bilateralFilter(img, cfg["d"], cfg["sigma_color"], cfg["sigma_space"])
    if method == "laplacian_sharpen":
        # g = f - c * Laplacian(f); 3x3 Laplace çekirdeği ile konvolüsyon
        kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], np.float32)
        lap = cv2.filter2D(img.astype(np.float32), -1, kernel)
        out = img.astype(np.float32) - cfg.get("amount", 1.0) * lap
        return np.clip(out, 0, 255).astype(np.uint8)
    if method == "unsharp_mask":
        # g = f + amount * (f - Gaussian(f))
        k = cfg["ksize"]
        blur = cv2.GaussianBlur(img, (k, k), 0).astype(np.float32)
        out = img.astype(np.float32) + cfg["amount"] * (img.astype(np.float32) - blur)
        return np.clip(out, 0, 255).astype(np.uint8)
    raise ValueError(method)


# ----------------------------------------------------------------------------
# Bölüm 8: Segmentasyon
# ----------------------------------------------------------------------------
def apply_segmentation(img, cfg):
    """İkili maske (bool) ve kullanılan eşik değerini döndürür."""
    method = cfg["method"]
    if method == "fixed":
        t = cfg["threshold"]
        return img > t, t
    if method == "otsu":
        t, b = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return b > 0, t
    if method == "triangle":
        t, b = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)
        return b > 0, t
    if method == "adaptive":
        a_method = (cv2.ADAPTIVE_THRESH_GAUSSIAN_C if cfg.get("type", "gaussian") == "gaussian"
                    else cv2.ADAPTIVE_THRESH_MEAN_C)
        b = cv2.adaptiveThreshold(img, 255, a_method, cv2.THRESH_BINARY,
                                  cfg["block_size"], cfg["C"])
        return b > 0, None
    if method == "kmeans":
        k = cfg.get("k", 2)
        data = img.reshape(-1, 1).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.1)
        cv2.setRNGSeed(0)
        _, labels, centers = cv2.kmeans(data, k, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
        darkest = int(np.argmin(centers.ravel()))
        return (labels.reshape(img.shape) != darkest), None
    raise ValueError(method)


# ----------------------------------------------------------------------------
# Bölüm 9: Morfoloji ve nesne ayırma
# ----------------------------------------------------------------------------
def structuring_element(ksize, shape="ellipse"):
    shapes = {"ellipse": cv2.MORPH_ELLIPSE, "rect": cv2.MORPH_RECT, "cross": cv2.MORPH_CROSS}
    return cv2.getStructuringElement(shapes[shape], (ksize, ksize))


def apply_morphology(mask, ops):
    out = mask.astype(np.uint8)
    for op in ops:
        se = structuring_element(op["ksize"], op.get("shape", "ellipse"))
        it = op.get("iterations", 1)
        if op["op"] == "erosion":
            out = cv2.erode(out, se, iterations=it)
        elif op["op"] == "dilation":
            out = cv2.dilate(out, se, iterations=it)
        elif op["op"] == "opening":
            out = cv2.morphologyEx(out, cv2.MORPH_OPEN, se, iterations=it)
        elif op["op"] == "closing":
            out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, se, iterations=it)
        else:
            raise ValueError(op["op"])
    return out > 0


def remove_small(mask, min_area):
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    keep = np.zeros(n, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_area
    return keep[lab]


def label_objects(mask, cfg):
    """Bağlı bileşen etiketleme veya distance transform + watershed ile ayırma."""
    method = cfg.get("method", "none") if cfg else "none"
    if method == "none":
        n, lab = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
        return lab
    if method == "distance_watershed":
        dist = ndi.distance_transform_edt(mask)
        if cfg.get("smooth_sigma", 0) > 0:
            dist = ndi.gaussian_filter(dist, cfg["smooth_sigma"])
        cc = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)[1]
        peaks = feature.peak_local_max(dist, min_distance=cfg["min_distance"],
                                       threshold_abs=cfg.get("min_peak_distance", 0),
                                       labels=cc, exclude_border=False)
        markers = np.zeros(mask.shape, np.int32)
        for i, (r, c) in enumerate(peaks, start=1):
            markers[r, c] = i
        lab = sk_seg.watershed(-dist, markers, mask=mask)
        return lab
    raise ValueError(method)


# ----------------------------------------------------------------------------
# Pipeline
# ----------------------------------------------------------------------------
def run_pipeline(img, config, return_steps=False):
    steps = {"original": img}
    x = apply_intensity(img, config.get("intensity", {"method": "none"}))
    steps["intensity"] = x
    for i, fcfg in enumerate(config.get("filters", [])):
        x = apply_filter(x, fcfg)
    steps["filtered"] = x
    mask, thr = apply_segmentation(x, config["segmentation"])
    steps["segmentation"] = mask
    steps["threshold"] = thr
    mask = apply_morphology(mask, config.get("morphology", []))
    if config.get("fill_holes", False):
        mask = ndi.binary_fill_holes(mask)
    steps["morphology"] = mask
    if config.get("min_area", 0) > 0:
        mask = remove_small(mask, config["min_area"])
    steps["cleaned"] = mask
    labels = label_objects(mask, config.get("separation"))
    if config.get("min_area", 0) > 0 and config.get("separation", {}).get("method", "none") != "none":
        # watershed sonrası küçük parçaları da sayma
        ids, areas = np.unique(labels[labels > 0], return_counts=True)
        small = ids[areas < config["min_area"]]
        labels[np.isin(labels, small)] = 0
    steps["labels"] = labels
    count = int(len(np.unique(labels[labels > 0])))
    if return_steps:
        return count, steps
    return count


def count_image(data_dir, sequence, frame, config):
    img = read_gray(data_dir, sequence, frame)
    t0 = time.perf_counter()
    count = run_pipeline(img, config)
    elapsed = time.perf_counter() - t0
    return count, elapsed


def with_changes(base, **changes):
    cfg = copy.deepcopy(base)
    cfg.update(copy.deepcopy(changes))
    return cfg


BASELINE_TEMPLATE = {
    "name": "Baseline",
    "intensity": {"method": "none"},
    "filters": [],
    "segmentation": {"method": "otsu"},
    "morphology": [],
    "fill_holes": False,
    "separation": {"method": "none"},
    "min_area": 0,
}
