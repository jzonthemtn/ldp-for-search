# Running the notebook during the talk

General setup lives in [README.md](README.md#setup). This file is the operational
runbook for presenting: what to do beforehand, what to run and in what order, and
what to do when something misbehaves in front of a room.

## The short version

| | |
|---|---|
| Run order | sections **1–6**, then **9**, then **10a**, then **11** |
| Total run time | about **7 seconds** |
| Network needed | **no**, once the one-time prep below is done |

## One-time prep, before you travel

```bash
source venv/bin/activate
pip install -r requirements.txt
python download_wands.py
```

> The virtualenv in this working copy is `venv/`, while the README's setup steps
> create `.venv/`. Both are gitignored. Use whichever one you actually have, and
> make sure JupyterLab is launched from it.

`download_wands.py` fetches the WANDS dataset and embeds 43,000 products. It takes a
few minutes the first time and prints `already cached` on every run after that. It
writes to `data/`, which is gitignored — so it does **not** travel with the repo. If
you present from a different machine or a fresh clone, you have to run it again, and
it needs network when you do.

The first notebook run also pulls `all-MiniLM-L6-v2` (~90 MB) into
`~/.cache/huggingface`. Running `download_wands.py` does this for you.

## Pre-flight, the morning of

Open the notebook and use **Kernel → Restart Kernel and Run All Cells**. It should
finish in seconds with no errors and every figure drawn. That single check exercises
the model load, the cached dataset, and every cell you will run live.

Then **Restart Kernel** again so you start the talk from a clean state.

To confirm you are genuinely offline-safe, launch with the network switched off, or:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 jupyter lab ldp_for_search.ipynb
```

## What to run, and when

Two slides send you to the notebook.

### Slide 10 — "Demo: invert a raw query vector"

Run **sections 1 through 6**, then **section 9**.

Section 1 loads the model and takes about two seconds; everything after it is
instant. Section 9 is the hinge — the attacker inverting the raw vector.

**Also run section 10a before you leave the notebook.** It only loads the cached
WANDS data and prints `already cached`, but having it in the kernel is what makes the
Part 5 demo instant instead of a pause on stage.

### Slide 21 — "Demo: segments of real users"

Run **section 10a** (if you skipped it earlier, or the kernel has restarted), then
**section 11**.

Section 11 will **not** run on its own. It needs `DATA_DIR`, `wands_vectors` and the
PCA basis, all of which section 10a defines. Skipping it gives you:

```
NameError: name 'DATA_DIR' is not defined
```

You do not need sections 10b or 10c live — those produce the charts that are already
on slides 15 and 18 as images.

## Section-to-cell map

| Section | What it does | Needed live |
|---|---|---|
| 1 | Load the embedding model | yes |
| 2–6 | Toy index, the LDP engine, query embeddings, k-NN | yes |
| 7–8 | Epsilon sweep and the Laplace audit plot | no, slides 14 and 18 |
| 9 | Raw vector inversion, the privacy failure | yes |
| 10a | Fetch and cache WANDS, define the shared names | **yes** |
| 10b–10c | Attack at scale, item vs class recovery | no, slide 15 |
| 11 | Segments, individual vs crowd, convergence | yes |

## If something goes wrong

**`NameError: name 'DATA_DIR' is not defined`** — you skipped section 10a. Run it and
re-run the failed cell.

**`NameError` on `sweep`, `wands_sweep` or similar in a plotting cell** — plotting
cells are separate from the cells that compute their data. Run the cell immediately
above the one that failed.

**Section 10a fails or tries to download** — `data/` is missing or incomplete. It
needs network to rebuild. Check that `data/` holds `product.csv`, `query.csv`,
`wands_vectors_pca20.npy`, `wands_products.npz` and `wands_pca.npz`.

**The model tries to reach Hugging Face** — set `HF_HUB_OFFLINE=1` and
`TRANSFORMERS_OFFLINE=1` before launching, so it uses the local cache and fails fast
rather than hanging on a bad venue network.

**Wrong interpreter** — section 10a prints the interpreter path it is using. It must
point inside your virtualenv. If it does not, switch kernels with **Kernel → Change
Kernel** and pick the one this project registered.

**Total fallback** — every figure in the notebook is also a PNG in `plots/` and is
already on a slide. If the kernel will not cooperate, keep talking over the slides;
nothing in the deck depends on the notebook running.

## One thing to know about scrolling

Five code cells have no stored output, including every plotting cell. If you scroll
the notebook without running it, those figures are blank. Run the cells, or use the
slides.
