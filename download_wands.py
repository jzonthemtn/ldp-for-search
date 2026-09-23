"""
Download the WANDS product search dataset and pre-compute its embeddings.

Run this ONCE before presenting:

    python download_wands.py

Everything is cached under data/, so the notebook needs no network at run time.

This script deliberately depends only on numpy, scikit-learn and sentence-transformers,
the same libraries the rest of the notebook already uses. Parsing is done with the
standard library so that section 10 adds no new dependencies.

WANDS is Wayfair's product search relevance dataset (ECIR 2022), MIT licensed:
https://github.com/wayfair/WANDS
"""

import csv
import sys
import urllib.request
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize

BASE_URL = "https://raw.githubusercontent.com/wayfair/WANDS/main/dataset"
DATA_DIR = Path(__file__).parent / "data"

MODEL_NAME = "all-MiniLM-L6-v2"
N_COMPONENTS = 20  # must match the toy sections of the notebook

# WANDS product descriptions are long enough to trip the default csv field limit
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def download():
    DATA_DIR.mkdir(exist_ok=True)
    for name in ("product.csv", "query.csv", "label.csv"):
        dest = DATA_DIR / name
        if dest.exists():
            print(f"{name}: already cached")
            continue
        print(f"{name}: downloading...")
        urllib.request.urlretrieve(f"{BASE_URL}/{name}", dest)
        print(f"{name}: saved to {dest} ({dest.stat().st_size / 1e6:.0f} MB)")


def read_products():
    """Read the product table. WANDS ships tab-separated despite the .csv extension."""
    ids, names, classes = [], [], []
    with open(DATA_DIR / "product.csv", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            name = (row.get("product_name") or "").strip()
            if not name:
                continue  # a handful of rows have no name
            ids.append(row.get("product_id") or "")
            names.append(name)
            classes.append((row.get("product_class") or "Unknown").strip() or "Unknown")
    return np.array(ids), np.array(names), np.array(classes)


def build_embeddings():
    products_out = DATA_DIR / "wands_products.npz"
    vectors_out = DATA_DIR / "wands_vectors_pca20.npy"

    if products_out.exists() and vectors_out.exists():
        print("embeddings: already cached")
        return

    # Imported here so the download step still runs if the model is slow to load
    from sentence_transformers import SentenceTransformer

    ids, names, classes = read_products()
    print(f"products: {len(names):,} rows, {len(set(classes.tolist())):,} classes")

    print(f"embedding with {MODEL_NAME} (takes ~10-30s on CPU)...")
    model = SentenceTransformer(MODEL_NAME)
    full = normalize(model.encode(names.tolist(), batch_size=256, show_progress_bar=True))

    print(f"fitting PCA to {N_COMPONENTS} dims...")
    pca = PCA(n_components=N_COMPONENTS, random_state=0)
    reduced = pca.fit_transform(full).astype(np.float32)
    print(f"PCA: {full.shape[1]} -> {reduced.shape[1]} dims, "
          f"{pca.explained_variance_ratio_.sum():.1%} of variance retained")

    # Persist the PCA basis so the notebook can project a fresh query without refitting
    np.savez(
        DATA_DIR / "wands_pca.npz",
        components=pca.components_.astype(np.float32),
        mean=pca.mean_.astype(np.float32),
    )
    np.save(vectors_out, reduced)
    np.savez_compressed(products_out, ids=ids, names=names, classes=classes)
    print(f"saved: {vectors_out.name}, {products_out.name}, wands_pca.npz")


if __name__ == "__main__":
    download()
    build_embeddings()
    print("\nDone. The notebook can now run fully offline.")
