"""
Offline tests for ai/guardrail.py: no model downloads, no API calls.

Uses a small SYNTHETIC knowledge base (invented wording, clearly not real
regulation) and a mock LLM, to check the parts that must work before any
model is involved: clause chunking, BM25 retrieval, JSON parsing, word-for-word
quote verification, keyword rules, red-team robustness and the metrics.

Run from the repo root:  python -m pytest ai/tests -q   (or: python ai/tests/test_guardrail_offline.py)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ai import guardrail as g  # noqa: E402

SYNTHETIC = """SYNTHETIC TEST DOCUMENT - NOT REAL REGULATION
1. Scope
These test rules apply to claims about textiles made in advertisements.
2. Generic terms
(1) Generic terms such as eco-friendly, green or sustainable shall not be used unless qualified and substantiated with verifiable evidence.
(2) Qualifiers shall be placed next to the generic term.
3. Certification
A claim that a product is certified shall name the certification body and the licence number.
4.1 Organic fibre
The word organic may be used only for fibres that are grown and certified as organic.
4.2 Processed fibres
Processed fibres such as viscose and lyocell shall not be described as organic.
5. Endorsements
Fabricated testimonials and endorsements are prohibited.
Page 2 of 2
"""


def kb():
    lines = [(1, l) for l in SYNTHETIC.splitlines() if l.strip() and not g.PAGE_NUMBER.match(l)]
    return g.chunk_document("TEST", lines, "synthetic")


def test_chunker_keeps_clause_numbers():
    ids = [c.clause_id for c in kb()]
    assert ids == ["preamble", "1", "2", "3", "4.1", "4.2", "5"], ids
    assert "Page 2 of 2" not in " ".join(c.text for c in kb())


def test_bm25_finds_the_right_clause():
    r = g.Retriever(kb(), use_embeddings=False, use_reranker=False)
    top = r.search("organic bamboo viscose kurta", k=2)
    assert top[0][0].clause_id in {"4.2", "4.1"}, [c.key for c, _ in top]


def mock_llm(answer: dict):
    return lambda system, user: (json.dumps(answer), 100, 50)


def guard(answer, rules_mode="flag_only"):
    r = g.Retriever(kb(), use_embeddings=False, use_reranker=False)
    return g.Guardrail(r, mock_llm(answer), "mock", "system prompt", rules_mode=rules_mode)


GOOD = {"verdict": "non-compliant", "risk_level": "high", "doc_id": "TEST", "clause_id": "4.2",
        "clause_quote": "Processed fibres such as viscose and lyocell shall not be described as organic.",
        "reason": "Organic on a processed fibre.", "compliant_rewrite": "Viscose kurta."}


def test_verified_quote_passes():
    res = guard(GOOD).check("Organic viscose kurta", log=False)
    assert res.status == "ok" and res.quote_verified and res.flagged


def test_invented_quote_is_blocked():
    bad = dict(GOOD, clause_quote="Processed fibres may be called organic if soft to touch.")
    res = guard(bad).check("Organic viscose kurta", log=False)
    assert res.status == "blocked_unverified_citation" and not res.quote_verified and res.flagged


def test_wrong_clause_id_is_blocked():
    bad = dict(GOOD, clause_id="99")
    res = guard(bad).check("Organic viscose kurta", log=False)
    assert res.status == "blocked_unverified_citation"


def test_parse_error_is_flagged_not_crashed():
    r = g.Retriever(kb(), use_embeddings=False, use_reranker=False)
    gr = g.Guardrail(r, lambda s, u: ("not json at all", 10, 5), "mock", "p")
    res = gr.check("Eco-friendly kurta", log=False)
    assert res.status == "parse_error" and res.flagged


def test_empty_claim_no_model_call():
    called = []
    r = g.Retriever(kb(), use_embeddings=False, use_reranker=False)
    gr = g.Guardrail(r, lambda s, u: called.append(1) or ("{}", 0, 0), "mock", "p")
    res = gr.check("   ", log=False)
    assert res.status == "error" and not called


def test_keyword_rules():
    names = lambda c: {h["rule"] for h in g.keyword_rules(c)}
    assert "generic_green_term" in names("Made with e-c-o friendly fabric")          # obfuscated
    assert "generic_green_term" in names("Yeh kurta poori tarah eco-friendly hai")   # Hinglish
    assert "organic_on_processed_fibre" in names("100% organic bamboo kurta")
    assert "certification_without_licence" in names("GOTS certified cotton")
    assert "certification_without_licence" not in names("Licence no. XX-1, GOTS certified cotton, certified by CB")
    assert not names("Straight-cut kurta in sizes 38 to 48")


def test_escalate_mode_overrides_compliant():
    ok = dict(GOOD, verdict="compliant", risk_level="low")
    res = guard(ok, rules_mode="escalate").check("Eco-friendly kurta", log=False)
    assert res.verdict == "non-compliant" and "Escalated" in res.reason


def test_evaluate_metrics():
    gold = [{"your_label": "non-compliant"}, {"your_label": "non-compliant"}, {"your_label": "compliant"}]
    res = [g.Result("a", "non-compliant", "high", status="ok", quote_verified=True),
           g.Result("b", "compliant", "low", status="ok", quote_verified=True),
           g.Result("c", "compliant", "low", status="ok", quote_verified=True)]
    m = g.evaluate(gold, res)
    assert m["tp"] == 1 and m["fn"] == 1 and m["tn"] == 1 and abs(m["recall_noncompliant"] - 0.5) < 1e-9
    assert m["invented_clauses_passed"] == 0


def test_errors_do_not_count_as_a_pass():
    """40 failed API calls must not report recall 1.0 as a pass (the 404 bug of 1 Oct 2026)."""
    gold = [{"your_label": "non-compliant"}] * 20 + [{"your_label": "compliant"}] * 20
    res = [g.Result(str(i), "insufficient_basis", "medium", status="error") for i in range(40)]
    m = g.evaluate(gold, res)
    assert m["parse_or_call_errors"] == 40 and m["valid_run"] is False and m["pass_recall_0.9"] is False


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t(); print("PASS", t.__name__)
    print(f"{len(tests)} tests passed")
