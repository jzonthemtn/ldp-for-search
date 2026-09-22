# Running the notebook during the talk

General setup lives in [README.md](README.md#setup). This file is the operational
runbook for presenting: what to do beforehand, what to run and in what order, and
what to do when something misbehaves in front of a room.

## The short version

| | |
|---|---|
| Live on stage | **nothing** — every result is a slide |
| Open as Q&A backup | sections **1**, **2**, **10a**, then **11** |
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

```bash
./start_jupyter.sh --check    # verifies the virtualenv and the cached dataset
./start_jupyter.sh            # launches JupyterLab on the notebook
```

`start_jupyter.sh` finds whichever virtualenv this checkout has, so you do not have
to remember whether it is `venv` or `.venv`, and it fails loudly if `data/` is
incomplete rather than letting you discover it mid-demo.

Then use **Kernel → Restart Kernel and Run All Cells**. It should
finish in seconds with no errors and every figure drawn. That single check exercises
the model load, the cached dataset, and every cell you will run live.

Then **Restart Kernel** again so you start the talk from a clean state.

To confirm you are genuinely offline-safe, launch with the network switched off, or:

```bash
./start_jupyter.sh --offline
```

## What to run, and when

**Nothing, during the talk.** Every notebook result now reaches the room as a slide.
The notebook is Q&A backup: the closing slide's note has you keep it open on the
convergence plot.

### If someone asks and you want to show it

Run **sections 1, 2 and 10a**, then **section 11**. About seven seconds cold.

Section 11 will not run on its own. It needs `DATA_DIR`, `wands_vectors` and the PCA
basis from section 10a, and `embedding_model` from section 1. A cold start gives you:

```
NameError: name 'DATA_DIR' is not defined
```

Priming those three before you walk on costs five seconds and means a Q&A request
never turns into a wait.

## Section-to-cell map

| Section | What it does | Needed live |
|---|---|---|
| 1 | Load the embedding model | only to run 11 |
| 2 | Toy index and the imports section 11 uses | only to run 11 |
| 3–6 | The LDP engine, query embeddings, k-NN | no |
| 7–8 | Epsilon sweep and the Laplace audit plot | no, slides 14, 15 and 18 |
| 9 | Raw vector inversion, the privacy failure | no, slide 10 |
| 10a | Fetch and cache WANDS, define the shared names | only to run 11 |
| 10b–10c | Attack at scale, item vs class recovery | no, slide 16 |
| 11 | Segments, individual vs crowd, convergence | no, slides 18 to 20 |

## If something goes wrong

**`NameError: name 'DATA_DIR' is not defined`** — the kernel is cold or 10a was
skipped. Run sections 1, 2 and 10a, then re-run the failed cell.

**`NameError` on `sweep`, `wands_sweep` or similar in a plotting cell** — plotting
cells are separate from the cells that compute their data. Run the cell immediately
above the one that failed.

**Section 10a fails or tries to download** — `data/` is missing or incomplete. It
needs network to rebuild. Check that `data/` holds `product.csv`, `query.csv`,
`wands_vectors_pca20.npy`, `wands_products.npz` and `wands_pca.npz`.

**The model tries to reach Hugging Face** — relaunch with `./start_jupyter.sh
--offline`, which pins it to the local cache so it fails fast rather than hanging on
a bad venue network.

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
