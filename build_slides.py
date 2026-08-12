"""
Build the conference deck from the plan in TALK_STRUCTURE.md.

    python build_slides.py

Writes ldp_for_search_slides.pptx. Re-run it after editing the SLIDES list below.
Speaker notes are attached to every slide.

Only python-pptx and Pillow are needed:

    pip install python-pptx
"""

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).parent
PLOTS = HERE / "plots"
OUTPUT = HERE / "ldp_for_search_slides.pptx"

# 16:9
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

INK = RGBColor(0x14, 0x1B, 0x2D)      # near-black navy, body text
MUTED = RGBColor(0x5A, 0x64, 0x7A)    # secondary text
ACCENT = RGBColor(0x00, 0x5E, 0xB8)   # primary blue
WARN = RGBColor(0xB4, 0x31, 0x1A)     # for the "this is the catch" moments
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
BAND = RGBColor(0x0E, 0x1A, 0x2F)     # dark slides that mark a demo or a turn

TITLE_FONT = "Helvetica Neue"
BODY_FONT = "Helvetica Neue"

# EMU. Width of the "-   " bullet prefix, used for the hanging indent.
HANGING_INDENT = 342900


# ----------------------------------------------------------------------------
# Slide content. Each entry is (kind, payload, speaker_notes).
# ----------------------------------------------------------------------------

SLIDES = [
    ("title", {
        "title": "Leveraging LDP for High-Trust OpenSearch UBI",
        "subtitle": "Keeping relevance work alive when you cannot store the queries",
        "footer": "Jeff Zemerick",
        "event": "OpenSearchCon, San Jose",
        "date": "September 24, 2026",
    }, "Open by naming the tension. We need behavioural data to tune relevance, and we are "
       "increasingly not allowed to keep it. This talk is about doing both."),

    ("bullets", {
        "title": "About me",
        "bullets": [
            "Independent consultant, Mountain Fog",
            "OpenSearch UBI and opensearch-migrations maintainer",
            "Apache Software Foundation member, OpenNLP PMC Chair",
            "PII redaction tooling at Philterd",
            "Works in search, NLP, and privacy",
        ],
    }, "Keep this to about 30 seconds. The credential that matters for this talk is the PII "
       "redaction work, because it is why the privacy problem is familiar rather than academic. "
       "The UBI maintainership is why the OpenSearch half is credible. Do not read the list."),

    # ---------------- Act 1. The blocker ----------------
    ("section", {"eyebrow": "Act 1", "title": "The blocker"},
     "About 8 minutes. Goal is that everyone understands the problem before any code appears."),

    ("bullets", {
        "title": "To tune search, you have to see what users do",
        "bullets": [
            "Relevance work is empirical, not theoretical",
            "Which queries fire, which results get clicked, at which position",
            "Learning-to-rank trains on exactly this signal",
            "Without it you are guessing, and shipping guesses to production",
        ],
    }, "Establish that behavioural data is not a nice-to-have. It is the input to the entire "
       "discipline. Everything after this depends on the audience accepting that."),

    ("bullets", {
        "title": "OpenSearch UBI exists for this",
        "bullets": [
            "ubi_queries:  user_query, query_id, client_id, timestamp",
            "ubi_events:  action_name, object_id, position, session_id, page_id",
            "ubi.js collects interactions in the browser and ships them to the cluster",
            "This is the raw material relevance tuning runs on",
        ],
    }, "Keep this factual and quick. The audience needs the field names because the next slide "
       "points at three of them specifically."),

    ("bullets", {
        "title": "Then legal reads the schema",
        "bullets": [
            "user_query is free text a person typed. It can contain anything",
            "client_id and session_id make it linkable across time",
            "In healthcare and finance, that combination is a hard stop",
            "Zero-trust stopped being a buzzword and became a blocker to relevance tuning",
        ],
        "accent": WARN,
    }, "Be specific. Legal does not object to 'search data' in the abstract. They object to "
       "these fields. Naming them makes the rest of the talk concrete."),

    ("bullets", {
        "title": "Redaction is reactive by construction",
        "bullets": [
            "You collect the PII first, then try to remove it",
            "You discover the failure after the fact, if at all",
            "A free-text query has no schema to redact against",
            "The fix has to be that the sensitive value never leaves the device readable",
        ],
    }, "This is the 'move away from reactive data scrubbing' promise from the abstract. Say "
       "plainly that you build redaction tooling and that it is the right tool for documents at "
       "rest. That makes this a statement about ordering rather than a swipe at a technique, and "
       "it preempts the obvious 'what about redaction' question. Land it as a shape-of-solution "
       "argument, not a tooling argument."),

    # ---------------- Act 2. Embeddings leak ----------------
    ("section", {"eyebrow": "Act 2", "title": "Embeddings are not anonymization"},
     "About 5 minutes. This exists to kill the objection half the room is already forming."),

    ("bullets", {
        "title": "The obvious first idea",
        "bullets": [
            "\"We will not store the text. We will store the embedding.\"",
            "It feels private. It is a vector of floats, not words",
            "It is not private. It is a lossy encoding",
            "Vector inversion recovers the intent",
        ],
    }, "Say the objection out loud in the audience's voice before you refute it. If you skip "
       "this, a good chunk of the room thinks the problem is already solved."),

    ("demo", {
        "title": "Demo: invert a raw query vector",
        "lines": [
            "Notebook sections 1 to 6, then section 9",
        ],
    }, "Read the 20 documents aloud. They fit in one breath. Then run section 9 and let the raw "
       "result speak. Do not rush this, it is the hinge of the talk."),

    ("bullets", {
        "title": "The raw vector gives up the intent",
        "bullets": [
            "Query: \"laptop computer\"",
            "Attacker inverts the raw vector, top hit: Laptop",
            "No text was stored, and the intent leaked anyway",
            "Storing embeddings is not a privacy control",
        ],
        "accent": WARN,
    }, "This is the result the rest of the talk builds on. Pause here."),

    # ---------------- Act 3. Mechanism and verification ----------------
    ("section", {"eyebrow": "Act 3", "title": "The mechanism, and how to verify it"},
     "About 7 minutes. Mechanism briefly, then two verification beats, weakest to strongest."),

    ("bullets", {
        "title": "Local Differential Privacy, in one slide",
        "bullets": [
            "Add calibrated Laplace noise to the query vector on the device",
            "Noise scale = sensitivity / epsilon",
            "Epsilon is the dial. Lower epsilon means more noise and more privacy",
            "The cluster never receives a readable query. There is nothing to scrub",
        ],
    }, "One slide only. Resist the urge to teach differential privacy properly, there is not "
       "time and it is not the point of the talk."),

    ("image", {
        "title": "Verification 1: the noise is what we claim",
        "path": "08_laplace_tent_audit.png",
        "caption": "1,000 draws of the same query. The Laplace tent, centred on the true value.",
    }, "This is the distributional check. It proves the mechanism is implemented correctly. It "
       "does not prove an attacker fails, which is why the next slide exists."),

    ("image", {
        "title": "Verification 2: measure an actual attacker",
        "path": "10_item_vs_class_recovery.png",
        "caption": "42,994 real Wayfair products. Attacker success against epsilon.",
    }, "Stronger evidence than the histogram, because it measures an adversary rather than a "
       "distribution. This discharges the 'verify, do not hope' promise in the abstract."),

    # ---------------- Act 4. The cost ----------------
    ("section", {"eyebrow": "Act 4", "title": "What it costs"},
     "About 7 minutes. Volunteer the weakness before anyone asks. This buys credibility for Act 5."),

    ("bullets", {
        "title": "That first demo was rigged",
        "bullets": [
            "It ran at epsilon 1.2 on a 20 document index",
            "Privacy was excellent. Utility was destroyed",
            "P@1 of 0.07 against a random baseline of 0.05",
            "The attacker learned nothing, and neither did the user",
        ],
        "accent": WARN,
    }, "Say this yourself. If it comes out in Q&A instead, the talk loses. Volunteering it is "
       "what makes Act 5 believable."),

    ("table", {
        "title": "The tradeoff on the toy index",
        "lead": "R@5 holds up long after P@1 collapses. The usable window is epsilon 3 to 5.",
        "columns": ["epsilon", "P@1", "R@5"],
        "rows": [["1.2", "0.07", "0.45"], ["3", "0.38", "0.75"],
                 ["5", "0.72", "0.95"], ["10", "0.98", "1.00"]],
        "footnote": "20 documents. Random chance is P@1 0.05 and R@5 0.25.",
    }, "The useful region is epsilon 3 to 5, where R@5 is high but P@1 has collapsed. Past 10 "
       "the noise stops doing anything."),

    ("table", {
        "title": "A real index: the curves separate",
        "lead": "The category leaks long before the item. At epsilon 10, 0.63 against 0.13.",
        "columns": ["epsilon", "item P@1", "class P@1"],
        "rows": [["5", "0.04", "0.33"], ["10", "0.13", "0.63"],
                 ["20", "0.42", "0.82"], ["50", "0.93", "0.98"]],
        "footnote": "Chance is item 0.00002 and class 0.026. WANDS, 42,994 products, 861 classes.",
    }, "Around epsilon 10 to 20 the attacker recovers the category but not the item. That gap is "
       "the honest version of the privacy claim, and far more defensible than 'they get gibberish'."),

    # ---------------- Act 5. What you keep ----------------
    ("section", {"eyebrow": "Act 5", "title": "What you keep"},
     "About 8 minutes. This is the payoff and the answer to Act 4. Give it the most room."),

    ("bullets", {
        "title": "The asymmetry is the whole point",
        "bullets": [
            "Laplace noise is zero-mean",
            "It cancels when you average over many independent users",
            "One person's query is unrecoverable",
            "The trend across ten thousand people is not",
        ],
        "accent": ACCENT,
    }, "This is the conceptual core of the talk. Everything before it was setup. LDP is not a "
       "privacy tax, it is a trade of individual resolution for population accuracy."),

    ("demo", {
        "title": "Demo: cohorts of real users",
        "lines": [
            "Notebook section 11",
            "480 real WANDS queries, grouped into 5 cohorts",
            "Every user privatizes independently, on their own device",
        ],
    }, "Stress that no cohort member sends a readable query, and the server does the aggregation "
       "on noised vectors only. There is no trusted intermediate step."),

    ("table", {
        "title": "Individuals hide. The crowd does not.",
        "columns": ["cohort", "individual", "chance", "cohort ID"],
        "rows": [
            ["Wall Art", "0.020", "0.014", "OK"],
            ["Accent Chairs", "0.020", "0.027", "OK"],
            ["Beds", "0.063", "0.026", "OK"],
            ["Area Rugs", "0.070", "0.031", "OK"],
            ["Coffee & Cocktail Tables", "0.030", "0.025", "OK"],
        ],
        "footnote": "epsilon 1.0, heavier noise than anything in Act 4. 20,000 users per cohort. 5 of 5 recovered.",
    }, "Individual recovery runs at roughly 1x to 2.5x chance, which is not usable. Aggregate "
       "recovery is exact. Same data, same epsilon, two different questions."),

    ("image", {
        "title": "Error falls as 1 / sqrt(n), exactly as theory says",
        "path": "11_aggregate_convergence.png",
        "caption": "Doubling the privacy budget is expensive. Four times the users is free.",
    }, "The centrepiece. Measured error tracks theory across four orders of magnitude. Point at "
       "the crossing with the red line, that is the next slide."),

    ("bullets", {
        "title": "The number to take home",
        "bullets": [
            "Error drops below the spread of the index at roughly 2,500 users",
            "Segments with thousands of users are measurable under LDP",
            "Segments with dozens are not",
            "Your head terms work. Your long tail does not",
        ],
        "accent": ACCENT,
    }, "Give the audience one operational number they can apply on Monday. This is it."),

    ("statement", {
        "text": "LDP does not cost you your analytics.\nIt costs you the ability to ask about one person.",
    }, "The reframe. Every input relevance tuning actually needs is a population statistic. Let "
       "this sit on screen for a beat before moving on."),

    # ---------------- Act 6. Back to OpenSearch ----------------
    ("section", {"eyebrow": "Act 6", "title": "Back to OpenSearch, and the limits"},
     "About 7 minutes. Land the integration, then be honest about what does not work."),

    ("bullets", {
        "title": "Where the noise gets injected",
        "bullets": [
            "In ubi.js, on the device, before the event is sent",
            "The cluster stores noised vectors and never sees the raw query",
            "Aggregation happens at query time over the noised data",
            "Nothing downstream needs to be trusted, because nothing downstream has the original",
        ],
    }, "The architectural payoff. The trust boundary moves to the device, which is the only place "
       "the raw query legitimately exists."),

    ("bullets", {
        "title": "What your dashboards can still compute",
        "bullets": [
            "Aggregate query intent per segment",
            "Demand trends and shifts over time",
            "Cohort-level training signal for learning-to-rank",
            "What they cannot do is show you one user's session",
        ],
    }, "Tie back to the abstract's promise about LTR and query-intent analysis. Then name the "
       "thing that genuinely goes away."),

    ("bullets", {
        "title": "The limits, stated plainly",
        "bullets": [
            "The category leaks. Harmless for furniture, maybe not for a medical corpus",
            "Epsilon does not transfer between indexes. It depends on coordinate spread",
            "Low-traffic segments stay unmeasurable",
            "Clicks are counts, not vectors, and want randomized response instead",
        ],
        "accent": WARN,
    }, "Every one of these is a question someone will ask. Answering them first is cheaper than "
       "answering them under pressure. Also mention that a formal epsilon-DP claim needs "
       "sensitivity calibrated to the true coordinate range."),

    # ---------------- Close ----------------
    ("bullets", {
        "title": "Takeaways",
        "bullets": [
            "Storing embeddings instead of text is not privacy",
            "Noise at the source beats scrubbing after the fact",
            "Verify the mechanism by attacking it, not by trusting it",
            "You trade individual resolution for population accuracy, and relevance only needs the latter",
        ],
        "accent": ACCENT,
    }, "Four sentences. If someone remembers only one, it should be the last."),

    ("title", {
        "title": "Questions",
        "subtitle": "github.com/jzonthemtn/ldp-for-search",
        "footer": "Jeff Zemerick",
        "event": "OpenSearchCon, San Jose",
        "date": "September 24, 2026",
    }, "Have the notebook open on the convergence plot behind you during Q&A. Likely questions: "
       "formal DP guarantee, why PCA, composition across repeated queries from one user, why not "
       "just hash the query."),
]


# ----------------------------------------------------------------------------
# Rendering helpers
# ----------------------------------------------------------------------------

def _textbox(slide, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True
    return frame


def _style(run, size, bold=False, color=INK, font=BODY_FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def _fill(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _rule(slide, top, color=ACCENT, width=Inches(1.6)):
    """Short accent rule under a title."""
    bar = slide.shapes.add_shape(1, Inches(0.9), top, width, Pt(4))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    bar.shadow.inherit = False


def _wrapped_lines(text, size_pt, box_width_in):
    """
    Estimate how many lines a title will occupy.

    python-pptx cannot measure rendered text, and a two-line title used to collide with
    the accent rule underneath it. Approximating an average bold-sans glyph at half the
    point size is crude but errs on the safe side, which is all this needs to do.
    """
    chars_per_line = max(1, int(box_width_in / (0.5 * size_pt / 72)))
    return max(1, -(-len(text) // chars_per_line))


def _title_block(slide, text, top_in, size, accent, width_in=11.5):
    """Draw a slide title and return the top of the accent rule beneath it."""
    lines = _wrapped_lines(text, size, width_in)
    frame = _textbox(slide, Inches(0.9), Inches(top_in),
                     Inches(width_in), Inches(0.55 * lines + 0.5))
    run = frame.paragraphs[0].add_run()
    run.text = text
    _style(run, size, bold=True, color=INK, font=TITLE_FONT)

    line_height_in = size * 1.22 / 72
    rule_top = Inches(top_in + lines * line_height_in + 0.12)
    _rule(slide, rule_top, accent)
    return lines


def _notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# Slide kinds rendered on the dark band, which need a light page number
DARK_KINDS = {"title", "section", "demo"}


def _slide_number(slide, number, dark):
    """Page number in the bottom right. Skipped on the opening slide."""
    # Right edge lands on the same 0.9in margin the titles and bullets use
    frame = _textbox(slide, Inches(11.38), Inches(6.72), Inches(1.05), Inches(0.45))
    para = frame.paragraphs[0]
    para.alignment = PP_ALIGN.RIGHT
    run = para.add_run()
    run.text = str(number)
    _style(run, 13, color=RGBColor(0x6E, 0x7C, 0x93) if dark else MUTED)


def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def render_title(prs, d):
    slide = _blank(prs)
    _fill(slide, BAND)
    frame = _textbox(slide, Inches(0.9), Inches(2.3), Inches(11.5), Inches(2.6))
    p = frame.paragraphs[0]
    _style(p.add_run(), 1)
    p.runs[0].text = d["title"]
    _style(p.runs[0], 48, bold=True, color=PAPER, font=TITLE_FONT)

    p2 = frame.add_paragraph()
    p2.space_before = Pt(14)
    r2 = p2.add_run()
    r2.text = d["subtitle"]
    _style(r2, 26, color=RGBColor(0x8E, 0xB8, 0xE8))

    foot = _textbox(slide, Inches(0.9), Inches(6.05), Inches(11.5), Inches(1.0))
    rf = foot.paragraphs[0].add_run()
    rf.text = d["footer"]
    _style(rf, 18, bold=True, color=RGBColor(0xC5, 0xCF, 0xE0))

    for i, line in enumerate([d.get("event"), d.get("date")]):
        if not line:
            continue
        p = foot.add_paragraph()
        p.space_before = Pt(4 if i == 0 else 1)
        run = p.add_run()
        run.text = line
        _style(run, 15, color=RGBColor(0x7C, 0x88, 0x9E))
    return slide


def render_section(prs, d):
    slide = _blank(prs)
    _fill(slide, BAND)
    frame = _textbox(slide, Inches(0.9), Inches(2.8), Inches(11.5), Inches(2.0))
    p = frame.paragraphs[0]
    r = p.add_run()
    r.text = d["eyebrow"].upper()
    _style(r, 18, bold=True, color=RGBColor(0x5A, 0x9B, 0xE8))

    p2 = frame.add_paragraph()
    p2.space_before = Pt(10)
    r2 = p2.add_run()
    r2.text = d["title"]
    _style(r2, 42, bold=True, color=PAPER, font=TITLE_FONT)
    return slide


def render_bullets(prs, d):
    slide = _blank(prs)
    _fill(slide, PAPER)
    accent = d.get("accent", ACCENT)

    lines = _title_block(slide, d["title"], 0.7, 34, accent)

    body = _textbox(slide, Inches(0.9), Inches(2.25 + 0.55 * (lines - 1)),
                    Inches(11.5), Inches(4.4 - 0.55 * (lines - 1)))
    for i, text in enumerate(d["bullets"]):
        p = body.paragraphs[0] if i == 0 else body.add_paragraph()
        p.space_after = Pt(20)

        # Hanging indent, so a bullet that wraps lines up under its own text
        # instead of running back out to the left margin
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', str(HANGING_INDENT))
        pPr.set('indent', str(-HANGING_INDENT))

        dot = p.add_run()
        dot.text = "-   "
        _style(dot, 24, bold=True, color=accent)
        run = p.add_run()
        run.text = text
        _style(run, 24, color=INK)
    return slide


def render_demo(prs, d):
    slide = _blank(prs)
    _fill(slide, BAND)

    tag = _textbox(slide, Inches(0.9), Inches(1.9), Inches(11.5), Inches(0.6))
    rt = tag.paragraphs[0].add_run()
    rt.text = "LIVE NOTEBOOK"
    _style(rt, 18, bold=True, color=RGBColor(0x5A, 0x9B, 0xE8))

    head = _textbox(slide, Inches(0.9), Inches(2.6), Inches(11.5), Inches(1.2))
    r = head.paragraphs[0].add_run()
    r.text = d["title"]
    _style(r, 38, bold=True, color=PAPER, font=TITLE_FONT)

    body = _textbox(slide, Inches(0.9), Inches(4.1), Inches(11.5), Inches(2.0))
    for i, line in enumerate(d["lines"]):
        p = body.paragraphs[0] if i == 0 else body.add_paragraph()
        p.space_after = Pt(12)
        run = p.add_run()
        run.text = line
        _style(run, 22, color=RGBColor(0xB8, 0xC2, 0xD4))
    return slide


def render_image(prs, d):
    slide = _blank(prs)
    _fill(slide, PAPER)

    head = _textbox(slide, Inches(0.9), Inches(0.45), Inches(11.5), Inches(0.9))
    r = head.paragraphs[0].add_run()
    r.text = d["title"]
    _style(r, 30, bold=True, color=INK, font=TITLE_FONT)

    path = PLOTS / d["path"]
    with Image.open(path) as img:
        aspect = img.width / img.height

    avail_h = Inches(4.75)
    avail_w = Inches(11.4)
    height = avail_h
    width = Emu(int(height * aspect))
    if width > avail_w:
        width = avail_w
        height = Emu(int(width / aspect))

    slide.shapes.add_picture(
        str(path),
        Emu(int((SLIDE_W - width) / 2)),
        Inches(1.55),
        width=width, height=height,
    )

    cap = _textbox(slide, Inches(0.9), Inches(6.55), Inches(11.5), Inches(0.7))
    cap.paragraphs[0].alignment = PP_ALIGN.CENTER
    rc = cap.paragraphs[0].add_run()
    rc.text = d["caption"]
    _style(rc, 16, color=MUTED)
    return slide


def render_table(prs, d):
    slide = _blank(prs)
    _fill(slide, PAPER)

    _title_block(slide, d["title"], 0.7, 32, ACCENT)

    table_top = 2.3
    if d.get("lead"):
        lead = _textbox(slide, Inches(0.9), Inches(1.85), Inches(11.5), Inches(0.6))
        rl = lead.paragraphs[0].add_run()
        rl.text = d["lead"]
        _style(rl, 21, color=MUTED)
        table_top = 2.75

    cols = d["columns"]
    rows = d["rows"]
    width = Inches(10.0)
    height = Inches(0.62) * (len(rows) + 1)
    shape = slide.shapes.add_table(
        len(rows) + 1, len(cols),
        Emu(int((SLIDE_W - width) / 2)), Inches(table_top), width, height,
    )
    table = shape.table
    table.first_row = True

    for c, name in enumerate(cols):
        cell = table.cell(0, c)
        cell.text = name
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        para = cell.text_frame.paragraphs[0]
        para.alignment = PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
        _style(para.runs[0], 18, bold=True, color=PAPER)
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT

    for rix, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.cell(rix, c)
            cell.text = value
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
            _style(para.runs[0], 18, color=INK)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                RGBColor(0xF4, 0xF7, 0xFB) if rix % 2 else PAPER)

    note = _textbox(slide, Inches(0.9), Inches(6.5), Inches(11.5), Inches(0.7))
    note.paragraphs[0].alignment = PP_ALIGN.CENTER
    rn = note.paragraphs[0].add_run()
    rn.text = d["footnote"]
    _style(rn, 15, color=MUTED)
    return slide


def render_statement(prs, d):
    slide = _blank(prs)
    _fill(slide, PAPER)
    frame = _textbox(slide, Inches(1.1), Inches(2.5), Inches(11.1), Inches(2.6))
    for i, line in enumerate(d["text"].split("\n")):
        p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        p.space_after = Pt(16)
        run = p.add_run()
        run.text = line
        _style(run, 34, bold=(i == 0), color=INK if i == 0 else ACCENT, font=TITLE_FONT)
    return slide


RENDERERS = {
    "title": render_title,
    "section": render_section,
    "bullets": render_bullets,
    "demo": render_demo,
    "image": render_image,
    "table": render_table,
    "statement": render_statement,
}


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    for number, (kind, payload, notes) in enumerate(SLIDES, start=1):
        slide = RENDERERS[kind](prs, payload)
        _notes(slide, notes)
        if number > 1:  # the opening title slide stays clean
            _slide_number(slide, number, kind in DARK_KINDS)

    prs.save(OUTPUT)
    print(f"wrote {OUTPUT.name}: {len(SLIDES)} slides")
    counts = {}
    for kind, _, _ in SLIDES:
        counts[kind] = counts.get(kind, 0) + 1
    print("  " + ", ".join(f"{k} x{v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    build()
