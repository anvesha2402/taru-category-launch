"""
AI5 - Cooperative content agents for TARU.

Pipeline for each content request:
    brief agent -> copywriter -> checks (rules + AI4 guardrail as a tool) -> revise (max 2) -> brand-voice critic -> approval queue

Autonomy level 2: the agents draft; a person approves every public line. Nothing here publishes anything.
The LLM is any callable llm(system, user) -> (text, input_tokens, output_tokens), e.g. ai.guardrail.make_llm(...).
"""
from __future__ import annotations

import csv
import json
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
BRAND_VOICE = REPO / "ai" / "content" / "brand_voice.md"
CLAIMS_MATRIX = REPO / "compliance" / "claims_matrix.csv"
REQUESTS = REPO / "ai" / "eval" / "content_requests.csv"
QUEUE = REPO / "ai" / "eval" / "content_approval_queue_v2.csv"
MAX_REVISIONS = 2
PIPELINE_VERSION = "v2"   # v1 = run of 2 Oct 2026 (2/21 passed); v2 changes listed in DL-18

LENGTH = {"social_post": "40 to 80 words", "product_description": "80 to 130 words",
          "email": "a subject line, then 120 to 180 words of body"}

# Approved examples given to the copywriter: lines from the brand book (section 2.3). "with a soft finish" is dropped
# from the product-page example because comfort words need an approved claim (none yet).
APPROVED_EXAMPLES = [
    "What does 'certified organic' actually certify? One post, four steps, no jargon.",
    "Mid-weight linen. Cut 4 cm fuller through the waist than our standard block, with extra seam allowance for alterations.",
    "Chosen with care. The proof is inside the box, if he wants it.",
]

# --------------------------------------------------------------------------
# Approved claims (D7)
# --------------------------------------------------------------------------

def approved_claims(path: Path = CLAIMS_MATRIX) -> list[dict]:
    """Claims the agents may use: D7 decision 'Use' or 'Conditional' (placeholders stay in square brackets)."""
    out = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            dec = r["decision"].strip().lower()
            if dec.startswith("use") or dec.startswith("conditional"):
                if "ai" in r["claim_type"].lower():      # the AI-image label is for images, not copy
                    continue
                out.append({"id": r["claim_id"], "wording": r["claim_wording"], "decision": r["decision"]})
    return out

# --------------------------------------------------------------------------
# Deterministic checks (no model): brand rules the brief bans outright
# --------------------------------------------------------------------------

COMPETITORS = ["manyavar", "mohey", "tasva", "fabindia", "sojanya", "isha life", "jaypore", "kisah", "myntra", "ajio"]
AVOID_WORDS = ["eco", "green", "sustainable", "sustainably", "natural", "naturally", "conscious", "guilt-free", "clean",
               "pure", "luxury", "luxurious", "premium", "exclusive", "curated", "timeless", "iconic", "heritage-inspired",
               "transparent", "perfect", "perfectly", "comfortable", "comfort", "soft", "softness", "breathable"]
SCARCITY = r"\b(only \d+ left|limited (stock|edition|time)|hurry|last chance|selling fast|while stocks last|don't miss out)\b"
TESTIMONIAL = r"(\bcustomers? (say|love)|\bloved by\b|\b\d[\d,]* (happy )?customers\b|★|\breview(s|ed)? (say|call)|\"[^\"]{10,}\"\s*[-–—]\s*[A-Z][a-z]+)"
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF]")


# What to do instead of each avoid-list word (from the brand book word bank), used in revision feedback
REPLACEMENT = {
    "perfect": "drop it and state the specific fact (the size range, the alteration window)",
    "perfectly": "drop it and state the specific fact",
    "comfort": "drop it: no comfort claim is approved yet (needs a wear trial)",
    "comfortable": "drop it: no comfort claim is approved yet (needs a wear trial)",
    "soft": "drop it: no softness claim is approved yet", "softness": "drop it: no softness claim is approved yet",
    "breathable": "drop it: not approved", "premium": "drop it; give the fabric or the price instead",
    "luxury": "drop it; give the fabric or the price instead", "luxurious": "drop it; give the fabric instead",
    "exclusive": "drop it", "curated": "use 'chosen' or drop it", "timeless": "use 'made to be handed down'",
    "iconic": "drop it", "heritage-inspired": "drop it; name the craft or place instead",
    "transparent": "use 'see for yourself' or 'scan to check'", "sustainable": "use the approved certification wording, or drop it",
    "sustainably": "use the approved certification wording, or drop it", "eco": "use the approved certification wording, or drop it",
    "green": "drop it (as a colour, use 'sage' or 'bottle')", "natural": "name the fibre (cotton, linen) instead",
    "naturally": "drop it", "conscious": "drop it", "guilt-free": "drop it", "clean": "drop it", "pure": "drop it",
}


def normalise_format(text: str) -> tuple[str, list[str]]:
    """Mechanical copy-editing the brand rules require: no exclamation marks, emojis or hashtags.
    These carry no meaning, so code fixes them instead of spending a revision on them."""
    fixes = []
    if "!" in text:
        text = re.sub(r"!+", ".", text); fixes.append("exclamation marks -> full stops")
    if EMOJI.search(text):
        text = EMOJI.sub("", text); fixes.append("emojis removed")
    if re.search(r"(^|\s)#\w", text):
        text = re.sub(r"(?m)^\s*(#\w+\s*)+$", "", text)            # lines made only of hashtags
        text = re.sub(r"(^|\s)#(\w+)", r"\1\2", text)            # inline #TARU -> TARU
        fixes.append("hashtags removed")
    text = re.sub(r"\.\.+", ".", text)
    text = re.sub(r"[ \t]+", " ", re.sub(r"\n{3,}", "\n\n", text)).strip()
    return text, fixes


def _norm(s: str) -> str:
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[\s.]+$", "", re.sub(r"\s+", " ", s)).strip()


def is_approved_sentence(sentence: str, claims: list[dict]) -> bool:
    """True if the sentence is, word for word, an approved D7 claim (or one sentence of one)."""
    n = _norm(sentence)
    for c in claims:
        if n == _norm(c["wording"]) or n in {_norm(x) for x in split_sentences(c["wording"])}:
            return True
    return False


def rule_violations(text: str) -> list[str]:
    t = text.lower()
    v = []
    if "!" in text:
        v.append("exclamation mark")
    if EMOJI.search(text):
        v.append("emoji")
    if re.search(r"(^|\s)#\w", text):
        v.append("hashtag in body copy")
    for c in COMPETITORS:
        if re.search(rf"\b{re.escape(c)}\b", t):
            v.append(f"competitor name: {c}")
    for w in AVOID_WORDS:
        if re.search(rf"\b{re.escape(w)}\b", t):
            v.append(f"avoid-list word: {w}")
    if re.search(SCARCITY, t):
        v.append("fake scarcity")
    if re.search(TESTIMONIAL, text, re.I):
        v.append("testimonial or review")
    if re.search(r"\b(slimming|hides? (the )?(belly|tummy))\b", t):
        v.append("body shaming")
    return v

# --------------------------------------------------------------------------
# Claim sentences sent to the guardrail
# --------------------------------------------------------------------------

CLAIM_TRIGGER = re.compile(
    r"organic|certif|gots|licen[cs]e|recycl|fibre|fiber|cotton|linen|grown|woven|trail|proof|planet|earth|"
    r"chemical|toxic|carbon|water|%|percent|first|only|best|guarantee|ai\b|generated|scan|qr|alteration|mark(ed)? down",
    re.I)


def split_sentences(text: str) -> list[str]:
    # split only where the next sentence starts with a capital or a quote, so "licence no. [X]" stays whole
    parts = re.split(r"(?<=[.?])\s+(?=[A-Z\"'‘“])|\n+", text.strip())
    return [p.strip(" -•") for p in parts if len(p.strip(" -•")) > 3]


def claim_sentences(text: str) -> list[str]:
    return [s for s in split_sentences(text) if CLAIM_TRIGGER.search(s)]

# --------------------------------------------------------------------------
# Agents
# --------------------------------------------------------------------------

def _json(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("no JSON object")
    return json.loads(m.group(0))


BRIEF_SYSTEM = """You are the brief agent for TARU, a fictional certified-organic men's ethnic wear brand. Turn a content request into a short structured brief.
Use only the approved claims listed; copy their wording exactly, keeping any [placeholders]. Do not invent facts, numbers, certificates, customers or reviews.
Return one JSON object with keys: objective, audience, occasion, key_message, approved_claim_ids (list of ids), facts_to_use (list of short strings taken from the request), call_to_action."""

WRITER_SYSTEM = """You are the copywriter for TARU, a fictional certified-organic men's ethnic wear brand. Write in the brand voice below.
Hard rules:
- Use only facts from the brief and wording from the approved claims. Keep [placeholders] such as [X] or [certification body] exactly as written; never fill them in.
- No testimonials, reviews, customer numbers, scarcity, celebrities or competitor names.
- No exclamation marks, emojis or hashtags.
- Output only the finished copy, nothing else.

BRAND VOICE
{voice}"""

CRITIC_SYSTEM = """You are the brand-voice critic for TARU. Score the draft against the brand voice below on four criteria, each 1 to 5:
clarity (easy to read, one idea per sentence), voice (assured, warm, precise, understated; uses the word bank), claim_accuracy (only approved claims, placeholders kept, nothing overstated), call_to_action (ends with something useful to the reader).
Then give overall (1 to 5): 5 = publish as is, 4 = minor edits, 3 = needs rework, 2 = off-brand, 1 = unusable.
Be strict: give 5 only if you would publish it unchanged. Any avoid-list word, unapproved claim, superlative or exclamation mark caps overall at 3.
Return one JSON object: {{"clarity": n, "voice": n, "claim_accuracy": n, "call_to_action": n, "overall": n, "note": "<one sentence>"}}

BRAND VOICE
{voice}"""


@dataclass
class Output:
    request_id: str
    content_type: str
    brief: dict = field(default_factory=dict)
    drafts: list[str] = field(default_factory=list)
    final_text: str = ""
    revisions: int = 0
    passed: bool = False
    rule_issues: list[str] = field(default_factory=list)
    format_fixes: list[str] = field(default_factory=list)
    guardrail_issues: list[dict] = field(default_factory=list)
    critic: dict = field(default_factory=dict)
    max_similarity: float = 0.0
    seconds: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0


class ContentTeam:
    def __init__(self, llm: Callable, guardrail=None, voice: str | None = None, claims: list[dict] | None = None,
                 critic_llm: Callable | None = None, embedder=None, competitor_texts: list[str] | None = None):
        self.llm, self.critic_llm = llm, critic_llm or llm
        self.guardrail = guardrail                    # ai.guardrail.Guardrail, or None to skip
        self.voice = voice if voice is not None else BRAND_VOICE.read_text(encoding="utf-8")
        self.claims = claims if claims is not None else approved_claims()
        self.embedder, self.competitor_texts = embedder, competitor_texts or []
        self._comp_vecs = embedder.encode(self.competitor_texts, normalize_embeddings=True) if (embedder and self.competitor_texts) else None
        self.tin = self.tout = 0

    def _call(self, llm, system, user):
        text, a, b = llm(system, user)
        self.tin += a; self.tout += b
        return text

    def _claims_text(self):
        return "\n".join(f"{c['id']}: {c['wording']}" for c in self.claims)

    # 1. brief
    def brief(self, req: dict) -> dict:
        user = (f"APPROVED CLAIMS\n{self._claims_text()}\n\nREQUEST\ntype: {req['content_type']}\nchannel: {req['channel']}\n"
                f"segment: {req['segment']}\noccasion: {req['occasion']}\nline: {req['product_line']}\nrequest: {req['request']}")
        try:
            return _json(self._call(self.llm, BRIEF_SYSTEM, user))
        except Exception:
            return {"objective": req["request"], "audience": req["segment"], "occasion": req["occasion"],
                    "key_message": req["request"], "approved_claim_ids": [], "facts_to_use": [req["request"]],
                    "call_to_action": "", "_note": "brief agent output unparseable; request used as brief"}

    # 2. copywriter
    def write(self, req: dict, brief: dict, feedback: list[str] | None = None, previous: str = "") -> str:
        ids = set(brief.get("approved_claim_ids") or [])
        claims = [c for c in self.claims if c["id"] in ids] or self.claims
        user = (f"CONTENT TYPE: {req['content_type']} for {req['channel']} ({LENGTH[req['content_type']]})\n"
                f"BRIEF\n{json.dumps(brief, ensure_ascii=False, indent=1)}\n\n"
                "APPROVED CLAIMS (wording to copy exactly)\n" + "\n".join(f"- {c['wording']}" for c in claims) + "\n\n"
                "APPROVED EXAMPLES OF THE VOICE\n" + "\n".join(f"- {e}" for e in APPROVED_EXAMPLES))
        if feedback:
            user += ("\n\nYOUR PREVIOUS DRAFT\n" + previous + "\n\nFIX THESE PROBLEMS, change nothing else that works:\n"
                     + "\n".join(f"- {f}" for f in feedback))
        user += ("\n\nBEFORE YOU ANSWER, CHECK: no exclamation marks; no hashtags; none of these words: "
                 + ", ".join(AVOID_WORDS) + "; claims copied exactly from the approved list; [placeholders] kept.")
        return self._call(self.llm, WRITER_SYSTEM.format(voice=self.voice), user).strip()

    # 3. checks
    def check(self, text: str) -> tuple[list[str], list[dict]]:
        rules = rule_violations(text)
        flagged = []
        if self.guardrail is not None:
            for s in claim_sentences(text):
                if is_approved_sentence(s, self.claims):     # human-approved in D7: not re-screened
                    continue
                r = self.guardrail.check(s, "TARU marketing copy (AI5 draft)")
                if r.flagged:
                    flagged.append({"sentence": s, "verdict": r.verdict, "status": r.status,
                                    "clause": f"{r.doc_id} {r.clause_id}".strip(), "reason": r.reason,
                                    "rewrite": r.compliant_rewrite})
        return rules, flagged

    @staticmethod
    def feedback(rules: list[str], flagged: list[dict]) -> list[str]:
        fb = []
        for v in rules:
            if v.startswith("avoid-list word: "):
                w = v.split(": ", 1)[1]
                fb.append(f'Do not use the word "{w}": {REPLACEMENT.get(w, "drop it")}.')
            else:
                fb.append(f"Remove: {v}")
        for f in flagged:
            if f["status"] == "blocked_unverified_citation":
                fb.append(f'Sentence "{f["sentence"]}" could not be verified against the rules. Use approved claim wording or remove it.')
            else:
                fb.append(f'Sentence "{f["sentence"]}" was judged {f["verdict"]}: {f["reason"]} '
                          f'Rewrite using approved claim wording or remove it.')
        return fb

    # 4. critic
    def critique(self, text: str) -> dict:
        try:
            d = _json(self._call(self.critic_llm, CRITIC_SYSTEM.format(voice=self.voice), f"DRAFT\n{text}"))
            for k in ("clarity", "voice", "claim_accuracy", "call_to_action", "overall"):
                d[k] = int(d[k])
            return d
        except Exception as e:
            return {"error": str(e)[:120]}

    def similarity(self, text: str) -> float:
        if self._comp_vecs is None:
            return 0.0
        v = self.embedder.encode([text], normalize_embeddings=True)[0]
        return float((self._comp_vecs @ v).max())

    def run(self, req: dict) -> Output:
        t0, tin0, tout0 = time.time(), self.tin, self.tout
        out = Output(req["request_id"], req["content_type"])
        out.brief = self.brief(req)
        text, fixes = normalise_format(self.write(req, out.brief))
        out.drafts.append(text); out.format_fixes += fixes
        rules, flagged = self.check(text)
        while (rules or flagged) and out.revisions < MAX_REVISIONS:
            out.revisions += 1
            text, fixes = normalise_format(self.write(req, out.brief, self.feedback(rules, flagged), previous=text))
            out.drafts.append(text); out.format_fixes += fixes
            rules, flagged = self.check(text)
        out.final_text, out.rule_issues, out.guardrail_issues = text, rules, flagged
        out.passed = not rules and not flagged
        out.critic = self.critique(text)
        out.max_similarity = self.similarity(text)
        out.seconds, out.tokens_in, out.tokens_out = time.time() - t0, self.tin - tin0, self.tout - tout0
        return out

# --------------------------------------------------------------------------
# Approval queue and evaluation
# --------------------------------------------------------------------------

QUEUE_COLUMNS = ["request_id", "content_type", "final_text", "passed_checks", "revisions", "open_issues", "format_fixes",
                 "critic_overall", "critic_clarity", "critic_voice", "critic_claim_accuracy", "critic_cta", "critic_note",
                 "max_similarity_to_competitor", "seconds",
                 "your_voice_score", "your_decision", "your_edit"]


def save_queue(outputs: list[Output], path: Path = QUEUE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(QUEUE_COLUMNS)
        for o in outputs:
            c = o.critic
            issues = o.rule_issues + [f'{g["sentence"]} -> {g["verdict"]}/{g["status"]}' for g in o.guardrail_issues]
            w.writerow([o.request_id, o.content_type, o.final_text, o.passed, o.revisions, " | ".join(issues),
                        "; ".join(sorted(set(o.format_fixes))),
                        c.get("overall", ""), c.get("clarity", ""), c.get("voice", ""), c.get("claim_accuracy", ""),
                        c.get("call_to_action", ""), c.get("note", c.get("error", "")),
                        round(o.max_similarity, 3), round(o.seconds, 1), "", "", ""])


def save_trace(outputs: list[Output], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for o in outputs:
            f.write(json.dumps(asdict(o), ensure_ascii=False) + "\n")


def evaluate(queue_rows: list[dict]) -> dict:
    """Pass tests from the brief. Human scores come from your_voice_score (1-5), filled in by the author."""
    n = len(queue_rows)
    passed = sum(str(r["passed_checks"]).strip().lower() == "true" for r in queue_rows)
    m = {"n": n, "passed_checks": passed, "pass_rate": passed / n if n else float("nan"),
         "pass_test_guardrail_0.9": n > 0 and passed / n >= 0.9,
         "revisions_mean": sum(int(r["revisions"]) for r in queue_rows) / n if n else float("nan")}
    pairs = [(int(float(r["your_voice_score"])), int(float(r["critic_overall"]))) for r in queue_rows
             if str(r.get("your_voice_score", "")).strip() and str(r.get("critic_overall", "")).strip()]
    human = [int(float(r["your_voice_score"])) for r in queue_rows if str(r.get("your_voice_score", "")).strip()]
    m["human_scored"] = len(human)
    if human:
        m["share_human_score_ge4"] = sum(h >= 4 for h in human) / len(human)
        m["pass_test_voice_80pct"] = m["share_human_score_ge4"] >= 0.8
    if pairs:
        m["judge_exact_agreement"] = sum(a == b for a, b in pairs) / len(pairs)
        m["judge_within_1"] = sum(abs(a - b) <= 1 for a, b in pairs) / len(pairs)
        try:
            from sklearn.metrics import cohen_kappa_score
            m["judge_weighted_kappa"] = cohen_kappa_score([a for a, _ in pairs], [b for _, b in pairs],
                                                          weights="quadratic", labels=[1, 2, 3, 4, 5])
        except Exception:
            pass
        m["judge_mean_minus_human_mean"] = sum(b - a for a, b in pairs) / len(pairs)
    return m
