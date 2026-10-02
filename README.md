# TARU: Creating a Certified-Organic Ethnic Wear Category for Indian Men

**Can a new brand earn and hold a price premium for certified-organic men's ethnic wear, and which product, proof, price, channel and cash plan makes that work?**

> **Disclaimer.** TARU is a fictional brand created for an independent student portfolio project. Market, competitor and regulatory facts come from public sources as cited. Consumer findings come from the author's own research with a convenience sample. Costs, targets and financial projections are illustrative assumptions.

---

## TL;DR

Status: research and economics complete; see `reports/TARU_Research_Economics_Recommendation.pdf`.

| | |
|---|---|
| Recommendation (go / no-go / pivot) | **Pivot**: launch through pop-ups, corporate gifting and own website; no marketplace; lean team; test in festive 2027 |
| Winning proof and its effect size | Untested: survey failed quality checks; interviews lean to the certification tag (4 of 9) |
| Acceptable price range (Everyday set) | ₹1,250–3,800 (survey, direction only); priced at ₹2,499 under the GST slab |
| Break-even | Briefed plan: none in 24 months. Pivot: ~280 sets a month |

## Business question and decision questions

| # | Decision question | Exhibit |
|---|---|---|
| Q1 | Who is the first customer (self-buyer aged 40–60 or gifter), and for which occasion? | Target and occasion choice with segment sizes |
| Q2 | What makes "organic" believable and valuable to them? Which proof moves trust most? | Claim-test results with effect sizes; proof-system design |
| Q3 | Is the reachable market big enough? | Adjustable TAM/SAM/SOM model |
| Q4 | What premium can each line hold, and does it cover cost? | Good-Better-Best price architecture with margin per SKU |
| Q5 | Which channels, in which order, at what contribution per unit? | Channel sequence and a margin waterfall per channel |
| Q6 | When to launch, and how much cash does the inventory need? | 24-month P&L, inventory and working-capital curve |

## Approach

```mermaid
flowchart LR
  A["Desk research<br/>market, rules, prices"] --> B["Interviews<br/>9 buyers, 2 partners"] --> C["Review mining<br/>287 reviews"] --> D["Survey with a<br/>3-arm claim test"]
  D --> E["Analysis"] --> F["Brand, range and<br/>claims matrix"] --> G["Channel economics<br/>and cash plan"] --> H["Live calculator"]
  classDef step fill:#F3EEE4,stroke:#1F3A2F,color:#2B2926
  classDef out fill:#1F3A2F,stroke:#1F3A2F,color:#ffffff
  class A,B,C,D,E,F,G step
  class H out
```

## Key findings

_To be added._

## AI/ML layer

Five AI tools were built and tested, one for each stage of the launch. Each does the first pass of a task; the author makes every decision. Nothing reaches a customer without a person's approval. The same diagrams are in the app's **AI layer** tab.

```mermaid
flowchart LR
  subgraph IN["Inputs"]
    REV[("287 Myntra reviews")]
    TR[("Google Trends")]
    D7[("D7 · Claims matrix<br/>approved claims")]
    REQ[("Content requests")]
  end
  subgraph AI["AI tools (first pass)"]
    AI2["AI2 · Review complaint map"]
    AI7["AI7 · Demand forecast"]
    AI4["AI4 · Claims guardrail"]
    AI5["AI5 · Content agents"]
    AI6["AI6 · Image bias audit"]
  end
  P{{"Author decides"}}
  subgraph OUT["Where the results go"]
    FIT["Fit promise and<br/>casting brief"]
    CASH["Cash plan:<br/>stock paid by September"]
    SHOP["Storefront copy"]
    IMG["Mood images only,<br/>labelled"]
  end
  REV --> AI2
  TR --> AI7
  D7 --> AI4
  REQ --> AI5
  AI5 -- "every draft" --> AI4
  AI2 -- "fit is the top complaint" --> AI6
  AI2 --> P
  AI7 --> P
  AI4 -- "flagged claims" --> P
  AI5 -- "drafts" --> P
  AI6 -- "audit results" --> P
  P --> FIT & CASH & SHOP & IMG
  classDef data fill:#FBF8F2,stroke:#D9C9A8,color:#2B2926
  classDef ai fill:#1F3A2F,stroke:#1F3A2F,color:#ffffff
  classDef person fill:#C8912F,stroke:#C8912F,color:#2B2926
  classDef out fill:#ffffff,stroke:#26324D,color:#2B2926
  class REV,TR,D7,REQ data
  class AI2,AI7,AI4,AI5,AI6 ai
  class P person
  class FIT,CASH,SHOP,IMG out
  style IN fill:#F3EEE4,stroke:#D9C9A8,color:#2B2926
  style AI fill:#F3EEE4,stroke:#1F3A2F,color:#2B2926
  style OUT fill:#F3EEE4,stroke:#26324D,color:#2B2926
```

| Tool | Launch stage | What it does | What the test found | Status |
|---|---|---|---|---|
| AI2 Review complaint map | Understand buyers | Tags 287 Myntra reviews by aspect; topic model (NMF) as a cross-check | Fit is the top complaint: 30% of 1–3 star reviews vs 19% of 4–5 star | Direction only |
| AI7 Demand forecast | Plan demand and stock | Compares same-month-last-year, Holt-Winters and SARIMAX on 12 unseen months of Google Trends | Simple baseline wins for "kurta for men" (12.3% error); peak in October–November | Baseline kept |
| AI4 Claims guardrail | Check every claim | Retrieves rule clauses (keyword + meaning search, re-ranked), Qwen 7B gives a verdict with a quote, code checks the quote word for word | 20/20 non-compliant claims caught; 0 invented clauses passed; precision 0.71 after a post-run rule fix | Pass test met |
| AI5 Content agents | Draft launch content | Brief writer → copywriter → rule and AI4 checks (up to 2 rewrites) → critic → author | 14/21 passed checks (target 90%); 8/21 on-voice (target 80%); critic vs author κ 0.22 | Both pass tests failed |
| AI6 Image bias audit | Make campaign images | 100 SDXL images (plain vs rewritten prompts, same seeds), coded blind by a person | Fuller build 1/20 → 8/20 (p = 0.016); age and skin tone did not improve | Mixed: mood images only |

Planned but not built: AI1 sentiment three ways (only 1 Hinglish review; labels would have been AI-made), AI3 claim-trust regression (depends on the survey, which failed its quality checks), AI8 provenance chat assistant (stretch).

<details>
<summary><b>Inside AI4, AI5 and AI6</b></summary>

**AI4 Claims guardrail** (`ai/guardrail.py`, `notebooks/07_claims_guardrail.ipynb`, results `ai/eval/AI4_results.md`)

```mermaid
flowchart LR
  A["Claim"] --> B["Find clauses:<br/>keyword + meaning search"] --> C["Re-rank<br/>(cross-encoder)"] --> D["Qwen 7B: verdict<br/>+ quoted clause"] --> E{"Quote matches the<br/>rulebook word for word?"}
  E -- "yes" --> F["Verdict stands"]
  E -- "no" --> H{{"Author reviews"}}
  F -- "non-compliant" --> H
  classDef ai fill:#1F3A2F,stroke:#1F3A2F,color:#ffffff
  classDef code fill:#ffffff,stroke:#26324D,color:#2B2926
  classDef person fill:#C8912F,stroke:#C8912F,color:#2B2926
  class C,D ai
  class A,B,E,F code
  class H person
```

**AI5 Content agents** (`ai/content_agents.py`, `notebooks/08_content_agents.ipynb`, results `ai/eval/AI5_results.md`)

```mermaid
flowchart LR
  R["Content request"] --> B["Brief writer"] --> W["Copywriter"] --> K{"Brand rules and<br/>AI4 guardrail pass?"}
  K -- "no: rewrite (max 2)" --> W
  K -- "yes, or out of rewrites" --> J["Critic scores<br/>the voice"] --> H{{"Author approves,<br/>edits or rejects"}}
  classDef ai fill:#1F3A2F,stroke:#1F3A2F,color:#ffffff
  classDef code fill:#ffffff,stroke:#26324D,color:#2B2926
  classDef person fill:#C8912F,stroke:#C8912F,color:#2B2926
  class B,W,J ai
  class R,K code
  class H person
```

**AI6 Image bias audit** (`notebooks/09_image_bias_audit.ipynb`, results `ai/eval/AI6_results.md`)

```mermaid
flowchart LR
  P["10 casting prompts<br/>× 5 fixed seeds"] --> B["SDXL: plain prompts<br/>50 images"]
  P --> R["SDXL: rewritten prompts,<br/>same seeds, 50 images"]
  B --> S["Shuffle and<br/>hide labels"]
  R --> S
  S --> H{{"A person codes blind:<br/>age, build, skin tone"}} --> T["Paired test<br/>on each seed"]
  classDef ai fill:#1F3A2F,stroke:#1F3A2F,color:#ffffff
  classDef code fill:#ffffff,stroke:#26324D,color:#2B2926
  classDef person fill:#C8912F,stroke:#C8912F,color:#2B2926
  class B,R ai
  class P,S,T code
  class H person
```

Key: dark green = AI model · white = input, rule or code check · gold = a person decides.
</details>

## Live calculator

**TARU Premium and Channel Calculator** (`app/`, Streamlit). Link: _add after deployment_.

- **Calculator:** change price, fabric and stitching cost, channel mix, acquisition cost, returns, cash on delivery, retailer margin and sale-or-return; see contribution per set by channel, a cost waterfall, blended margin, the premium over Manyavar, break-even sets per month and a warning outside the survey's acceptable price range. Two presets: the plan as briefed (₹355 per set, 957 sets a month to break even) and the recommended pivot (₹677, 281). Defaults reproduce `model/taru_economics.xlsx` exactly (`app/tests/test_model.py`).
- **Storefront (mock-up):** a non-functional shop page in the brand identity, using only approved claims (D7) and author-approved AI5 copy. Images are AI-generated concept images, each labelled, cropped so no text inside an image makes an unapproved claim (`brand/concept_images/README.md`).
- **AI layer:** simple diagrams of where each AI tool sits in the launch, what happens inside it, what its test found and where a person decides.
- **Evidence:** each research source with an honest status (not valid / direction only).
- **About and disclaimer.**

Run locally: `pip install -r app/requirements.txt && streamlit run app/app.py`

## Brand book preview

_To be added._

## Repository map

| Folder | Contents |
|---|---|
| `app/` | Streamlit "TARU Premium and Channel Calculator" (D9): calculator, storefront mock-up, AI layer, evidence |
| `data/raw/` | Price audit, review corpus, Google Trends CSVs, anonymised survey export |
| `data/clean/` | Cleaned datasets; `data/data_dictionary.md` describes every field |
| `notebooks/` | 01–05 analysis notebooks (D5) and 06–10 AI/ML notebooks (D12) |
| `research/` | Interview guides, codebook, JTBD statements, questionnaire, product cards (D2, D4) |
| `brand/` | Brand book, claim library, tag and QR-page mock-ups (D6) |
| `compliance/` | Claims substantiation matrix (D7) and the AI4 guardrail's pre-screen of it (`claims_matrix_prescreened.csv`) |
| `model/` | `taru_economics.xlsx`: range, price and channel economics model (D8) |
| `reports/` | Category dossier, launch deck, executive summary (D1, D10) |
| `ai/` | Prompt library, evaluation sets, red-team log, bias audit, call logs, guardrail knowledge base |
| `assets/` | Images and charts used in this README |

## Methods and limitations

_To be added. Will cover sample sizes, the convenience-sample caveat, the stated-preference discount, and every assumption flagged as low confidence in the sources register._

## How to reproduce

```bash
git clone https://github.com/<your-username>/taru-category-launch.git
cd taru-category-launch
pip install -r requirements.txt
# open the notebooks in order (01 → 10) in Jupyter or Google Colab
streamlit run app/app.py
```

## Research ethics

- Every survey and interview participant saw a consent statement. No names or contact details are stored.
- Interview notes are anonymised (B01–B09, P01–P02) **before** any AI tool processes them. Raw notes and recordings never enter this repository.
- Reviews and prices were collected by hand from public pages. Only review text, star rating and date are stored, never reviewer identities.
- No employer-confidential information is used.

## AI-assistance note

AI tools were used to write code, to act as the first coder on anonymised interview excerpts, and to draft review-topic labels. The author checked every output, blind-coded a 20% sample to measure agreement (Cohen's κ), and made every final decision. The hand-labelled test sets (120 reviews, 40 claims) were created by the author before any model saw them. All AI-generated images are labelled.

## Licence

Source code is released under the MIT licence (see `LICENSE`). Research materials, datasets, survey instruments, brand assets and reports are all rights reserved.

## Author

Anvesha · PGDM (E-Business), WeSchool Mumbai
