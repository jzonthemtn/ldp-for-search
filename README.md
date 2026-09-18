# LDP for Search

A local Jupyter port of a Colab notebook demonstrating **Local Differential Privacy (LDP)**
applied to query embeddings before they reach a vector search engine, such as the OpenSearch
k-NN plugin.

Original notebook: [Colab](https://colab.research.google.com/drive/1IYkm_sjU5Et6_fdT3y8LgbQX4Uv2kdwQ#scrollTo=Pen5HBN7WXoP)

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

Section 10 uses the WANDS dataset. Cell 10a runs `download_wands.py` from inside the notebook,
so you can do everything from JupyterLab. To pre-cache it from a terminal instead:

```bash
python download_wands.py
```

Either way, run it once before presenting. After that the whole notebook works with no network.

`download_wands.py` uses only numpy, scikit-learn and sentence-transformers, the same libraries
sections 1 through 9 already need. Parsing is done with the standard library and the cache is
written as plain `.npy` and `.npz` files. If the early sections run in your kernel, section 10
will too. Cell 10a prints the interpreter path it uses, which makes a wrong-kernel problem
obvious straight away.

## What the notebook covers

Sections 1 through 9 use a 20-document toy index that is small enough to read aloud. Section 10
swaps in a real 43,000-product index.

1. Load the `all-MiniLM-L6-v2` embedding model.
2. Build a simulated search index of 20 product names. Embed, L2-normalize, reduce to 20
   dimensions with PCA.
3. The LDP engine: `inject_laplace_noise(vector, epsilon)`, the logic that would live
   client-side.
4. Embed a user query, `"laptop computer"`.
5. Project the query through the fitted PCA model and add Laplace noise at `epsilon = 1.2`.
6. k-NN search with the noised vector, simulating OpenSearch.
7. An epsilon sweep measuring where the true intent, `"Laptop"`, actually ranks. Reported as
   P@1 and R@5 over 200 noisy draws per epsilon, plus a tradeoff plot.
8. A "statistical tent" audit. 1,000 noisy draws histogrammed to verify the Laplace
   distribution is centered on the true value.
9. Privacy failure vs. success. A simulated vector-inversion attack against the raw query
   versus the noised query.
10. The same mechanism against 42,994 real Wayfair products, scoring the attacker on
    item-level and class-level recovery separately.
11. What survives the noise. Cohorts of users built from the 480 real WANDS queries, each user
    privatizing independently, showing that individual queries stay hidden while cohort-level
    trends are recovered exactly.

## Where the tradeoff sits on the toy index

The sweep in section 7 uses a 20-document index, so random guessing gives P@1 0.05 and
R@5 0.25.

| epsilon | mean rank | P@1  | R@5  |
|--------:|----------:|-----:|-----:|
|     0.5 |      9.15 | 0.04 | 0.27 |
|     1.2 |      7.05 | 0.07 | 0.45 |
|       3 |      3.94 | 0.38 | 0.75 |
|       5 |      1.84 | 0.72 | 0.95 |
|      10 |      1.03 | 0.98 | 1.00 |
|      20 |      1.00 | 1.00 | 1.00 |

At the notebook's default `epsilon = 1.2`, results are close to random. Privacy is strong, but
the user does not find what they were looking for. The region the framing describes, high R@5
with collapsed P@1, sits around `epsilon = 3` to `5`. Past `epsilon = 10` the noise stops doing
anything and the raw intent is fully recoverable.

## What the 43k index adds

[WANDS](https://github.com/wayfair/WANDS) is Wayfair's product search relevance dataset from
ECIR 2022, MIT licensed. It has 42,994 products, 480 real queries, and 861 product classes.

The class labels are the reason it is worth the extra step. They separate two questions the
20-item index cannot tell apart: did the attacker recover the *exact product*, or only the
*category*? Scored on the query `"solid wood platform bed"` over 300 noisy draws:

| epsilon | scale | item P@1 | item R@5 | class P@1 | class R@5 |
|--------:|------:|---------:|---------:|----------:|----------:|
|       1 | 1.000 |     0.00 |     0.01 |      0.06 |      0.11 |
|       5 | 0.200 |     0.04 |     0.09 |      0.33 |      0.60 |
|      10 | 0.100 |     0.13 |     0.31 |      0.63 |      0.92 |
|      20 | 0.050 |     0.42 |     0.76 |      0.82 |      1.00 |
|      30 | 0.033 |     0.70 |     0.96 |      0.93 |      1.00 |
|      50 | 0.020 |     0.93 |     1.00 |      0.98 |      1.00 |
|     100 | 0.010 |     1.00 |     1.00 |      1.00 |      1.00 |

Random guessing over 42,994 products gives item P@1 0.00002 and class P@1 0.026, since "Beds"
has 1,112 members.

Around `epsilon = 10` to `20` the two curves separate. The attacker recovers the category most
of the time while the exact product stays largely hidden. That gap is the honest version of the
privacy claim. It also names the residual leak: LDP at a usable epsilon does not hide the broad
category of what someone is shopping for.

Note that the useful epsilon range here, 10 to 50, looks nothing like the toy index's 1.2. The
Laplace scale is `sensitivity / epsilon`, and what matters is its size relative to the spread of
the vector coordinates, which differs between the two PCA fits. Epsilon is not portable across
indexes.

## What survives the noise

Section 11 is the counterweight to sections 7 and 10. Those measure what LDP costs. This one
measures what it keeps, which is the reason to use it at all.

The noise is zero-mean, so it cancels when averaged across independent users. At `epsilon = 1.0`,
heavier noise than anything in section 10, all five cohorts are identified correctly from the
noised data, while individual recovery stays at roughly chance. The estimation error falls as
`1 / sqrt(n)`:

| users | centroid error |
|------:|---------------:|
|    10 |          2.098 |
|   100 |          0.638 |
| 1,000 |          0.194 |
| 10,000 |         0.066 |
| 100,000 |        0.020 |

The spread of the index itself is 0.128, which the error crosses at roughly 2,300 users. That is
the practical threshold. Segments with thousands of users are measurable under LDP. Segments with
dozens are not.

That 2,300 is not a constant. It is the crossing at `epsilon = 1.0` on this index, and it moves
with the privacy budget: error goes as `(1 / epsilon) / sqrt(n)`, so the threshold scales as
`1 / epsilon^2`. At `epsilon = 0.5` it is around 9,200 users, at `epsilon = 2` around 575. Like
epsilon itself, it does not transfer between indexes, because the yardstick is the coordinate
spread of the index you are on.

## Knobs

- `epsilon` in section 5 is the privacy control. Lower means more noise, more privacy, and less
  search accuracy.
- `n_components` in the `PCA(...)` call. Fewer dimensions spreads the noise budget over fewer
  coordinates.
- `text_queries` in section 4. Swap in other queries. A commented-out list of alternatives is
  included.
- `WANDS_QUERY` in section 10b. Any of the 480 real queries in `data/query.csv` works.

`np.random.seed(42)` is set so the noisy results are reproducible. Remove it to see the
run-to-run variation that the noise actually produces.

## Files

- `ldp_for_search.ipynb` is the notebook.
- `download_wands.py` fetches and caches the WANDS dataset and its embeddings.
- `data/` holds the cached dataset and vectors. It is gitignored.
