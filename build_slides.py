"""
Build the conference deck from the plan in TALK_STRUCTURE.md.

    python build_slides.py

Writes ldp_for_search_slides.pptx. Re-run it after editing the SLIDES list below.
Speaker notes are attached to every slide.

Only python-pptx and Pillow are needed:

    pip install python-pptx
"""

import re
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).parent
PLOTS = HERE / "plots"
OUTPUT = HERE / "ldp_for_search_slides.pptx"
NOTES_OUTPUT = HERE / "SPEAKER_NOTES.md"
FEEDBACK_QR = HERE / "leveraging-ldp-for-high-trust-opensearch-ubi_zemerick_1212636_feedback-code.png"

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
MONO_FONT = "Consolas"   # for field names; ships with Office on macOS and Windows

# EMU. Width of the "-   " bullet prefix, used for the hanging indent.
HANGING_INDENT = 342900


# ----------------------------------------------------------------------------
# Slide content. Each entry is (kind, payload, speaker_notes).
# ----------------------------------------------------------------------------

SLIDES = [
    ("title", {
        "title": "Leveraging LDP for High-Trust OpenSearch UBI",
        "subtitle": "Tuning search when you can't store the queries",
        "footer": "Jeff Zemerick",
        "event": "OpenSearchCon NA",
        "date": "September 24, 2026",
    }, "Open by naming the tension. We need behavioural data to tune relevance, and we are "
       "increasingly not allowed to keep it. This talk is about doing both."),

    ("bullets", {
        "title": "About me",
        "bullets": [
            "Independent consultant at Mountain Fog",
            "OpenSearch UBI and opensearch-migrations maintainer",
            "Apache Software Foundation member, OpenNLP PMC Chair",
            "PII redaction tooling at Philterd",
            "Works in search, NLP, and privacy",
        ],
        "link": {"text": "jeffzemerick.dev", "url": "https://jeffzemerick.dev"},
    }, "Keep this to about 30 seconds. The credential that matters for this talk is the PII "
       "redaction work, because it is why the privacy problem is familiar rather than academic. "
       "The UBI maintainership is why the OpenSearch half is credible. Do not read the list."),

    # ---------------- Part 1. The blocker ----------------
    ("section", {"eyebrow": "Part 1", "title": "The problem"},
     "About 8 minutes. Goal is that everyone understands the problem before any code appears."),

    ("bullets", {
        "title": "To tune search you have to see what users do",
        "bullets": [
            "Relevance is measured",
            "Which queries fire, which results get clicked, at which position",
            "Learning-to-rank trains on exactly this signal",
            "Without it you are guessing, and shipping guesses to production",
        ],
        "image": {"path": "04_relevance_loop.png"},
    }, "Establish that behavioural data is not a nice-to-have. It is the input to the entire "
       "discipline. Everything after this depends on the audience accepting that."),

    ("bullets", {
        "title": "OpenSearch UBI exists for this",
        "bullets": [
            "`ubi_queries`:  `user_query, query_id, client_id, timestamp`",
            "`ubi_events`:  `action_name, object_id, position, session_id, page_id`",
            "`ubi.js` collects interactions in the browser and ships them to the cluster",
            "This is the raw material relevance tuning runs on",
        ],
        "image": {"path": "05_ubi_pipeline.png"},
        "link": {"text": "ubisearch.dev", "url": "https://ubisearch.dev",
                 "lead": "For examples and code, go to", "size": 17},
    }, "Keep this factual and quick. The audience needs the field names because the next slide "
       "points at three of them specifically."),

    ("bullets", {
        "title": "Legal rules won't let us see the user queries",
        "bullets": [
            "`user_query` is free text and can contain *anything*",
            "Telling users not to enter PII or PHI does not stop them",
            "`client_id` and `session_id` make it linkable across time",
            "Zero-trust becomes a blocker to relevance tuning",
            "This applies to any behavioral data, not just search tuning",
        ],
        "accent": WARN,
    }, "Be specific. Legal does not object to 'search data' in the abstract. They object to "
       "these fields. Naming them makes the rest of the talk concrete. Know which half you are "
       "about to solve: everything after this addresses user_query. The identifiers are dealt "
       "with on the limitations slide, so do not imply here that they go away too."),

    ("bullets", {
        "title": "Redaction is reactive and sometimes too late",
        "bullets": [
            "You collect the PII first, then try to remove it",
            "Leaked PII is discovered later",
            "A free-text query has no schema to redact against",
            "The fix has to be that the sensitive value never leaves the device readable",
        ],
        "image": {"path": "07_ordering.png"},
        "note": {"lead": "Still need to redact data at rest?",
                 "text": "philterd.ai", "url": "https://philterd.ai"},
    }, "This is the 'move away from reactive data scrubbing' promise from the abstract. Say "
       "plainly that you build redaction tooling and that it is the right tool for documents at "
       "rest. That makes this a statement about ordering rather than a swipe at a technique, and "
       "it preempts the obvious 'what about redaction' question. Land it as a shape-of-solution "
       "argument, not a tooling argument."),

    # ---------------- Part 2. Embeddings leak ----------------
    ("section", {"eyebrow": "Part 2", "title": "Embeddings are not anonymization"},
     "About 5 minutes. This exists to kill the objection half the room is already forming."),

    ("bullets", {
        "title": "The obvious first idea",
        "bullets": [
            "\"We will not store the text. We will store the embedding.\"",
            "It's numbers, not words",
            "It is not private, just a lossy encoding",
            "Vector inversion recovers the intent",
        ],
        "image": {"path": "09_vector_inversion.png"},
        "note": {"lead": "Morris et al., Text Embeddings Reveal (Almost) As Much As Text:",
                 "text": "arxiv.org/abs/2310.06816",
                 "url": "https://arxiv.org/abs/2310.06816"},
    }, "Say the objection out loud in the audience's voice before you refute it. If you skip "
       "this, a good chunk of the room thinks the problem is already solved."),

    ("table", {
        "title": "The same attack on both vectors",
        "lead": "The attacker looks up the nearest documents to whatever vector they intercepted",
        "columns": ["Attacker intercepts", "Their best guess", "Distance"],
        "rows": [
            ["The raw vector", "Laptop", "0.2092"],
            ["The noised vector", "Gaming Console", "4.8870"],
        ],
        "footnote": "Query \"laptop computer\" at epsilon 1.2, from notebook section 9",
    }, "Notebook section 9, run beforehand rather than live. Read the 20 documents aloud first, "
       "they fit in one breath, so the room can hold the whole index in their heads. Then let "
       "the top row speak: the raw vector hands over the intent. Do not rush this, it is the "
       "hinge of the talk. The distance column is the part people miss, so point at it. The "
       "noised vector is not merely wrong, it is 4.9 away from everything, so which document "
       "wins is close to arbitrary. The number to have ready if someone wants it: its top "
       "five candidates all sit within 0.15 of each other, while real documents in this index "
       "are at least 0.89 apart, so the ranking is a tie rather than a wrong answer. "
       "Two things to be straight about if asked. This is a "
       "nearest-neighbour lookup against the index rather than literal text inversion, which "
       "is a weaker attacker than the Morris paper on the previous slide assumes, and it still "
       "succeeds. And epsilon 1.2 is the rigged setting the epsilon sweep later confesses to."),

    ("bullets", {
        "title": "The raw vector gives up the intent",
        "bullets": [
            "Query: \"laptop computer\"",
            "Attacker inverts the raw vector, top hit: Laptop",
            "Intent was leaked even though no text was stored",
            "Storing embeddings is not a privacy control",
        ],
        "accent": WARN,
        "bold": -1,
    }, "This is the result the rest of the talk builds on. Pause here."),

    # ---------------- Part 3. Mechanism and verification ----------------
    ("section", {"eyebrow": "Part 3", "title": "The fix and the proof"},
     "About 7 minutes. Mechanism briefly, then two verification beats, weakest to strongest."),

    ("bullets", {
        "title": "Local Differential Privacy",
        "bullets": [
            "The vector was never the problem, storing it readable was",
            "Add calibrated noise to the query vector on the device",
            "Epsilon is the dial, and lower epsilon means more noise and more privacy",
            "The user's query is not stored so there is nothing to redact",
        ],
        "image": {"path": "13_epsilon_dial.png"},
        "note": {"lead": "More on local differential privacy:",
                 "text": "en.wikipedia.org/wiki/Local_differential_privacy",
                 "url": "https://en.wikipedia.org/wiki/Local_differential_privacy"},
    }, "One slide only. Resist the urge to teach differential privacy properly, there is not "
       "time and it is not the point of the talk. The noise is Laplace, but the word can wait "
       "for the next slide, where the shape is on screen and does the explaining for you. If "
       "someone asks here, one sentence: symmetric noise, equally likely to push the value up "
       "or down, centered on the truth. The formula is deliberately off the slide. If someone "
       "asks, the noise scale is sensitivity over epsilon, and sensitivity here is 1.0 per "
       "coordinate on vectors whose whole norm is 1, which is conservative rather than tight. "
       "The notes file has the longer answer. Do not volunteer the word, it is the only term in "
       "the deck with no definition behind it."),

    ("image", {
        "title": "Verification 1: the noise",
        "path": "08_laplace_tent_audit.png",
        "caption": "A biased mechanism would put the peak off the red line, and the spread is "
                   "the privacy.",
    }, "This is the distributional check. It proves the mechanism is implemented correctly. It "
       "does not prove an attacker fails, which is why the next slide exists. Say what the "
       "thousand is, because the title does not: one query, one coordinate of its vector, and "
       "a thousand independent noise draws on that same true value. You cannot audit a random "
       "mechanism from one sample, so you repeat it until the shape shows. Then head off the "
       "objection someone in the room is already forming. Yes, averaging those thousand draws "
       "recovers the true value, which is exactly what the peak landing on the red line shows. "
       "That is the auditor's view rather than a usage pattern: a query is privatized once, on "
       "submit. The moment one person emits the same query a thousand times, an attacker can "
       "average it back, which is why the appendix says privatize on submit and never per "
       "keystroke. It is the asymmetry the payoff rests on, pointed the other way. Many draws from one "
       "person breaks privacy, one draw each from many people preserves it."),

    ("image", {
        "title": "A higher epsilon is a narrower spread",
        "path": "08b_epsilon_spread_comparison.png",
        "caption": "Both panels share one x axis. At epsilon 10 almost every draw lands on "
                   "the red line.",
    }, "The dial, made visible. Same query, same coordinate, same thousand draws. Only epsilon "
       "differs. The scale is one over epsilon, so 1.2 gives 0.833 and 10 gives 0.100, about "
       "eight times narrower. Say why the shared x axis matters: let each panel scale itself "
       "and they look identical, which is the opposite of the point. Then land both halves of "
       "the trade. At epsilon 10 the noise is finally smaller than the index itself, 0.141 "
       "against a coordinate spread of 0.171, which is why the next part shows utility jumping "
       "from 0.72 to 0.98 between epsilon 5 and 10. And that is also the cost: a spread this "
       "narrow means someone reading a single sample is reading the true value. There is no "
       "setting that is private and accurate for one query, which is what the payoff slides "
       "exist to answer."),

    ("image", {
        "title": "Verification 2: measure an actual attacker",
        "path": "10_item_vs_class_recovery.png",
        "caption": "The category leaks well before the item does.",
        "note": {"lead": "Data: WANDS, Wayfair product search relevance (ECIR 2022), MIT licensed:",
                 "text": "github.com/wayfair/WANDS",
                 "url": "https://github.com/wayfair/WANDS"},
    }, "Stronger evidence than the histogram, because it measures an adversary rather than a "
       "distribution. This discharges the 'verify, do not hope' promise in the abstract. "
       "Head off the obvious confusion: the previous slide used epsilon 1.2 and this axis runs "
       "to 200. Epsilon is not portable between indexes, because what matters is the noise "
       "scale relative to the spread of the coordinates, and that spread differs between the "
       "20-document PCA and this 43,000-document one. On the baselines: the query is 'solid "
       "wood platform bed', whose class Beds holds 1,112 of the 42,994 products, so class "
       "chance is 2.6 percent and item chance 0.002 percent. Class recovery of 6 percent at "
       "epsilon 1 is low but not nothing. Do not oversell the item curve either: 13 percent at "
       "epsilon 10 is still about 5,600 times chance, so the claim is that the category leaks "
       "first, not that the item is safe. This is where the limitations slide gets its first "
       "bullet, so it lands later as a callback rather than a new admission."),

    ("image", {
        "title": "Epsilon 1.2 is barely better than guessing",
        "path": "07_epsilon_tradeoff_toy_index.png",
        "caption": "The red line is where the Part 2 demo ran. Utility only comes back where "
                   "the attacker wins too.",
    }, "Volunteer the confession here, because no slide makes it for you any more. That demo "
       "back in Part 2 was rigged: epsilon 1.2 on a twenty document index, where the attacker "
       "learned nothing and neither did the user. Say it yourself. If it comes out in Q&A "
       "instead, the talk loses, and volunteering it is what makes the payoff believable. Go to "
       "the red line first and stay there. That is the demo from Part 2, with the top hit "
       "correct 7 percent of the time against a 5 percent baseline, and the top five 45 "
       "against 25. Barely above guessing. Then sweep right to make the second point, that utility only returns as "
       "epsilon rises, and by then the attacker is reading the query too. Note the curves rise "
       "here where slide 16's rose for the attacker: up means the search still works. Exact "
       "values if asked: at epsilon 1.2, P@1 0.07 and R@5 0.45; at 3, 0.38 and 0.75; at 5, "
       "0.72 and 0.95; at 10, 0.98 and 1.00. Resist calling epsilon 3 to 5 a usable window. "
       "P@1 of 0.38 is eight times chance, so the attacker is already doing well there. The "
       "honest version of that argument needs the real index, which is the next slide."),

    ("bullets", {
        "title": "You lose the person and keep the pattern",
        "bullets": [
            "The noise cancels when you average over many users",
            "One person's query is unrecoverable",
            "The trend across ten thousand people is not",
            "That trend is all UBI needs to tune relevance",
        ],
        "image": {"path": "21_cancellation.png"},
        "accent": ACCENT,
    }, "This is the conceptual core of the talk. Everything before it was setup. LDP is not a "
       "privacy tax, it is a trade of individual resolution for population accuracy."),

    ("image", {
        "title": "Error falls as 1 / sqrt(users)",
        "path": "11_aggregate_convergence.png",
        "lead": "Average the noised queries of `n` users in one segment, then see how far that "
                "average lands from the truth.",
        "caption": "The red line is the smallest segment you can measure.",
    }, "The centerpiece, and now the only place section 11's result appears, so open with it. "
       "480 real WANDS queries in five segments, every user privatizing independently on their "
       "own device, no readable query anywhere and no trusted intermediate step. Individual "
       "recovery per segment runs 0.020, 0.020, 0.063, 0.070 and 0.030 against chance of 0.014 "
       "to 0.031, roughly one to two and a half times chance, which is not usable. Segment "
       "identification is 5 of 5, exact. Same data, same epsilon of 1.0, two different "
       "questions. Then the plot. Take the shape first. More users, less error. The measured green "
       "line tracks the predicted grey one across four orders of magnitude. This is ordinary "
       "statistics, so say so: averaging n independent things shrinks the noise as one over "
       "root n, the same reason a poll of four thousand beats one of one thousand. Nothing "
       "here is special to privacy. Then the red line. Read it off the bottom axis: 2,300 "
       "users. That is the answer, and it is the next slide. If asked where 2,300 comes from, "
       "it is where the measured error drops under 0.128, the average spread of one "
       "coordinate across the index. That bar is strict on purpose. Two typical products sit "
       "about 0.82 apart, so the line is roughly six times stricter than just telling "
       "products apart."),

    ("bullets", {
        "title": "How big a segment has to be",
        "bullets": [
            "Error drops below the spread of the index at roughly 2,300 users",
            "That is at epsilon 1, and halving epsilon needs four times the users",
            "Segments with thousands of users are measurable under LDP",
            "Segments with dozens are not measurable",
            "Your head terms work, but your long tail does not",
        ],
        "accent": ACCENT,
    }, "Give the audience one operational number they can apply on Monday. This is it. The "
       "2,300 is where the measured error crosses the spread of the index, 0.128, on the "
       "convergence plot. It is not a constant: error goes as one over epsilon times one over "
       "root n, so the threshold scales as one over epsilon squared. At epsilon 0.5 it is "
       "about 9,200 users, at epsilon 2 it is about 575."),

    ("bullets", {
        "title": "So how do you pick epsilon",
        "bullets": [
            "Start at epsilon 1, then measure",
            "Pick it for the privacy you need, because utility also depends on the number of users",
            "Segments too small? Add users or widen them, and leave epsilon alone",
        ],
        "accent": ACCENT,
        "emphasize": -1,
    }, "The question everyone is holding, answered now that they have seen the evidence for "
       "every step. Step one is the reframe: there is no epsilon that is private and accurate "
       "for one query, so stop looking for it on the tradeoff curve. Point back to the attack "
       "curve for step two, because that is how you measure what an epsilon buys on an index "
       "you actually run. Step three is the convergence plot and the previous slide. Step four "
       "is the whole talk in one line: error goes as one over epsilon times one over root n, "
       "so privacy rides on epsilon alone while accuracy has two dials, and n is the one that "
       "costs nothing. If someone wants a starting number, say epsilon 1 on an index like "
       "this one and then measure, rather than giving them a figure to carry home unexamined."),

    ("statement", {
        "text": "LDP does not cost you your analytics.\nIt costs you the ability to ask about one person.",
    }, "The reframe. Every input relevance tuning actually needs is a population statistic. Let "
       "this sit on screen for a beat before moving on."),

    # ---------------- Part 4. Back to OpenSearch ----------------
    ("section", {"eyebrow": "Part 4", "title": "Back in OpenSearch"},
     "About 7 minutes. Land the integration, then be honest about what does not work."),

    ("bullets", {
        "title": "Where the noise gets injected",
        "bullets": [
            "On the device, before `ubi.js` sends the event",
            "Aggregation happens at query time over the noised data",
            "Nothing downstream needs to be trusted, because nothing downstream has the original",
            "You set epsilon in the client you ship",
        ],
        "note": {"lead": "An upcoming UBI RFC will bring this capability into `ubi.js`"},
        "image": {"path": "28_trust_boundary.png"},
    }, "Say up front that none of this is built into UBI today. ubi.js is a serializer, and the "
       "embedding, the projection and the noise are code the adopter writes and runs before "
       "handing the request to trackQuery. The notes file has the call shape and the two ways "
       "to get it wrong. "
       "The architectural payoff. The trust boundary moves to the device, which is the only place "
       "the raw query legitimately exists. The last bullet answers the obvious objection, that the "
       "people collecting the data are the ones choosing how much privacy users get. True, and the "
       "standing critique of deployed LDP. The web deployment is the answer: because the mechanism "
       "ships as JavaScript, a user, an auditor or a regulator can open devtools and check the "
       "epsilon. A server-side pipeline or a native app cannot make that claim. It turns trust us "
       "into check us, which is the same promise as the rest of the talk."),

    ("image", {
        "title": "What changes in ubi_queries",
        "path": "28_ubi_document.png",
        "note": {"lead": "UBI supports this today through `query_attributes`, and the RFC "
                         "will propose making it first-class"},
    }, "The integration question, answered concretely, and it needs no change to the UBI spec. "
       "query_attributes is typed as a free-form object for exactly this kind of thing, and "
       "the epsilon travels with the record so a reader knows the budget it was collected "
       "under. user_query is emptied rather than dropped because the published schema lists it "
       "as required. Worth knowing if someone asks: the schema contradicts itself there, since "
       "the field also carries a comment saying it is not required, for recommendation systems "
       "with no typed query. Two things to volunteer: the identifiers are deliberately "
       "identical on both sides, which is the limitation two slides later, and every dashboard "
       "that reads user_query breaks, which is the real migration cost. A float array in an "
       "object is not a knn_vector either, so averaging these at query time needs a scripted "
       "aggregation or an explicit vector mapping."),

    ("bullets", {
        "title": "What your dashboards can still compute",
        "bullets": [
            "Aggregate query intent per segment",
            "Demand trends and shifts over time",
            "Segment-level training signal for learning-to-rank",
            "What they cannot do is show you one user's session",
        ],
    }, "Tie back to the abstract's promise about LTR and query-intent analysis. Then name the "
       "thing that genuinely goes away. If anyone presses on the learning-to-rank bullet, be "
       "straight: LTR judgments come from clicks, and this mechanism does not touch clicks, so "
       "that signal survives because it was never protected rather than because LDP preserved "
       "it. The limitations slide says so."),

    ("bullets", {
        "title": "The limitations",
        "bullets": [
            "The category leaks and that is worse for healthcare than furniture",
            "Epsilon values don't transfer between indexes",
            "Long tail queries stay unmeasurable",
            "This protects `user_query` but `ubi_events` still holds clicks and ids in the clear",
        ],
        "accent": WARN,
    }, "Every one of these is a question someone will ask. Answering them first is cheaper than "
       "answering them under pressure. Also mention that a formal epsilon-DP claim needs "
       "sensitivity calibrated to the true coordinate range. Here the vectors are "
       "L2-normalized before PCA, so the whole 20-dimensional vector has norm 1, which makes "
       "sensitivity 1.0 per coordinate conservative rather than tight. That is the answer if "
       "someone asks how sensitivity was set. Two follow-ups come off that bullet. Asked how "
       "often epsilon needs re-tuning, say when you re-embed or refit PCA, because routine "
       "additions to a large index do not move the coordinate spread, and normalizing before "
       "PCA keeps sensitivity itself stable whatever the catalogue holds. Asked whether "
       "privacy decays over time, say yes but not through epsilon: one user's repeated "
       "queries compose, and an attacker who averages that one user's own noised draws "
       "recovers the intent, which is the asymmetry of the payoff turned around. Epsilon is a "
       "budget per release rather than a standing property, so the fix is rotating or "
       "dropping client_id and session_id, not a smaller epsilon. On the long tail, which "
       "someone will ask about: "
       "the workarounds are coarser segments and longer time windows, and both are the same "
       "trade at lower resolution, because they only raise n. The genuinely different answer is "
       "shuffle DP or secure aggregation, which buys far more utility at the same epsilon but "
       "changes the architecture rather than the parameter. Worth adding that tail relevance is "
       "usually improved by retrieval work rather than behavioural signal anyway. On the last "
       "bullet, be direct: this is scoped work, not a finished privacy story for all of UBI. "
       "The query text is covered. Clicks are counts rather than vectors and want randomized "
       "response, and client_id and session_id would need rotating or dropping. That is the "
       "honest answer to the linkability half of the problem raised in Part 1."),

    # ---------------- Close ----------------
    ("bullets", {
        "title": "Takeaways",
        "bullets": [
            "Storing embeddings instead of text is not privacy",
            "Keeping sensitive data out of the index beats redacting it later",
            "Verify the mechanism by testing it, not by trusting it",
            "You trade individual resolution for population accuracy but that's what relevance tuning needs",
        ],
        "accent": ACCENT,
        "emphasize": -1,
    }, "Four sentences. If someone remembers only one, it should be the last."),

    ("title", {
        "title": "Questions",
        "subtitle": "github.com/jzonthemtn/ldp-for-search",
        "footer": "Jeff Zemerick",
        "event": "OpenSearchCon NA",
        "date": "September 24, 2026",
        "qr": FEEDBACK_QR,
        "qr_label": "Session feedback",
    }, "Have the notebook open on the convergence plot behind you during Q&A. Likely questions: "
       "formal DP guarantee, why PCA, composition across repeated queries from one user, why not "
       "just hash the query, and how you actually test the mechanism. That last one is the "
       "takeaway slide's promise, so have the four checks ready, each catching something "
       "different. One, audit the distribution, section 8: privatize one coordinate a thousand "
       "times and confirm the peak sits on the true value and the spread is sensitivity over "
       "epsilon. That catches a mechanism that is not what you claim, a wrong scale or a sign "
       "error, and it is cheap. Two, run an actual attacker, section 10: noise a query, do "
       "nearest neighbour against your real index, and score item and class recovery against "
       "chance across an epsilon sweep. That catches correctly implemented but still leaking, "
       "which is the one that matters. Three, measure the utility cost, section 7, so you know "
       "what the epsilon test two approved leaves you. Four, check the convergence, section 11: "
       "confirm error falls as one over root n. That catches noise that is not independent "
       "across users, a reused seed or a per-session draw, because correlated noise does not "
       "cancel and the measured line flattens away from theory. Two things worth saying: none "
       "of this needs production data, and tests two and four are the ones people skip and the "
       "ones that find real problems."),
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


def _code_runs(paragraph, text, size, color, bold=False):
    """
    Add `text` to a paragraph, rendering `backticked` spans in the mono face and
    *starred* spans in italics.

    Field names are the subject of several slides, so they read as identifiers
    rather than prose. Mono runs drop a point, because the face runs wider than
    Helvetica and an unadjusted span pushes the line into an extra wrap. Both
    markers survive into the speaker notes, where markdown reads them the same way.
    """
    for i, part in enumerate(text.split("`")):
        if not part:
            continue
        if i % 2 == 1:
            run = paragraph.add_run()
            run.text = part
            _style(run, size - 2, bold=bold, color=color, font=MONO_FONT)
            continue
        for j, span in enumerate(part.split("*")):
            if not span:
                continue
            run = paragraph.add_run()
            run.text = span
            _style(run, size, bold=bold, color=color, font=BODY_FONT)
            run.font.italic = j % 2 == 1


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


# Renderers disagree about hyperlink colour: PowerPoint honours the colour set on
# the run, LibreOffice (which produces the PDF) always uses the theme's. The stock
# theme ships pure blue, which is illegible on the dark section slides, so the theme
# gets a value that clears 3:1 on both the white and the dark background.
LINK_THEME = "4A90D9"


def _retheme_links(prs, rgb=LINK_THEME):
    part = prs.slide_master.part.part_related_by(RT.THEME)
    xml = part.blob.decode("utf-8")
    for tag, colour in (("hlink", rgb), ("folHlink", rgb)):
        xml = re.sub(rf"<a:{tag}>.*?</a:{tag}>",
                     f'<a:{tag}><a:srgbClr val="{colour}"/></a:{tag}>', xml, count=1)
    part._blob = xml.encode("utf-8")


def _note_line(slide, note, dark, top=None, center=False):
    """An aside along the bottom of a slide, for a pointer that would derail the body.

    A chart slide already spends the bottom band on its caption, so `top` and
    `center` let the note tuck underneath it and line up with it.
    """
    left, width = (Inches(1.45), Inches(10.4)) if center else (Inches(0.9), Inches(9.8))
    frame = _textbox(slide, left, Inches(6.55) if top is None else top, width, Inches(0.55))
    para = frame.paragraphs[0]
    if center:
        para.alignment = PP_ALIGN.CENTER
    lead = para.add_run()
    para._p.remove(lead._r)
    _code_runs(para, note["lead"] + (" " if note.get("url") else ""), 14,
               RGBColor(0x8E, 0x9B, 0xB2) if dark else MUTED)
    if not note.get("url"):
        return
    link = para.add_run()
    link.text = note["text"]
    link.hyperlink.address = note["url"]
    _style(link, 14, color=RGBColor(0x5A, 0x9B, 0xE8) if dark else ACCENT)
    link.font.underline = True


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

    # Optional QR in the right margin, e.g. the session feedback code on the
    # closing slide. The white pad behind it keeps a quiet zone against the band.
    qr = d.get("qr")
    if qr:
        side = Inches(2.7)
        pad = Inches(0.14)
        left = SLIDE_W - Inches(0.9) - side
        top = Inches(2.3)
        card = slide.shapes.add_shape(1, left - pad, top - pad, side + 2 * pad, side + 2 * pad)
        card.fill.solid()
        card.fill.fore_color.rgb = PAPER
        card.line.fill.background()
        card.shadow.inherit = False
        slide.shapes.add_picture(str(qr), left, top, width=side, height=side)

        label = _textbox(slide, left - pad, top + side + pad + Inches(0.12), side + 2 * pad, Inches(0.4))
        label.paragraphs[0].alignment = PP_ALIGN.CENTER
        rl = label.paragraphs[0].add_run()
        rl.text = d.get("qr_label", "Session feedback")
        _style(rl, 14, color=RGBColor(0x8E, 0xB8, 0xE8))
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

    if d.get("note"):
        _note_line(slide, d["note"], dark=True)
    return slide


def _figure(slide, name, left_in, top_in, max_w_in, max_h_in):
    """Place a plot inside a box, preserving aspect ratio and centring it there."""
    path = PLOTS / name
    with Image.open(path) as img:
        aspect = img.width / img.height

    width, height = Inches(max_w_in), Emu(int(Inches(max_w_in) / aspect))
    if height > Inches(max_h_in):
        height = Inches(max_h_in)
        width = Emu(int(height * aspect))

    slide.shapes.add_picture(
        str(path),
        Emu(int(Inches(left_in) + (Inches(max_w_in) - width) / 2)),
        Emu(int(Inches(top_in) + (Inches(max_h_in) - height) / 2)),
        width=width, height=height,
    )


def render_bullets(prs, d):
    slide = _blank(prs)
    _fill(slide, PAPER)
    accent = d.get("accent", ACCENT)

    # An optional figure sits to the right, and the bullet column gives up the space
    image = d.get("image")
    body_w = 5.6 if image else 11.5
    size = 21 if image else 24

    lines = _title_block(slide, d["title"], 0.7, 34, accent)

    body = _textbox(slide, Inches(0.9), Inches(2.25 + 0.55 * (lines - 1)),
                    Inches(body_w), Inches(4.4 - 0.55 * (lines - 1)))
    # One bullet may be set in the accent colour. Used where the slide has a
    # conclusion the audience is expected to copy down rather than just hear.
    emphasized = d.get("emphasize")
    if emphasized is not None:
        emphasized %= len(d["bullets"])
    # Same addressing, for a bullet that wants weight rather than colour.
    bolded = d.get("bold")
    if bolded is not None:
        bolded %= len(d["bullets"])

    for i, text in enumerate(d["bullets"]):
        p = body.paragraphs[0] if i == 0 else body.add_paragraph()
        p.space_after = Pt(14 if image else 20)

        # Hanging indent, so a bullet that wraps lines up under its own text
        # instead of running back out to the left margin
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', str(HANGING_INDENT))
        pPr.set('indent', str(-HANGING_INDENT))

        dot = p.add_run()
        dot.text = "-   "
        _style(dot, size, bold=True, color=accent)
        _code_runs(p, text, size, accent if i == emphasized else INK, bold=i == bolded)

    link = d.get("link")
    if link:
        link_size = link.get("size", size)
        p = body.add_paragraph()
        p.space_before = Pt(8)
        if link.get("lead"):
            lead = p.add_run()
            lead.text = link["lead"] + " "
            _style(lead, link_size, color=MUTED)
        run = p.add_run()
        run.text = link["text"]
        run.hyperlink.address = link["url"]
        # styled after the hyperlink, so it wins over the theme's link colour
        _style(run, link_size, color=accent)
        run.font.underline = True

    if image:
        _figure(slide, image["path"], left_in=6.85, top_in=2.05,
                max_w_in=5.5, max_h_in=4.4)
    if d.get("note"):
        _note_line(slide, d["note"], dark=False)
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

    # An optional line between title and plot, saying how to read the axes. The
    # caption underneath says what the plot means; this one says what it shows.
    lead = d.get("lead")
    if lead:
        box = _textbox(slide, Inches(0.9), Inches(1.20), Inches(11.5), Inches(0.5))
        box.paragraphs[0].alignment = PP_ALIGN.CENTER
        _code_runs(box.paragraphs[0], lead, 15, MUTED)

    path = PLOTS / d["path"]
    with Image.open(path) as img:
        aspect = img.width / img.height

    top = Inches(2.0) if lead else Inches(1.55)
    avail_h = Inches(4.3) if lead else Inches(4.75)
    avail_w = Inches(11.4)
    height = avail_h
    width = Emu(int(height * aspect))
    if width > avail_w:
        width = avail_w
        height = Emu(int(width / aspect))

    slide.shapes.add_picture(
        str(path),
        Emu(int((SLIDE_W - width) / 2)),
        top,
        width=width, height=height,
    )

    if d.get("caption"):
        cap = _textbox(slide, Inches(1.45), Inches(6.55), Inches(10.4), Inches(0.7))
        cap.paragraphs[0].alignment = PP_ALIGN.CENTER
        _code_runs(cap.paragraphs[0], d["caption"], 16, MUTED)
    if d.get("note"):
        caption = bool(d.get("caption"))
        _note_line(slide, d["note"], dark=False,
                   top=Inches(6.95) if caption else None, center=caption)
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

    if d.get("body"):
        top = table_top + 0.62 * (len(rows) + 1) + 0.38
        box = _textbox(slide, Inches(1.65), Inches(top), Inches(10.0), Inches(1.9))
        for i, line in enumerate(d["body"]):
            para = box.paragraphs[0] if i == 0 else box.add_paragraph()
            para.space_after = Pt(8)
            _code_runs(para, line, 18, INK)

    if d.get("footnote"):
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



# Standing material for the notes file, appended after the per-slide notes. This is
# position rather than delivery: it answers questions that are not about any one slide.
APPENDIX = """\
## Appendix: should UBI standardize the vector?

Expect this from the room, given the `ubi_queries` slide. The position:

**File the spec bug now, separately.** `schema/1.3.0/query.request.schema.json` lists
`user_query` in `required`, while the field's own `$comment` says it is "currently not
required to support recommendation systems etc that might not have a user generated
query". Both statements are in 1.2.0 and 1.3.0. That needs an issue, not an RFC, and it
blocks any privacy-preserving use of the schema.

**Not yet for a top-level vector field.** A bare `query_vector` is not self-describing. A
consumer also needs the embedding model, the PCA basis (the notebook persists
`wands_pca.npz` for exactly this reason, and without it the coordinates mean nothing
across deployments), the sensitivity, and the epsilon. Several shapes are also unsettled:
one epsilon or per-coordinate budgets, fixed or per-deployment dimensionality, whether
`ubi_events` gets a parallel treatment. A top-level field has to answer those.
`query_attributes` lets us defer them, which is what it is for.

**The argument that eventually wins is semantic.** A privatized query is not a query
modifier, it is a substitute for `user_query`. It is primary content in a different
representation, and `query_attributes` is documented as filter choices, pagination and
experiment identifiers. Primary content in the metadata bag is fine for one
implementation and wrong once there are five.

**So: ship it under `query_attributes`, and put the standardization question to the
room.** This is an unusually good place to find the second and third implementers, and an
RFC with three interested parties goes very differently from one with a conference talk
behind it. If something is opened sooner, scope it to the envelope, a
`query_representation` object carrying mechanism, model, basis reference, epsilon and the
vector, rather than a bare vector field. The envelope is the part that has to be agreed
for anyone else's tooling to read the data.

## Appendix: implementing this in ubi.js

`ubi.js` does not build vectors, but it does not need changing either. It is a thin
serializer, and `query_attributes` is already a constructor argument
(`opensearch-project/user-behavior-insights`, `ubi-javascript-collector/ubi.js`):

```js
const q = new UbiQueryRequest(app, clientId, queryId,
  "",                                   // user_query emptied
  "product_id",
  { noised_query_vector: v, epsilon: 1.0 });
await ubiClient.trackQuery(q);
```

The work is a pre-step that produces `v`: embed the query, L2-normalize, project through
the PCA basis, add Laplace noise. The basis ships to the client too, about 30 KB as
float32 for 20 x 384. It is public, not a secret.

**Embedding in the browser, two options.** `transformers.js` runs `all-MiniLM-L6-v2` as
ONNX over WASM or WebGPU, which puts the queries in the same space as the product index,
at the cost of roughly 23 MB quantized on first load. Or skip the model entirely and hash
character n-grams into a fixed-width vector, applying the same scheme to products
server-side. That loses synonym matching but needs no download, and for segment-level
intent it may be enough.

**Never sample the noise with `Math.random()`.** V8 implements it as xorshift128+, and the
internal state is recoverable from a handful of outputs. An attacker who predicts the
stream subtracts the noise exactly and recovers the raw vector, which does not weaken the
guarantee, it voids it. Use `crypto.getRandomValues()`, then inverse-CDF with
`u ~ Uniform(-0.5, 0.5)`:

```js
const noise = -b * Math.sign(u) * Math.log(1 - 2 * Math.abs(u));
```

Reject `|u| === 0.5` or that returns `-Infinity`.

**Privatize on submit, never per keystroke.** Autocomplete firing on every character
spends the budget many times over on one intent, and the draws compose, so an attacker
who averages them recovers the query. This is the practical face of the composition
question on the Questions slide.

## Appendix: why PCA, and what "coordinate spread" means

No slide mentions PCA, which is deliberate, but it is not optional in the mechanism and it
is the first thing an implementer will trip over.

**Why reduce dimensions at all.** The encoder emits 384. Laplace noise is added to every
coordinate independently, so the norm of the noise vector grows as the square root of the
dimension while the signal does not. Going from 384 to 20 cuts the noise norm by about
4.4x at the same epsilon, which is the difference between a usable mechanism and one that
destroys everything. The price is variance: the notebook keeps 41.9% of it at 20
components.

**The basis has to be fixed and shared.** PCA is fit once on the index vectors and the
same basis is applied to queries, which is why `download_wands.py` persists
`wands_pca.npz`. Refit it and every stored vector becomes meaningless, because they no
longer live in the same space.

**What "coordinate spread" means on the limitations slide.** It is the mean per-coordinate
standard deviation of the index vectors, `wands_vectors.std(axis=0).mean()`, which is
0.128 for the 20-dimension WANDS basis. Epsilon only means something relative to that
number. A different corpus, or the same corpus at a different number of components, gives
a different spread and therefore a different usable epsilon. That is the whole content of
"epsilon does not transfer between indexes", and it is also why the toy index needed
epsilon 1.2 while the real one is discussed at 1 to 20.
"""


def _markdown_notes():
    """
    Render the speaker notes as markdown, for presenting from the PDF.

    Generated rather than written by hand so it cannot drift from SLIDES, which
    stays the single source of truth for both the deck and the notes.
    """
    out = [
        "# Speaker notes",
        "",
        "Generated by `build_slides.py`. Do not edit by hand: the notes live in the",
        "`SLIDES` list in that file, and this is rewritten on every build.",
        "",
    ]

    for number, (kind, d, notes) in enumerate(SLIDES, start=1):
        if kind == "statement":
            heading = d["text"].replace("\n", " ")
        elif kind == "section":
            heading = f'{d["eyebrow"]}. {d["title"]}'
        else:
            heading = d.get("title", "")

        out += ["---", "", f"## {number}. {heading}", ""]

        if kind == "title" and d.get("subtitle"):
            out += [f'*{d["subtitle"]}*', ""]
        if d.get("lead"):
            out += [f'*{d["lead"]}*', ""]

        for text in d.get("bullets", []) or d.get("lines", []):
            out.append(f"- {text}")
        if d.get("bullets") or d.get("lines"):
            out.append("")

        if d.get("columns"):
            out.append("| " + " | ".join(d["columns"]) + " |")
            out.append("|" + "---|" * len(d["columns"]))
            for row in d["rows"]:
                out.append("| " + " | ".join(row) + " |")
            out.append("")

        for line in d.get("body", []):
            out += [line, ""]

        if d.get("path"):
            out += [f'![{d.get("caption", "")}](plots/{d["path"]})', ""]
        elif d.get("image"):
            out += [f'![]({"plots/" + d["image"]["path"]})', ""]

        for key in ("caption", "footnote"):
            if d.get(key):
                out += [f'*{d[key]}*', ""]
        if d.get("link"):
            out += [f'{d["link"].get("lead", "")} <{d["link"]["url"]}>'.strip(), ""]
        if d.get("note"):
            note = d["note"]
            url = f' <{note["url"]}>' if note.get("url") else ""
            out += [f'{note["lead"]}{url}', ""]

        out += [notes, ""]

    out += ["---", "", APPENDIX]
    return "\n".join(out).rstrip() + "\n"


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    for number, (kind, payload, notes) in enumerate(SLIDES, start=1):
        slide = RENDERERS[kind](prs, payload)
        _notes(slide, notes)
        if number > 1:  # the opening title slide stays clean
            _slide_number(slide, number, kind in DARK_KINDS)

    _retheme_links(prs)
    prs.save(OUTPUT)
    NOTES_OUTPUT.write_text(_markdown_notes())
    print(f"wrote {OUTPUT.name}: {len(SLIDES)} slides")
    print(f"wrote {NOTES_OUTPUT.name}")
    counts = {}
    for kind, _, _ in SLIDES:
        counts[kind] = counts.get(kind, 0) + 1
    print("  " + ", ".join(f"{k} x{v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    build()
