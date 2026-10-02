"""
"AI layer" tab for the TARU app: simple diagrams of where each AI tool sits in the launch,
what happens inside it, what the test found, and where a person decides.

Every number comes from the results files in ai/eval/ and reports/survey_interview_findings.md.
The same diagrams appear in the README as Mermaid charts.
"""
from __future__ import annotations

import html

C = dict(heartwood="#1F3A2F", kora="#F3EEE4", ink="#2B2926", indigo="#26324D", madder="#84302A",
         haldi="#C8912F", khadi="#D9C9A8")

# Box kinds used in every flow. (label shown in the legend)
KINDS = {
    "data": "Input or data",
    "code": "Rule or code check",
    "ai": "AI or ML model",
    "person": "A person decides",
}

# Stages of the launch, left to right, and the tool that supports each one.
STAGES = [
    ("01", "Understand buyers", "AI2"),
    ("02", "Plan demand and stock", "AI7"),
    ("03", "Check every claim", "AI4"),
    ("04", "Draft launch content", "AI5"),
    ("05", "Make campaign images", "AI6"),
]

TOOLS = {
    "AI2": dict(
        name="Review complaint map",
        question="What do buyers complain about that the big brands do not fix?",
        flow=[("data", "287 Myntra reviews, names removed"),
              ("code", "Tag each review by a published keyword list"),
              ("ai", "Topic model (NMF) as a cross-check"),
              ("code", "Compare 1–3 star with 4–5 star reviews"),
              ("person", "Author reads the themes and decides")],
        result=["Fit is the top complaint: 30% of 1–3 star reviews vs 19% of 4–5 star",
                "Agrees with interviews: 8 of 9 buyers named a fit problem"],
        status=("Direction only", "warn"),
        means="TARU's promise became fit: \"cut for the body you have\".",
        source="reports/survey_interview_findings.md §6.2",
    ),
    "AI7": dict(
        name="Demand forecast",
        question="When does demand peak, so stock is paid for in time?",
        flow=[("data", "Google Trends searches, Oct 2021 – Sep 2026"),
              ("ai", "Three methods: same month last year, Holt-Winters, SARIMAX"),
              ("code", "Test on 12 months the models had not seen"),
              ("code", "Keep a model only if it beats the simple baseline"),
              ("person", "Author uses the monthly weights in the cash plan")],
        result=["\"Kurta for men\": the simple baseline wins (12.3% error); the models add error",
                "\"Wedding outfit for men\": Holt-Winters wins (17.8%)",
                "Both peak in October–November"],
        status=("Baseline kept", "ok"),
        means="Stock must be paid for by September. Search interest is not sales.",
        source="reports/survey_interview_findings.md §6.1",
    ),
    "AI4": dict(
        name="Claims guardrail",
        question="Can a checker catch green claims that break Indian rules, without inventing rules?",
        flow=[("data", "A claim, e.g. \"eco-friendly kurta\""),
              ("code", "Find matching clauses: keyword + meaning search over 143 clauses"),
              ("ai", "Re-rank the best clauses (cross-encoder)"),
              ("ai", "Qwen 7B gives a verdict and quotes the clause"),
              ("code", "Quote checked word for word against the rulebook"),
              ("person", "Flagged or blocked claims go to the author")],
        result=["Caught 20 of 20 non-compliant claims",
                "0 invented clauses got through",
                "Precision 0.71 after a rule fix made post-run (to confirm on new claims)",
                "Red team: 9 of 10 attacks handled"],
        status=("Pass test met", "ok"),
        means="Safe as a first screen before a person, not as the final word: it over-flags correct claims.",
        source="ai/eval/AI4_results.md",
    ),
    "AI5": dict(
        name="Content agents",
        question="Can a team of AI agents draft launch posts, product pages and emails in TARU's voice?",
        flow=[("data", "Content request, e.g. a Diwali gifting post"),
              ("ai", "Brief writer"),
              ("ai", "Copywriter"),
              ("code", "Brand rules + AI4 guardrail check every draft"),
              ("ai", "Rewrite if it fails (up to 2 times)"),
              ("ai", "Critic scores the voice"),
              ("person", "Author approves, edits or rejects")],
        result=["14 of 21 passed the checks (target 90%)",
                "8 of 21 scored on-voice by the author (target 80%)",
                "Author: 2 approved, 12 edited, 7 rejected",
                "AI critic vs author: weak agreement (κ 0.22)"],
        status=("Both pass tests failed", "fail"),
        means="Useful as a first draft for a writer. It cannot publish on its own, and the AI critic cannot replace the author.",
        source="ai/eval/AI5_results.md",
    ),
    "AI6": dict(
        name="Image bias audit",
        question="Does the image model show TARU's real customer: men 40–65, fuller builds, Indian skin tones?",
        flow=[("data", "10 casting prompts × 5 fixed seeds"),
              ("ai", "SDXL draws 50 images from plain prompts"),
              ("ai", "Same seeds, rewritten prompts: 50 more"),
              ("person", "100 images shuffled and coded blind by a person"),
              ("code", "Paired test on each same-seed pair")],
        result=["Fuller build when asked: 1 of 20 → 8 of 20 after rewriting (p = 0.016)",
                "Age as asked: 78% → 76%; most misses looked older",
                "Skin tone as asked: 9 of 15 in both versions"],
        status=("Mixed", "warn"),
        means="AI images only as labelled mood images, each checked by a person. Never as product photos.",
        source="ai/eval/AI6_results.md",
    ),
}

LINKS = [  # (from, what it does, to, what happens there)
    ("AI2", "found fit is the top complaint, so TARU promises fit", "AI6", "then tested whether AI images can show fuller builds"),
    ("D7", "lists the claims TARU may make", "AI4", "checks every claim against them and the rules"),
    ("AI5", "sends every draft for checking", "AI4", "screens it before the author sees it"),
    ("AI5", "drafts the author approved", "SHOP", "uses them as its copy"),
    ("AI7", "shows the October–November peak", "XLSX", "the cash plan pays for stock by September"),
]

NOT_BUILT = [
    ("AI1", "Sentiment three ways", "Dropped: only 1 Hinglish review was found, and the test labels would have been AI-made."),
    ("AI3", "Claim-trust regression", "Not run: it depends on the survey claim test, which failed its quality checks."),
    ("AI8", "Provenance chat assistant", "Stretch goal, not built."),
]

ROLE = {"AI2": "AI2 · Review complaint map", "AI4": "AI4 · Claims guardrail", "AI5": "AI5 · Content agents",
        "AI6": "AI6 · Image bias audit", "AI7": "AI7 · Demand forecast", "D7": "D7 · Claims matrix",
        "SHOP": "Storefront mock-up", "XLSX": "Economics model"}


def _e(s: str) -> str:
    return html.escape(s, quote=False)


def _flow(steps: list[tuple[str, str]]) -> str:
    parts = []
    for i, (kind, text) in enumerate(steps):
        if i:
            parts.append('<span class="arr" aria-hidden="true">→</span>')
        parts.append(f'<div class="box {kind}"><span class="k">{_e(KINDS[kind])}</span>{_e(text)}</div>')
    return f'<div class="flow">{"".join(parts)}</div>'


def _tool(tid: str) -> str:
    t = TOOLS[tid]
    label, tone = t["status"]
    res = "".join(f"<li>{_e(r)}</li>" for r in t["result"])
    return f"""
<article class="tool" id="{tid.lower()}">
  <header><span class="tid">{tid}</span><h3>{_e(t['name'])}</h3><span class="status {tone}">{_e(label)}</span></header>
  <p class="q">{_e(t['question'])}</p>
  {_flow(t['flow'])}
  <div class="two">
    <div><h4>What the test found</h4><ul>{res}</ul></div>
    <div><h4>What it means for TARU</h4><p>{_e(t['means'])}</p><p class="src">Source: {_e(t['source'])}</p></div>
  </div>
</article>"""


def render() -> str:
    legend = "".join(f'<span class="lg"><i class="sw {k}"></i>{_e(v)}</span>' for k, v in KINDS.items())

    stages = []
    for num, stage, tid in STAGES:
        t = TOOLS[tid]
        label, tone = t["status"]
        stages.append(f"""
<div class="stage">
  <div class="sn">{num} · {_e(stage).upper()}</div>
  <a class="card" href="#{tid.lower()}"><span class="tid">{tid}</span><b>{_e(t['name'])}</b>
    <span class="one">{_e(t['result'][0])}</span>
    <span class="status {tone}">{_e(label)}</span></a>
  <div class="gate"><i class="sw person"></i>A person decides</div>
</div>""")

    links = "".join(
        f'<li><span class="node">{_e(ROLE[a])}</span> <span class="lt">{_e(what)}</span> '
        f'<span class="arr" aria-hidden="true">→</span> <span class="node">{_e(ROLE[b])}</span> '
        f'<span class="lt">{_e(rest)}</span></li>'
        for a, what, b, rest in LINKS)

    tools = "".join(_tool(tid) for _, _, tid in STAGES)
    nb = "".join(f'<li><span class="tid muted">{a}</span> <b>{_e(n)}</b>. {_e(why)}</li>' for a, n, why in NOT_BUILT)

    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
:root {{ --hw:{C['heartwood']}; --kora:{C['kora']}; --ink:{C['ink']}; --khadi:{C['khadi']}; --indigo:{C['indigo']};
        --madder:{C['madder']}; --haldi:{C['haldi']}; --paper:#FBF8F2; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--kora); color:var(--ink); font:15px/1.5 'IBM Plex Sans', system-ui, sans-serif; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:24px 16px 40px; }}
h2 {{ font:500 26px/1.2 'Fraunces', Georgia, serif; color:var(--hw); margin:0 0 6px; }}
h3 {{ font:500 20px/1.2 'Fraunces', Georgia, serif; color:var(--hw); margin:0; }}
h4 {{ font:500 11px/1.4 'IBM Plex Mono', monospace; letter-spacing:.08em; text-transform:uppercase; color:var(--hw); margin:0 0 6px; }}
p {{ margin:0 0 8px; }}
.lede {{ max-width:760px; margin-bottom:16px; }}
section {{ margin-top:32px; }}
.legend {{ display:flex; flex-wrap:wrap; gap:8px 18px; font-size:13px; margin:8px 0 16px; }}
.lg {{ display:inline-flex; align-items:center; gap:6px; }}
.sw {{ display:inline-block; width:14px; height:14px; border-radius:3px; flex:none; }}
.sw.data, .box.data {{ background:var(--paper); border:1.5px solid var(--khadi); }}
.sw.code, .box.code {{ background:#fff; border:1.5px solid var(--indigo); }}
.sw.ai, .box.ai {{ background:var(--hw); border:1.5px solid var(--hw); color:#fff; }}
.sw.person, .box.person {{ background:var(--haldi); border:1.5px solid var(--haldi); color:var(--ink); }}
.tid {{ font:500 12px/1 'IBM Plex Mono', monospace; color:var(--hw); background:#fff; border:1px solid var(--hw);
        border-radius:4px; padding:3px 6px; }}
.tid.muted {{ color:#6b665e; border-color:#b9b2a5; }}
.status {{ font:500 11px/1 'IBM Plex Mono', monospace; letter-spacing:.04em; text-transform:uppercase; padding:4px 7px; border-radius:4px; white-space:nowrap; }}
.status.ok {{ background:#DCE6DF; color:var(--hw); }}
.status.warn {{ background:#F1E2C2; color:#6A4B12; }}
.status.fail {{ background:#EFD9D6; color:var(--madder); }}

/* diagram 1: stages */
.stages {{ display:grid; grid-template-columns:repeat(5, minmax(0,1fr)); gap:24px; }}
.stage {{ position:relative; display:flex; flex-direction:column; gap:8px; min-width:0; }}
.stage + .stage::before {{ content:"→"; position:absolute; left:-19px; top:62px; color:var(--hw); font-size:18px; }}
.sn {{ font:500 11px/1.3 'IBM Plex Mono', monospace; letter-spacing:.06em; color:var(--hw); min-height:30px; }}
.card {{ display:flex; flex-direction:column; gap:8px; align-items:flex-start; background:#fff; border:1.5px solid var(--hw);
         border-radius:8px; padding:12px; color:inherit; text-decoration:none; flex:1; }}
.card:hover {{ box-shadow:0 0 0 3px rgba(31,58,47,.15); }}
.card b {{ font:500 17px/1.2 'Fraunces', Georgia, serif; color:var(--hw); }}
.card .one {{ font-size:13px; flex:1; }}
.gate {{ display:flex; align-items:center; gap:6px; font-size:12px; }}

.links {{ list-style:none; padding:0; margin:0; display:grid; gap:8px; }}
.links li {{ background:#fff; border:1px solid var(--khadi); border-radius:8px; padding:10px 12px; font-size:14px; }}
.node {{ font-weight:600; color:var(--hw); white-space:nowrap; }}
.lt {{ color:#4a463f; }}
.arr {{ color:var(--hw); font-weight:600; }}

/* diagram 2: inside each tool */
.tool {{ background:#fff; border:1px solid var(--khadi); border-radius:10px; padding:16px; margin-top:16px; scroll-margin-top:12px; }}
.tool header {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:6px; }}
.tool header .status {{ margin-left:auto; }}
.q {{ color:#4a463f; font-style:italic; }}
.flow {{ display:flex; flex-wrap:wrap; align-items:stretch; gap:8px 6px; margin:12px 0 14px; }}
.flow .arr {{ align-self:center; }}
.box {{ flex:1 1 130px; max-width:200px; min-width:0; border-radius:6px; padding:8px 10px; font-size:13px; line-height:1.35; }}
.box .k {{ display:block; font:500 9.5px/1.3 'IBM Plex Mono', monospace; letter-spacing:.06em; text-transform:uppercase; opacity:.75; margin-bottom:3px; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
.two ul {{ margin:0; padding-left:18px; }}
.two li {{ margin-bottom:3px; }}
.src {{ font:400 11px/1.4 'IBM Plex Mono', monospace; color:#6b665e; }}
.nb {{ padding-left:0; list-style:none; display:grid; gap:8px; }}
.rule {{ background:var(--hw); color:#fff; border-radius:10px; padding:16px; margin-top:32px; }}
.rule b {{ font:500 19px/1.3 'Fraunces', Georgia, serif; }}
.rule p {{ margin:6px 0 0; font-size:13px; opacity:.9; }}

@media (max-width: 900px) {{
  .stages {{ grid-template-columns:1fr; gap:28px; }}
  .stage + .stage::before {{ content:"↓"; left:12px; top:-25px; }}
  .sn {{ min-height:0; }}
  .two {{ grid-template-columns:1fr; gap:12px; }}
  .box {{ max-width:none; flex-basis:100%; }}
  .flow {{ flex-direction:column; }}
  .flow .arr {{ transform:rotate(90deg); align-self:flex-start; margin-left:14px; }}
  .tool header .status {{ margin-left:0; }}
}}
</style></head><body><div class="wrap">

<h2>Where AI sits in the TARU launch</h2>
<p class="lede">Five AI tools were built and tested, one for each stage of the launch. Each one does the first pass of a task,
and a person makes the decision. Click a tool to see inside it.</p>
<div class="legend">{legend}</div>
<div class="stages">{''.join(stages)}</div>

<section>
<h2>How the tools feed each other</h2>
<ul class="links">{links}</ul>
</section>

<section>
<h2>Inside each tool</h2>
<p class="lede">Each row reads left to right: what goes in, what the AI does, what code checks, and where a person decides.</p>
{tools}
</section>

<section>
<h2>Planned but not built</h2>
<ul class="nb">{nb}</ul>
</section>

<div class="rule"><b>One rule across every tool: nothing reaches a customer without a person's approval.</b>
<p>Models: Qwen2.5-7B-Instruct (Apache 2.0) for AI4 and AI5; Stable Diffusion XL 1.0 (CreativeML Open RAIL++-M) for AI6; standard Python
libraries for AI2 and AI7. All open-weight, run on free cloud GPUs, no per-use fee. Failed tests are reported as failed.</p></div>

</div></body></html>"""


if __name__ == "__main__":  # quick preview: python app/ai_layer.py > /tmp/ai_layer.html
    print(render())
