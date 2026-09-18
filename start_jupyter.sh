#!/usr/bin/env bash
#
# Start JupyterLab on the demo notebook, from this repo's virtualenv.
#
#     ./start_jupyter.sh              launch
#     ./start_jupyter.sh --offline    launch with Hugging Face pinned to the local cache
#     ./start_jupyter.sh --check      run the pre-flight checks and exit
#
# Presenting from this notebook? See RUNNING_THE_DEMO.md.

set -euo pipefail

cd "$(dirname "$0")"

NOTEBOOK="ldp_for_search.ipynb"
OFFLINE=0
CHECK_ONLY=0

for arg in "$@"; do
    case "$arg" in
        --offline) OFFLINE=1 ;;
        --check)   CHECK_ONLY=1 ;;
        -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown option: $arg" >&2; exit 2 ;;
    esac
done

fail() { echo "error: $*" >&2; exit 1; }

# The README's setup creates .venv, but an existing checkout may have venv.
VENV=""
for candidate in venv .venv; do
    if [ -x "$candidate/bin/jupyter" ]; then VENV="$candidate"; break; fi
done

if [ -z "$VENV" ]; then
    for candidate in venv .venv; do
        if [ -d "$candidate" ]; then
            fail "$candidate exists but has no jupyter. Run: $candidate/bin/pip install -r requirements.txt"
        fi
    done
    fail "no virtualenv found. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
fi

[ -f "$NOTEBOOK" ] || fail "$NOTEBOOK not found in $(pwd)"

echo "virtualenv: $VENV  ($("$VENV/bin/python" --version 2>&1))"

# Section 10a needs these. Missing files mean section 11 cannot run, and
# rebuilding them needs network, so say so now rather than on stage.
missing=""
for f in product.csv query.csv wands_vectors_pca20.npy wands_products.npz wands_pca.npz; do
    [ -f "data/$f" ] || missing="$missing $f"
done

if [ -n "$missing" ]; then
    echo
    echo "warning: data/ is incomplete, missing:$missing"
    echo "         Sections 10 and 11 will not run until you cache the dataset:"
    echo "             $VENV/bin/python download_wands.py"
    echo "         That step needs network."
    echo
else
    echo "dataset:    data/ complete"
fi

if [ "$OFFLINE" -eq 1 ]; then
    export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
    echo "offline:    Hugging Face pinned to the local cache"
fi

if [ "$CHECK_ONLY" -eq 1 ]; then
    [ -n "$missing" ] && exit 1
    echo "pre-flight OK"
    exit 0
fi

echo
exec "$VENV/bin/jupyter" lab "$NOTEBOOK"
