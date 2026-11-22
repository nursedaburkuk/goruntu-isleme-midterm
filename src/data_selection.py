"""Seed ile tekrarlanabilir geliştirme / doğrulama / test görüntü seçimi (Ödev Bölüm 3)."""
import os
import glob
import numpy as np
import pandas as pd

STUDENT_NUMBER = "244329048"
SEED = int(STUDENT_NUMBER[-5:]) + 2026  # 29048 + 2026 = 31074

N_VALIDATION = 5
N_DEVELOPMENT = 10
N_TEST_BLOCKS = 3
TEST_BLOCK_LENGTH = 5
# "En az 5 karelik boşluk": iki kare arasında en az 5 kare bulunmalıdır,
# yani kare numaraları arasındaki fark en az 6 olmalıdır.
MIN_GAP_FRAMES = 5
MAX_ATTEMPTS = 10000


def list_frames(data_dir, sequence):
    files = sorted(glob.glob(os.path.join(data_dir, sequence, "t*.tif")))
    return [int(os.path.basename(f)[1:4]) for f in files]


def _dev_val_ok(val, dev):
    if len(set(val) | set(dev)) != len(val) + len(dev):
        return False
    for v in val:
        for d in dev:
            if abs(v - d) - 1 < MIN_GAP_FRAMES:
                return False
    return True


def _test_blocks_ok(starts):
    s = sorted(starts)
    for a, b in zip(s[:-1], s[1:]):
        end_a = a + TEST_BLOCK_LENGTH - 1
        if b - end_a - 1 < MIN_GAP_FRAMES:
            return False
    return True


def select_frames(data_dir, seed=SEED):
    """Deterministik seçim. Koşullar sağlanamazsa aynı RNG ile yeniden çekilir
    (deterministik tekrar prosedürü); deneme sayısı kaydedilir."""
    rng = np.random.default_rng(seed)
    frames01 = list_frames(data_dir, "01")
    frames02 = list_frames(data_dir, "02")

    # Kural 1-3: önce 5 doğrulama, sonra 10 geliştirme karesi (Sequence 01)
    dev_val_attempts = 0
    while True:
        dev_val_attempts += 1
        if dev_val_attempts > MAX_ATTEMPTS:
            raise RuntimeError("Geliştirme/doğrulama seçimi koşulları sağlanamadı")
        val = sorted(rng.choice(frames01, size=N_VALIDATION, replace=False).tolist())
        remaining = [f for f in frames01 if f not in val]
        dev = sorted(rng.choice(remaining, size=N_DEVELOPMENT, replace=False).tolist())
        if _dev_val_ok(val, dev):
            break

    # Kural 4-5: Sequence 02'den 3 başlangıç noktası, her biri 5 ardışık kare
    possible_starts = [f for f in frames02 if f + TEST_BLOCK_LENGTH - 1 <= max(frames02)]
    test_attempts = 0
    while True:
        test_attempts += 1
        if test_attempts > MAX_ATTEMPTS:
            raise RuntimeError("Test bloğu seçimi koşulları sağlanamadı")
        starts = rng.choice(possible_starts, size=N_TEST_BLOCKS, replace=False).tolist()
        if _test_blocks_ok(starts):
            break

    rows = []
    for f in dev:
        rows.append(dict(group="development", sequence="01", frame=f, block="",
                         filename=f"01/t{f:03d}.tif"))
    for f in val:
        rows.append(dict(group="validation", sequence="01", frame=f, block="",
                         filename=f"01/t{f:03d}.tif"))
    for b, s in enumerate(sorted(starts), start=1):
        for f in range(s, s + TEST_BLOCK_LENGTH):
            rows.append(dict(group="test", sequence="02", frame=f, block=f"B{b}",
                             filename=f"02/t{f:03d}.tif"))
    df = pd.DataFrame(rows)
    df["seed"] = seed
    df["dev_val_attempts"] = dev_val_attempts
    df["test_attempts"] = test_attempts
    return df


if __name__ == "__main__":
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/Fluo-N2DH-GOWT1"
    out = select_frames(data_dir)
    out.to_csv("selected_frames.csv", index=False)
    print(out.to_string())
