# LDP for Search

Demonstrates **Local Differential Privacy (LDP)** applied to query embeddings before they
reach a vector search engine, such as the OpenSearch k-NN plugin.

Presented at OpenSearchCon NA 2026.

Normally the user's raw query embedding goes straight to the search backend, where it can be
inverted to recover the original intent. Instead, the client injects calibrated Laplace noise
into the vector first. The engine still returns useful results, but no single query reveals
exactly what the user was looking for.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
source .venv/bin/activate
jupyter lab ldp_for_search.ipynb
```

The first execution downloads the `all-MiniLM-L6-v2` sentence-transformer model, about 90 MB,
from Hugging Face and caches it under `~/.cache/huggingface`. Subsequent runs are offline.

Section 10 onwards uses [WANDS](https://github.com/wayfair/WANDS), Wayfair's product search
relevance dataset, which is MIT licensed. Cell 10a runs `download_wands.py` from inside the
notebook, so you can do everything from JupyterLab. To pre-cache it from a terminal instead:

```bash
python download_wands.py
```

Either way, run it once before presenting. After that the whole notebook works with no network.

`download_wands.py` uses only numpy, scikit-learn and sentence-transformers, the same libraries
sections 1 through 9 already need. Parsing is done with the standard library and the cache is
written as plain `.npy` and `.npz` files. If the early sections run in your kernel, section 10
will too. Cell 10a prints the interpreter path it uses, which makes a wrong-kernel problem
obvious straight away.
