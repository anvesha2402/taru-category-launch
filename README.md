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

_Diagram to be added._

Desk research → interviews → review mining → survey with a randomised 3-arm claim test → analysis → brand, range and claims matrix → channel economics and cash plan → live calculator.

## Key findings

_To be added._

## Live calculator

_Link and GIF to be added once the Streamlit app is deployed._

## Brand book preview

_To be added._

## Repository map

| Folder | Contents |
|---|---|
| `app/` | Streamlit "TARU Premium and Channel Calculator" (D9) |
| `data/raw/` | Price audit, review corpus, Google Trends CSVs, anonymised survey export |
| `data/clean/` | Cleaned datasets; `data/data_dictionary.md` describes every field |
| `notebooks/` | 01–05 analysis notebooks (D5) and 06–10 AI/ML notebooks (D12) |
| `research/` | Interview guides, codebook, JTBD statements, questionnaire, product cards (D2, D4) |
| `brand/` | Brand book, claim library, tag and QR-page mock-ups (D6) |
| `compliance/` | Claims substantiation matrix (D7) |
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
