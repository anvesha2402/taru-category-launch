"""
TARU Claims Guardrail (AI4)
===========================

Retrieval-augmented checker for marketing claims against Indian greenwashing,
advertising and labelling rules plus the GOTS standard.

Pipeline for one claim:
    keyword rules  →  hybrid retrieval (BM25 + embeddings, fused with RRF)
    →  cross-encoder rerank  →  LLM verdict as fixed JSON
    →  verbatim-quote verification (blocks any invented or altered clause)
    →  log the call

Autonomy level 2: the guardrail recommends; a person decides (brief 6A.3).

Heavy dependencies (sentence-transformers, chromadb, LLM SDKs) are imported
lazily, so the chunker, BM25, verification and evaluation run without them.
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[1]
KB_RAW = REPO / "ai" / "kb" / "raw"
KB_CHUNKS = REPO / "ai" / "kb" / "chunks.jsonl"
KB_MANUAL = REPO / "ai" / "kb" / "manual_chunks.jsonl"
PROMPT_FILE = REPO / "ai" / "prompts" / "guardrail_v1.txt"
LOG_FILE = REPO / "ai" / "logs" / "calls.csv"

# One entry per source document. Save each file in ai/kb/raw/ under this name.
DOCS = {
    "CCPA": {"file": "ccpa_greenwashing_guidelines_2024.txt",  # OCR of the scanned gazette PDF (tesseract)
             "title": "CCPA Guidelines for Prevention and Regulation of Greenwashing or Misleading Environmental Claims, 2024"},
    "ASCI-GREEN": {"file": "asci_environmental_green_claims_2024.pdf",
                   "title": "ASCI Guidelines for Advertisements Making Environmental/Green Claims, 2024"},
    "ASCI-AI": {"file": "asci_ai_labelling_2026_final.pdf",
                "title": "ASCI Guidelines for Responsible Labelling of Synthetically Generated Content in Advertising, 2026"},
    "LM-PCR": {"file": "legal_metrology_packaged_commodities_rules.pdf",
               "title": "Legal Metrology (Packaged Commodities) Amendment Rules, 13 Feb 2026 (country-of-origin filter on e-commerce)"},
    "TC-DRAFT": {"file": "textiles_committee_draft_labelling_2026.pdf",
                 "title": "Textiles Committee draft labelling regulations, March 2026 (draft, not in force)"},
    "GOTS": {"file": "gots_standard.pdf",
             "title": "Global Organic Textile Standard (current version)"},
    "GOTS-LABEL": {"file": "gots_label_grades.txt",
                   "title": "GOTS label grades (web page saved as text)"},
    "ITR-2026": {"file": "it_amendment_rules_2026.pdf",
                 "title": "Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Amendment Rules, 2026"},
}

EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TOP_K_EACH = 20        # candidates from BM25 and from embeddings
TOP_K_FINAL = 5        # clauses shown to the LLM
RRF_K = 60
MAX_CHUNK_CHARS = 1500
MIN_QUOTE_CHARS = 20

# --------------------------------------------------------------------------
# 1. Loading and clause chunking
# --------------------------------------------------------------------------

# A clause heading: "5.", "5)", "4.2", "4.2.1" at the start of a line.
# Single numbers need "." or ")" so dates like "15 October" are not headings.
HEADING = re.compile(r"^\s*(?:Clause|Rule|Section|Para(?:graph)?)?\s*(\d{1,2}(?:\.\d{1,2}){1,3}|\d{1,2}[.)])\s+(?=\S)")
SUBCLAUSE = re.compile(r"^\s*\(((?:\d{1,2})|(?:[a-z]{1,2})|(?:[ivx]{1,5}))\)\s+")
PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?\d{1,3}(?:\s*(?:of|/)\s*\d{1,3})?\s*$", re.I)


@dataclass
class Chunk:
    doc_id: str
    clause_id: str
    text: str
    page: int
    title: str = ""

    @property
    def key(self) -> str:
        return f"{self.doc_id} {self.clause_id}"


def read_document(path: Path) -> list[tuple[int, str]]:
    """Return [(page_number, line)] for a PDF or text file."""
    lines: list[tuple[int, str]] = []
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        for p, page in enumerate(PdfReader(str(path)).pages, 1):
            for line in (page.extract_text() or "").splitlines():
                lines.append((p, line))
    else:
        for line in path.read_text(encoding="utf-8").splitlines():
            lines.append((1, line))
    return [(p, re.sub(r"[ \t]+", " ", l).rstrip()) for p, l in lines
            if l.strip() and not PAGE_NUMBER.match(l)]


def chunk_document(doc_id: str, lines: list[tuple[int, str]], title: str = "",
                   heading: re.Pattern = HEADING) -> list[Chunk]:
    """Split a document into clause chunks, keeping the clause number."""
    chunks: list[Chunk] = []
    cur_id, cur_page, buf = "preamble", lines[0][0] if lines else 1, []

    def flush():
        text = " ".join(buf).strip()
        if text:
            chunks.extend(_split_long(doc_id, cur_id.rstrip(".)"), text, cur_page, title))

    for page, line in lines:
        m = heading.match(line)
        if m:
            flush()
            cur_id, cur_page, buf = m.group(1), page, [line.strip()]
        else:
            buf.append(line.strip())
    flush()
    return chunks


def _split_long(doc_id, clause_id, text, page, title) -> list[Chunk]:
    """Split an over-long clause at its sub-clause markers: 5 → 5(1), 5(2)…"""
    if len(text) <= MAX_CHUNK_CHARS:
        return [Chunk(doc_id, clause_id, text, page, title)]
    # split at numbered sub-clauses only; lettered items stay inside their parent
    parts = re.split(r"(?=\s\(\d{1,2}\)\s)", text)
    out, head = [], parts[0].strip()
    for part in parts[1:]:
        m = re.match(r"\s\(([^)]+)\)\s", part)
        sub = m.group(1) if m else str(len(out) + 1)
        out.append(Chunk(doc_id, f"{clause_id}({sub})", (head + " … " + part.strip()) if head and len(head) < 300 else part.strip(), page, title))
    return out or [Chunk(doc_id, clause_id, text, page, title)]


def build_chunks(kb_raw: Path = KB_RAW, docs: dict = DOCS) -> tuple[list[Chunk], dict]:
    """Chunk every available document. Manual chunks override a document entirely."""
    manual: dict[str, list[Chunk]] = {}
    if KB_MANUAL.exists():
        for line in KB_MANUAL.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                manual.setdefault(d["doc_id"], []).append(Chunk(**d))
    chunks, report = [], {}
    for doc_id, meta in docs.items():
        if doc_id in manual:
            chunks += manual[doc_id]
            report[doc_id] = {"status": "manual", "chunks": len(manual[doc_id])}
            continue
        path = kb_raw / meta["file"]
        if not path.exists():
            report[doc_id] = {"status": "MISSING", "file": meta["file"]}
            continue
        doc_chunks = chunk_document(doc_id, read_document(path), meta["title"])
        # documents that restart numbering (annexures, schedules) would repeat clause ids;
        # later repeats become e.g. "2 [part 2]" so every citation points at exactly one chunk
        seen: dict[str, int] = {}
        for c in doc_chunks:
            n = seen.get(c.clause_id, 0) + 1; seen[c.clause_id] = n
            if n > 1:
                c.clause_id = f"{c.clause_id} [part {n}]"
        chunks += doc_chunks
        status = "ok" if len(doc_chunks) >= 5 else "CHECK: fewer than 5 clauses found"
        report[doc_id] = {"status": status, "chunks": len(doc_chunks)}
    return chunks, report


def save_chunks(chunks: list[Chunk], path: Path = KB_CHUNKS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


def load_chunks(path: Path = KB_CHUNKS) -> list[Chunk]:
    return [Chunk(**json.loads(l)) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

# --------------------------------------------------------------------------
# 2. Hybrid retrieval
# --------------------------------------------------------------------------

def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9%]+", text.lower())


class Retriever:
    """BM25 + embeddings (chromadb), fused with reciprocal rank fusion, then reranked.

    use_embeddings / use_reranker can be switched off to run on a machine
    without the models (the offline tests do this).
    """

    def __init__(self, chunks: list[Chunk], use_embeddings: bool = True, use_reranker: bool = True):
        from rank_bm25 import BM25Okapi
        self.chunks = chunks
        self.bm25 = BM25Okapi([_tokens(c.text) for c in chunks])
        self.collection = None
        self.reranker = None
        if use_embeddings:
            import chromadb
            from chromadb.utils import embedding_functions
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
            client = chromadb.Client()
            self.collection = client.get_or_create_collection("taru_kb", embedding_function=ef,
                                                              metadata={"hnsw:space": "cosine"})
            if self.collection.count() == 0:
                self.collection.add(ids=[str(i) for i in range(len(chunks))],
                                    documents=[c.text for c in chunks],
                                    metadatas=[{"doc_id": c.doc_id, "clause_id": c.clause_id} for c in chunks])
        if use_reranker:
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder(RERANK_MODEL)

    def search(self, query: str, k: int = TOP_K_FINAL) -> list[tuple[Chunk, float]]:
        bm = self.bm25.get_scores(_tokens(query))
        bm_rank = sorted(range(len(self.chunks)), key=lambda i: -bm[i])[:TOP_K_EACH]
        ranked_lists = [bm_rank]
        if self.collection is not None:
            res = self.collection.query(query_texts=[query], n_results=min(TOP_K_EACH, len(self.chunks)))
            ranked_lists.append([int(i) for i in res["ids"][0]])
        fused: dict[int, float] = {}
        for lst in ranked_lists:
            for rank, idx in enumerate(lst):
                fused[idx] = fused.get(idx, 0.0) + 1.0 / (RRF_K + rank + 1)
        cand = sorted(fused, key=lambda i: -fused[i])[:TOP_K_EACH]
        if self.reranker is not None and cand:
            scores = self.reranker.predict([(query, self.chunks[i].text) for i in cand])
            order = sorted(zip(cand, scores), key=lambda t: -t[1])
        else:
            order = [(i, fused[i]) for i in cand]
        return [(self.chunks[i], float(s)) for i, s in order[:k]]

# --------------------------------------------------------------------------
# 3. Keyword rules (can only raise risk, never lower it)
# --------------------------------------------------------------------------

RULES = [
    ("generic_green_term", "high", r"\b(eco[\s-]?friendly|eco[\s-]?conscious|green|sustainabl[ey]|planet[\s-]?friendly|earth[\s-]?friendly|environment[\s-]?friendly|good for the planet)\b"),
    ("natural_unqualified", "medium", r"\b(natural|nature|pure)\b"),
    ("absolute_claim", "high", r"\b(chemical[\s-]?free|toxin[\s-]?free|non[\s-]?toxic|zero[\s-]?(impact|waste|emissions?)|100\s*%\s*(sustainable|natural|organic|eco)|carbon[\s-]?neutral|climate[\s-]?positive|biodegradable)\b"),
    ("organic_on_processed_fibre", "high", r"\borganic\b.{0,20}\b(bamboo|viscose|lyocell|modal|rayon|tencel|polyester)\b|\b(bamboo|viscose|lyocell|modal|rayon|tencel)\b.{0,20}\borganic\b"),
    ("health_or_skin_claim", "high", r"\b(hypoallergenic|allerg|rash|eczema|dermatolog|skin[\s-]?safe|good for (your )?skin|healthier)\b"),
    ("comparative_superlative", "medium", r"\b(first|only|best|most|better than|no\.?\s*1|number one|india'?s (first|only))\b"),
    ("future_pledge", "medium", r"\bby\s+20\d\d\b|\b(pledge|committed to|on track to)\b"),
    ("testimonial_or_endorsement", "high", r"\b(customers? (say|love)|testimonial|rated \d|recommended by|doctor|dermatologist)\b"),
]
_RISK = {"low": 0, "medium": 1, "high": 2}


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[‐-―]", "-", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def keyword_rules(claim: str) -> list[dict]:
    t = _normalise(claim)
    # de-obfuscate "e-c-o" / "e.c.o" style spellings
    t2 = re.sub(r"(?<=\b[a-z])[\.\-_ ](?=[a-z]\b)", "", t)
    hits = []
    for name, risk, pat in RULES:
        if re.search(pat, t) or re.search(pat, t2):
            hits.append({"rule": name, "risk": risk})
    # certification named with no licence number or certifier anywhere in the claim
    if re.search(r"\b(gots|certified|certification)\b", t) and not re.search(
            r"\b(licen[cs]e|lic\.?\s*no|certified by|certification body)\b", t):
        hits.append({"rule": "certification_without_licence", "risk": "high"})
    return hits

# --------------------------------------------------------------------------
# 4. LLM call, JSON parsing and quote verification
# --------------------------------------------------------------------------

SCHEMA_KEYS = ["verdict", "risk_level", "doc_id", "clause_id", "clause_quote", "reason", "compliant_rewrite"]
VERDICTS = {"compliant", "non-compliant", "insufficient_basis"}


@dataclass
class Result:
    claim: str
    verdict: str
    risk_level: str
    doc_id: str = ""
    clause_id: str = ""
    clause_quote: str = ""
    reason: str = ""
    compliant_rewrite: str = ""
    quote_verified: bool = False
    status: str = ""                 # ok | blocked_unverified_citation | parse_error | error
    rule_hits: list = field(default_factory=list)
    retrieved: list = field(default_factory=list)
    latency_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def flagged(self) -> bool:
        """True if the claim goes to a human as risky or unverifiable."""
        return self.verdict != "compliant" or self.status != "ok"


def load_prompt(path: Path = PROMPT_FILE) -> str:
    return path.read_text(encoding="utf-8")


def format_context(hits: list[tuple[Chunk, float]]) -> str:
    return "\n\n".join(f'<clause doc_id="{c.doc_id}" clause_id="{c.clause_id}">\n{c.text}\n</clause>' for c, _ in hits)


def parse_json(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    d = json.loads(m.group(0))
    missing = [k for k in SCHEMA_KEYS if k not in d]
    if missing:
        raise ValueError(f"missing keys: {missing}")
    if d["verdict"] not in VERDICTS or d["risk_level"] not in _RISK:
        raise ValueError(f"bad verdict or risk: {d['verdict']}, {d['risk_level']}")
    return d


def verify_quote(d: dict, hits: list[tuple[Chunk, float]]) -> bool:
    """The quote must appear word for word in the retrieved chunk with the cited IDs."""
    quote = _normalise(d.get("clause_quote", ""))
    if len(quote) < MIN_QUOTE_CHARS:
        return False
    for c, _ in hits:
        if c.doc_id == d.get("doc_id") and c.clause_id == d.get("clause_id"):
            # " … " joins a clause heading to a sub-clause; a quote may not span it
            if any(quote in _normalise(seg) for seg in c.text.split(" … ")):
                return True
    return False


def make_llm(provider: str, model: str) -> Callable[[str, str], tuple[str, int, int]]:
    """Return call(system, user) -> (text, input_tokens, output_tokens)."""
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()                       # reads ANTHROPIC_API_KEY

        def call(system, user):
            r = client.messages.create(model=model, max_tokens=800, temperature=0, system=system,
                                       messages=[{"role": "user", "content": user}])
            return r.content[0].text, r.usage.input_tokens, r.usage.output_tokens
        return call
    if provider == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client()                              # reads GEMINI_API_KEY / GOOGLE_API_KEY

        def call(system, user):
            r = client.models.generate_content(
                model=model, contents=user,
                config=types.GenerateContentConfig(system_instruction=system, temperature=0,
                                                   response_mime_type="application/json"))
            u = r.usage_metadata
            return r.text, getattr(u, "prompt_token_count", 0) or 0, getattr(u, "candidates_token_count", 0) or 0
        return call
    raise ValueError(f"unknown provider {provider}")


def log_call(res: Result, agent: str, prompt_version: str, model: str, path: Path = LOG_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "agent", "prompt_version", "model", "input_tokens", "output_tokens",
                        "latency_s", "verdict", "risk_level", "status", "claim"])
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), agent, prompt_version, model, res.input_tokens,
                    res.output_tokens, round(res.latency_s, 2), res.verdict, res.risk_level, res.status, res.claim])


class Guardrail:
    def __init__(self, retriever: Retriever, llm: Callable, model: str, prompt: str,
                 prompt_version: str = "guardrail_v1", rules_mode: str = "flag_only"):
        assert rules_mode in {"flag_only", "escalate"}
        self.retriever, self.llm, self.model = retriever, llm, model
        self.prompt, self.prompt_version, self.rules_mode = prompt, prompt_version, rules_mode

    def check(self, claim: str, context_note: str = "", log: bool = True) -> Result:
        claim = (claim or "").strip()
        if not claim:
            return Result(claim, "insufficient_basis", "medium", status="error", reason="empty claim")
        rule_hits = keyword_rules(claim)
        hits = self.retriever.search(claim + " " + " ".join(h["rule"].replace("_", " ") for h in rule_hits))
        user = (f"{format_context(hits)}\n\n<where_it_appears>{context_note or 'unspecified'}</where_it_appears>\n"
                f"<claim>\n{claim}\n</claim>")
        t0 = time.time()
        try:
            raw, tin, tout = self.llm(self.prompt, user)
        except Exception as e:                                # network, quota, etc.
            res = Result(claim, "insufficient_basis", "medium", status="error", reason=str(e)[:200])
            res.rule_hits = rule_hits
            return res
        latency = time.time() - t0
        try:
            d = parse_json(raw)
            res = Result(claim, d["verdict"], d["risk_level"], d["doc_id"], d["clause_id"], d["clause_quote"],
                         d["reason"], d["compliant_rewrite"])
            res.quote_verified = verify_quote(d, hits) if d["verdict"] != "insufficient_basis" else False
            res.status = "ok" if (res.quote_verified or d["verdict"] == "insufficient_basis") else "blocked_unverified_citation"
            if res.status != "ok":
                res.clause_quote = "[BLOCKED: quote not found word for word in the retrieved clause]"
        except Exception as e:
            res = Result(claim, "insufficient_basis", "medium", status="parse_error", reason=str(e)[:200])
        res.rule_hits, res.latency_s, res.input_tokens, res.output_tokens = rule_hits, latency, tin, tout
        res.retrieved = [c.key for c, _ in hits]
        if self.rules_mode == "escalate" and any(h["risk"] == "high" for h in rule_hits) and res.verdict == "compliant":
            res.verdict, res.risk_level = "non-compliant", "high"
            res.reason = (res.reason + " [Escalated by keyword rule: " + ", ".join(h["rule"] for h in rule_hits) + "]").strip()
        if log:
            log_call(res, "guardrail", self.prompt_version, self.model)
        return res

# --------------------------------------------------------------------------
# 5. Evaluation
# --------------------------------------------------------------------------

def evaluate(gold: list[dict], results: list[Result]) -> dict:
    """gold rows need 'your_label' in {compliant, non-compliant}. Positive class = non-compliant."""
    tp = fp = fn = tn = 0
    for g, r in zip(gold, results):
        actual = g["your_label"].strip().lower() == "non-compliant"
        pred = r.flagged
        tp += actual and pred; fn += actual and not pred
        fp += (not actual) and pred; tn += (not actual) and (not pred)
    recall = tp / (tp + fn) if tp + fn else float("nan")
    precision = tp / (tp + fp) if tp + fp else float("nan")
    invented = sum(1 for r in results if r.status == "ok" and r.verdict != "insufficient_basis" and not r.quote_verified)
    return {
        "n": len(results), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "recall_noncompliant": recall, "precision_noncompliant": precision,
        "pass_recall_0.9": recall >= 0.9,
        "blocked_unverified_citations": sum(r.status == "blocked_unverified_citation" for r in results),
        "parse_or_call_errors": sum(r.status in {"parse_error", "error"} for r in results),
        "invented_clauses_passed": invented,          # must be 0 by construction
        "total_input_tokens": sum(r.input_tokens for r in results),
        "total_output_tokens": sum(r.output_tokens for r in results),
        "mean_latency_s": sum(r.latency_s for r in results) / max(len(results), 1),
    }
