"""
Build the hand-drawn (well, matplotlib-drawn) diagrams the deck uses.

    python build_diagrams.py

Writes into plots/, alongside the measured figures the notebook produces. These are
schematics, not results: nothing here is plotted from data.

Only matplotlib is needed.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).parent
PLOTS = HERE / "plots"

# Same palette as build_slides.py, so a diagram sits on a slide without clashing.
INK = "#141B2D"
MUTED = "#5A647A"
ACCENT = "#005EB8"
WARN = "#B4311A"   # the deck's "this is the catch" red
GOOD = "#1B7A3F"   # its counterpart, for the row that gets the ordering right
EDGE = "#C8D0DE"
PAPER = "#FFFFFF"
WASH = "#F3F6FB"   # the faint fill behind inert UI chrome
TINT = "#E3EEFA"   # the accent at 10%, for the one row that was clicked


def _node(ax, cx, cy, w, h, title, index=None, fields=None, filled=False):
    """A box in a flow diagram. Boxes that map to a UBI index also carry its schema."""
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.04,rounding_size=0.18",
        linewidth=1.6,
        edgecolor=ACCENT if filled else EDGE,
        facecolor=ACCENT if filled else PAPER,
    )
    ax.add_patch(box)

    body = PAPER if filled else INK
    faint = "#CFE2F6" if filled else MUTED

    if index is None:
        ax.text(cx, cy, title, ha="center", va="center",
                fontsize=13, color=body,
                fontweight="bold" if filled else "normal", linespacing=1.45)
        return

    ax.text(cx, cy + 0.80, title, ha="center", va="center",
            fontsize=13, color=body,
            fontweight="bold" if filled else "normal", linespacing=1.4)
    ax.text(cx, cy + 0.16, index, ha="center", va="center",
            fontsize=10.5, color=PAPER if filled else ACCENT,
            family="monospace", fontweight="bold")
    ax.text(cx, cy - 0.58, fields, ha="center", va="center",
            fontsize=9, color=faint, family="monospace", linespacing=1.6)


def _arrow(ax, start, end, rad, color=MUTED):
    ax.add_patch(FancyArrowPatch(
        start, end,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>", mutation_scale=15,
        linewidth=1.5, color=color,
    ))


def relevance_loop(path):
    """The tuning loop for slide 4: observation is the step that closes it."""
    fig, ax = plt.subplots(figsize=(5.4, 4.35), dpi=220)
    # The axes fill the figure, so one data unit is a predictable fraction of an
    # inch and the schema lines can be sized against the box width they sit in.
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    # Limits hug the content, so the slide is not paying for empty margin
    ax.set_xlim(0.05, 9.95)
    ax.set_ylim(0.85, 9.25)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    w, h = 3.9, 2.6
    left, right = 2.15, 7.85
    top, bottom = 7.7, 2.4

    _node(ax, left, top, w, h, "A user searches",
          index="ubi_queries",
          fields="user_query, query_id,\nclient_id, timestamp")
    _node(ax, right, top, w, h, "Results come\nback ranked")
    _node(ax, right, bottom, w, h, "What they click,\nskip, and where",
          index="ubi_events",
          fields="action_name, object_id,\nposition, session_id,\npage_id",
          filled=True)
    _node(ax, left, bottom, w, h, "You tune\nthe ranking")

    pad = 0.25
    _arrow(ax, (left + w / 2 + pad, top), (right - w / 2 - pad, top), 0)
    _arrow(ax, (right, top - h / 2 - pad), (right, bottom + h / 2 + pad), 0, ACCENT)
    _arrow(ax, (right - w / 2 - pad, bottom), (left + w / 2 + pad, bottom), 0, ACCENT)
    _arrow(ax, (left, bottom + h / 2 + pad), (left, top - h / 2 - pad), 0)

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")


def _box(ax, x, y, w, h, **kw):
    kw.setdefault("boxstyle", "round,pad=0.02,rounding_size=0.12")
    kw.setdefault("linewidth", 1.4)
    ax.add_patch(FancyBboxPatch((x, y), w, h, **kw))


def ubi_pipeline(path):
    """Slide 5: where the two indices come from. Browser on the left, cluster on the right."""
    fig, ax = plt.subplots(figsize=(5.5, 4.35), dpi=220)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(0.05, 9.95)
    ax.set_ylim(0.9, 7.3)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    # ---- the browser, where ubi.js runs -------------------------------------
    _box(ax, 0.25, 1.3, 4.3, 5.6, edgecolor=EDGE, facecolor=PAPER)
    ax.plot([0.25, 4.55], [6.25, 6.25], color=EDGE, linewidth=1.2)
    for i in range(3):
        ax.add_patch(Circle((0.62 + 0.30 * i, 6.57), 0.075, color=EDGE))
    ax.text(4.40, 6.57, "a search page", ha="right", va="center",
            fontsize=8.5, color=MUTED)

    _box(ax, 0.62, 5.35, 3.56, 0.62, edgecolor=EDGE, facecolor=WASH)
    ax.text(0.85, 5.66, "winter boots", ha="left", va="center",
            fontsize=9.5, color=MUTED, family="monospace")

    for i, y in enumerate((4.35, 3.42, 2.49), start=1):
        hit = i == 2
        _box(ax, 0.98, y, 3.20, 0.70,
             edgecolor=ACCENT if hit else EDGE,
             facecolor=TINT if hit else WASH,
             linewidth=1.6 if hit else 1.2)
        ax.text(0.72, y + 0.35, str(i), ha="center", va="center",
                fontsize=9.5, color=ACCENT if hit else MUTED,
                family="monospace", fontweight="bold" if hit else "normal")
    ax.text(2.58, 3.77, "clicked", ha="center", va="center",
            fontsize=9, color=ACCENT, fontweight="bold")

    _box(ax, 0.62, 1.60, 1.45, 0.55, edgecolor=ACCENT, facecolor=PAPER)
    ax.text(1.345, 1.875, "ubi.js", ha="center", va="center",
            fontsize=10, color=ACCENT, family="monospace", fontweight="bold")

    # ---- the hop to the cluster ---------------------------------------------
    _arrow(ax, (4.75, 4.1), (5.75, 4.1), 0, ACCENT)
    ax.text(5.25, 4.52, "events", ha="center", va="center",
            fontsize=9, color=MUTED, family="monospace")

    # ---- the cluster, and the two indices it lands in ------------------------
    _box(ax, 5.95, 1.3, 3.85, 5.6, edgecolor=MUTED, facecolor="#FBFCFE",
         linestyle="--", linewidth=1.2)
    ax.text(7.875, 6.45, "OpenSearch", ha="center", va="center",
            fontsize=10.5, color=MUTED, fontweight="bold")

    for y, name, gloss, filled in (
        (4.12, "ubi_queries", "what was searched", False),
        (1.95, "ubi_events", "what was done with it", True),
    ):
        _box(ax, 6.30, y, 3.15, 1.45,
             edgecolor=ACCENT, facecolor=ACCENT if filled else PAPER, linewidth=1.6)
        ax.text(7.875, y + 0.92, name, ha="center", va="center",
                fontsize=11, color=PAPER if filled else ACCENT,
                family="monospace", fontweight="bold")
        ax.text(7.875, y + 0.42, gloss, ha="center", va="center",
                fontsize=9, color="#CFE2F6" if filled else MUTED)

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")


def ordering(path):
    """
    Slide 7: the same four moments, in two different orders.

    The argument is about when protection happens, not whether redaction works,
    so both rows show it working. Only the position of the device boundary moves.
    """
    fig, ax = plt.subplots(figsize=(5.5, 4.4), dpi=220)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(0.1, 9.9)
    ax.set_ylim(1.25, 7.65)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    boundary = 4.35

    def row(y, label, colour, band_from, band_to, band_text, marks, text_x=None):
        ax.text(0.35, y + 1.18, label, ha="left", va="center",
                fontsize=11.5, color=colour, fontweight="bold")
        ax.add_patch(FancyBboxPatch(
            (band_from, y - 0.32), band_to - band_from, 0.64,
            boxstyle="round,pad=0.01,rounding_size=0.1",
            linewidth=0, facecolor=colour, alpha=0.14))
        ax.text(text_x if text_x else (band_from + band_to) / 2, y + 0.72, band_text,
                ha="center", va="center", fontsize=11, color=colour)
        ax.plot([0.35, 9.65], [y, y], color=EDGE, linewidth=1.4, zorder=1)
        for x, text in marks:
            ax.add_patch(Circle((x, y), 0.10, color=MUTED, zorder=3))
            ax.text(x, y - 0.60, text, ha="center", va="center",
                    fontsize=10.5, color=MUTED, linespacing=1.35)

    row(5.50, "Redact after the fact", WARN,
        boundary, 8.95, "readable, off the device",
        [(1.15, "typed"), (6.75, "stored"), (8.95, "redacted")])

    row(2.60, "Protect before it leaves", GOOD,
        2.55, 9.65, "unreadable from here on",
        [(1.15, "typed"), (2.55, "made\nunreadable"), (6.75, "stored")],
        text_x=7.0)

    ax.plot([boundary, boundary], [1.95, 6.85], color=MUTED,
            linewidth=1.3, linestyle=(0, (4, 3)), zorder=2)
    ax.text(boundary, 7.25, "leaves the device", ha="center", va="center",
            fontsize=11, color=MUTED, fontweight="bold")

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")


def vector_inversion(path):
    """
    Slide 9: not just that the text can be recovered, but by what method.

    The attack is a nearest-neighbour search: embed a pile of candidate strings,
    compare each to the stolen vector, keep the closest. The scores are schematic,
    the method is not.
    """
    fig, ax = plt.subplots(figsize=(5.5, 4.4), dpi=220)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(0.2, 9.8)
    ax.set_ylim(0.5, 8.35)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    query = '"laptop computer"'

    # ---- what actually gets stored -----------------------------------------
    _box(ax, 0.4, 6.95, 4.0, 1.0, edgecolor=EDGE, facecolor=WASH)
    ax.text(2.4, 7.45, query, ha="center", va="center",
            fontsize=11, color=INK, family="monospace")
    ax.text(2.4, 6.55, "typed", ha="center", va="center", fontsize=9.5, color=MUTED)

    _arrow(ax, (4.55, 7.45), (5.35, 7.45), 0, MUTED)
    ax.text(4.95, 7.95, "embed", ha="center", va="center", fontsize=9.5, color=MUTED)

    _box(ax, 5.5, 6.95, 4.0, 1.0, edgecolor=ACCENT, facecolor=PAPER)
    ax.text(7.5, 7.45, "[ 0.031  -0.114  ... ]", ha="center", va="center",
            fontsize=10, color=INK, family="monospace")
    ax.text(7.5, 6.55, "stored", ha="center", va="center", fontsize=9.5, color=ACCENT)

    _arrow(ax, (7.5, 6.25), (7.5, 5.68), 0, WARN)
    ax.text(7.25, 5.95, "the attacker gets this", ha="right", va="center",
            fontsize=9.5, color=WARN)

    # ---- the attack ---------------------------------------------------------
    _box(ax, 0.4, 0.75, 9.1, 4.75, edgecolor=EDGE, facecolor="#FCFDFE")
    ax.text(4.95, 4.95, "embed guesses, compare, keep the closest",
            ha="center", va="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.text(1.0, 4.30, "guess", ha="left", va="center", fontsize=9, color=MUTED)
    ax.text(8.9, 4.30, "similarity", ha="right", va="center", fontsize=9, color=MUTED)

    guesses = [('"winter boots"', "0.11", False),
               ('"dog food"', "0.07", False),
               (query, "0.94", True)]
    for y, (text, score, hit) in zip((3.60, 2.85, 2.10), guesses):
        if hit:
            ax.add_patch(FancyBboxPatch(
                (0.75, y - 0.32), 8.4, 0.64,
                boxstyle="round,pad=0.01,rounding_size=0.1",
                linewidth=0, facecolor=WARN, alpha=0.14))
        colour = WARN if hit else MUTED
        ax.text(1.0, y, text, ha="left", va="center", fontsize=11,
                color=colour, family="monospace",
                fontweight="bold" if hit else "normal")
        ax.text(8.9, y, score, ha="right", va="center", fontsize=11,
                color=colour, family="monospace",
                fontweight="bold" if hit else "normal")

    ax.text(4.95, 1.25, "the closest guess is the query itself",
            ha="center", va="center", fontsize=10, color=WARN, style="italic")

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")


def epsilon_dial(path):
    """
    Slide 13: epsilon as a dial, and nothing else.

    Deliberately not a picture of the noise itself: slide 14 shows the real
    Laplace tent from 1,000 draws, and a cartoon of it here would spend that.
    This draws only the trade-off the rest of the talk keeps referring back to.
    """
    fig, ax = plt.subplots(figsize=(5.5, 2.9), dpi=220)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(0.3, 9.9)
    ax.set_ylim(0.35, 5.4)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    _arrow(ax, (5.0, 4.35), (1.25, 4.35), 0, ACCENT)
    ax.text(3.1, 4.95, "more privacy", ha="center", va="center",
            fontsize=12, color=ACCENT, fontweight="bold")

    _box(ax, 1.0, 2.65, 8.0, 0.42, edgecolor=EDGE, facecolor=WASH)
    for i, label in enumerate(("0.5", "1", "2", "4", "8")):
        x = 1.0 + 2.0 * i
        ax.plot([x, x], [2.50, 3.22], color=EDGE, linewidth=1.2, zorder=0)
        ax.text(x, 2.02, label, ha="center", va="center",
                fontsize=10.5, color=MUTED, family="monospace")
    ax.text(9.45, 2.86, "\u03b5", ha="left", va="center",
            fontsize=14, color=INK, fontstyle="italic")

    _arrow(ax, (5.0, 1.30), (8.75, 1.30), 0, MUTED)
    ax.text(6.9, 0.72, "more accuracy", ha="center", va="center",
            fontsize=12, color=MUTED, fontweight="bold")

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")


def trust_boundary(path):
    """
    Slide 28: the architecture, drawn around the line that matters.

    Three boxes on the device, one in the cluster, and a dashed line between them.
    The cluster panel is deliberately the smaller of the two: it holds strictly
    less than the device does, which is the whole architectural claim.
    """
    fig, ax = plt.subplots(figsize=(5.5, 3.7), dpi=220)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(0.2, 9.8)
    ax.set_ylim(0.9, 7.3)
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    boundary = 5.35

    # ---- the device ---------------------------------------------------------
    _box(ax, 0.35, 1.9, 4.5, 4.6, edgecolor=ACCENT, facecolor=PAPER)
    ax.text(2.6, 6.15, "the device", ha="center", va="center",
            fontsize=11, color=ACCENT, fontweight="bold")

    for cy, text, filled in ((5.30, "raw query vector", False),
                             (4.00, "ubi.js adds noise", False),
                             (2.70, "noised vector", True)):
        _box(ax, 0.75, cy - 0.42, 3.7, 0.84,
             edgecolor=ACCENT if filled else EDGE,
             facecolor=ACCENT if filled else WASH)
        ax.text(2.6, cy, text, ha="center", va="center", fontsize=11,
                color=PAPER if filled else INK,
                fontweight="bold" if filled else "normal")

    _arrow(ax, (2.6, 4.82), (2.6, 4.47), 0, MUTED)
    _arrow(ax, (2.6, 3.52), (2.6, 3.17), 0, MUTED)

    # ---- the line, and what crosses it --------------------------------------
    ax.plot([boundary, boundary], [1.55, 6.75], color=MUTED,
            linewidth=1.3, linestyle=(0, (4, 3)))
    ax.text(boundary, 7.05, "leaves the device", ha="center", va="center",
            fontsize=10.5, color=MUTED, fontweight="bold")
    _arrow(ax, (4.9, 2.70), (5.85, 2.70), 0, ACCENT)

    # ---- the cluster, holding strictly less ---------------------------------
    _box(ax, 5.9, 1.9, 3.8, 2.4, edgecolor=MUTED, facecolor="#FBFCFE",
         linestyle="--", linewidth=1.2)
    ax.text(7.8, 3.90, "OpenSearch", ha="center", va="center",
            fontsize=11, color=MUTED, fontweight="bold")
    _box(ax, 6.2, 2.28, 3.2, 0.84, edgecolor=ACCENT, facecolor=PAPER)
    ax.text(7.8, 2.70, "noised vectors only", ha="center", va="center",
            fontsize=11, color=INK)

    ax.text(4.95, 1.25, "the raw query never crosses this line",
            ha="center", va="center", fontsize=10.5, color=ACCENT, style="italic")

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")


def cancellation(path):
    """
    Slide 21: why zero-mean noise is survivable in aggregate.

    The dots are real Laplace draws, not hand-placed, and the marked average is
    the actual mean of the dots plotted. Axes are left off because the point is
    the geometry, not any particular coordinate system.
    """
    rng = np.random.default_rng(7)
    n = 300
    draws = rng.laplace(0.0, 1.0, size=(n, 2))
    mean = draws.mean(axis=0)

    fig, ax = plt.subplots(figsize=(5.2, 4.3), dpi=220)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim(-6.4, 6.4)
    ax.set_ylim(-5.6, 6.2)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(PAPER)

    ax.scatter(draws[:, 0], draws[:, 1], s=16, color=MUTED, alpha=0.40,
               linewidths=0, zorder=1)

    # The truth, and the average of every dot, drawn as a ring around a dot
    # because at this sample size they land almost on top of each other.
    ax.scatter([0], [0], s=320, facecolors="none", edgecolors=INK,
               linewidths=1.8, zorder=3)
    ax.scatter(mean[:1], mean[1:], s=70, color=ACCENT, zorder=4)

    # Point at a far dot that is still inside the view, so the leader is visible
    norms = np.linalg.norm(draws, axis=1)
    far = draws[np.argmax(np.where(norms < 4.6, norms, 0))]
    ax.annotate("one user's noised query,\nuseless on its own",
                xy=(far[0], far[1]), xytext=(-6.2, 5.4),
                fontsize=10.5, color=MUTED, ha="left", va="center",
                linespacing=1.4,
                arrowprops=dict(arrowstyle="-", color=EDGE, linewidth=1.2))

    ax.annotate(f"the truth, and the average\nof all {n} dots",
                xy=(0.35, -0.35), xytext=(2.5, -4.6),
                fontsize=10.5, color=ACCENT, ha="center", va="center",
                linespacing=1.4,
                arrowprops=dict(arrowstyle="-", color=ACCENT, linewidth=1.2))

    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor=PAPER)
    plt.close(fig)
    print(f"wrote {path.relative_to(HERE)}")
    return float(np.linalg.norm(mean))


if __name__ == "__main__":
    PLOTS.mkdir(exist_ok=True)
    relevance_loop(PLOTS / "04_relevance_loop.png")
    ubi_pipeline(PLOTS / "05_ubi_pipeline.png")
    ordering(PLOTS / "07_ordering.png")
    vector_inversion(PLOTS / "09_vector_inversion.png")
    epsilon_dial(PLOTS / "13_epsilon_dial.png")
    trust_boundary(PLOTS / "28_trust_boundary.png")
    cancellation(PLOTS / "21_cancellation.png")
