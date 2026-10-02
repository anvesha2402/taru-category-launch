"""Offline tests for ai/content_agents.py: mock LLMs, no downloads, no API calls."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ai import content_agents as ca  # noqa: E402

REQ = {"request_id": "T1", "content_type": "social_post", "channel": "Instagram", "segment": "self-buyer",
       "occasion": "everyday", "product_line": "Everyday", "request": "Free alterations"}
CLAIMS = [{"id": "CL07", "wording": "Free alterations within 30 days of delivery.", "decision": "Use"}]
BRIEF = json.dumps({"objective": "x", "audience": "y", "occasion": "z", "key_message": "k",
                    "approved_claim_ids": ["CL07"], "facts_to_use": [], "call_to_action": "Visit"})
CRITIC = json.dumps({"clarity": 4, "voice": 4, "claim_accuracy": 5, "call_to_action": 4, "overall": 4, "note": "ok"})


def scripted(drafts):
    """LLM mock: brief call, then drafts in order, then the critic."""
    seq = iter([BRIEF] + drafts + [CRITIC])
    return lambda system, user: (next(seq), 10, 5)


def team(drafts, guardrail=None):
    return ca.ContentTeam(scripted(drafts), guardrail=guardrail, voice="voice", claims=CLAIMS)


def test_rule_violations():
    v = ca.rule_violations("Amazing eco kurta! Loved by 10,000 customers. Only 3 left. Better than Manyavar #organic")
    assert any("exclamation" in x for x in v) and any("eco" in x for x in v)
    assert "fake scarcity" in v and "testimonial or review" in v and "hashtag in body copy" in v
    assert any("manyavar" in x for x in v)
    assert ca.rule_violations("Free alterations within 30 days of delivery. Visit the pop-up on Saturday.") == []


def test_clean_draft_passes_first_time():
    o = team(["Free alterations within 30 days of delivery. Book a fitting."]).run(REQ)
    assert o.passed and o.revisions == 0 and o.critic["overall"] == 4


def test_revision_fixes_rule_violation():
    o = team(["A sustainable kurta!", "Free alterations within 30 days of delivery."]).run(REQ)
    assert o.passed and o.revisions == 1 and len(o.drafts) == 2


def test_stops_after_two_revisions_and_flags():
    o = team(["Eco kurta!", "Green kurta!", "Pure kurta!"]).run(REQ)
    assert not o.passed and o.revisions == ca.MAX_REVISIONS and o.rule_issues


class FakeResult:
    def __init__(self, flagged):
        self.flagged, self.verdict, self.status = flagged, "non-compliant" if flagged else "compliant", "ok"
        self.doc_id, self.clause_id, self.reason, self.compliant_rewrite = "CCPA", "5", "generic term", ""


class FakeGuardrail:
    def __init__(self): self.seen = []
    def check(self, claim, note=""):
        self.seen.append(claim)
        return FakeResult("planet" in claim.lower())


def test_guardrail_called_on_claim_sentences_only():
    fg = FakeGuardrail()
    o = team(["Good for the planet. See you on Saturday.", "Free alterations within 30 days of delivery. See you on Saturday."],
             guardrail=fg).run(REQ)
    assert o.passed and o.revisions == 1
    assert "See you on Saturday." not in fg.seen and any("planet" in s for s in fg.seen)


def test_evaluate_with_human_scores():
    rows = [{"passed_checks": "True", "revisions": "0", "critic_overall": "4", "your_voice_score": "4"},
            {"passed_checks": "True", "revisions": "1", "critic_overall": "5", "your_voice_score": "3"},
            {"passed_checks": "False", "revisions": "2", "critic_overall": "3", "your_voice_score": ""}]
    m = ca.evaluate(rows)
    assert abs(m["pass_rate"] - 2 / 3) < 1e-9 and not m["pass_test_guardrail_0.9"]
    assert m["human_scored"] == 2 and m["share_human_score_ge4"] == 0.5 and m["judge_exact_agreement"] == 0.5


def test_approved_claims_from_d7():
    ids = {c["id"] for c in ca.approved_claims()}
    assert {"CL05", "CL06", "CL07", "CL10", "CL22"} <= ids                # Use
    assert not ids & {"CL08", "CL12", "CL13", "CL14", "CL15", "CL16", "CL17", "CL18", "CL19"}   # test-only, banned, image label


def test_sentence_split_keeps_licence_number():
    s = ca.split_sentences("Organic cotton fabric, certified by [body], licence no. [X]. Book a fitting.")
    assert s == ["Organic cotton fabric, certified by [body], licence no. [X].", "Book a fitting."]
