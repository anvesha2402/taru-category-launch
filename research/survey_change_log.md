# Survey change log

Every departure from Appendix A5 of the brief, with its reason. Add pilot changes below.

| # | Date | Change | Reason |
|---|---|---|---|
| 1 | 29 Sep 2026 | A4 (day of birth) moved after Block B, into its own page | Google Forms branches at the end of a page. A4 must be the last question before the claim test, or the branch would skip Block B |
| 2 | 29 Sep 2026 | Consent, A1 and A2 each sit on their own page | Each has an "end survey" option; Forms branches reliably on one question per page |
| 3 | 29 Sep 2026 | Age bands set to Under 18 / 18–24 / 25–32 / 33–39 / 40–49 / 50–60 / 61+ | Brief does not specify bands; these separate gifters (25–40) from self-buyers (40–60) |
| 4 | 29 Sep 2026 | Block H asks income band only | Age band (A1) and city (A3) are already collected; asking twice adds time and inconsistency |
| 5 | 29 Sep 2026 | Card C wording keeps "GOTS-certified" and the licence number from Card B (DL-11) | Otherwise C vs B changes three things at once and cannot isolate the benefit + QR bundle |
| 6 | 29 Sep 2026 | Attention check reads "For this row, please select '2 Disagree'" | Matches the scale labels exactly so failures are unambiguous |
| 7 | 29 Sep 2026 | **Speeders cannot be measured** | Google Forms records only the submission time, not the start time. Quality screens used instead: attention-check failure, straight-lining (same answer on every row of the trust grid and both Kano grids), Van Westendorp order violations (D1 ≤ D2 ≤ D3 ≤ D4), and role/age contradictions (A1 vs A2). Report this as a limitation |
| 8 | 29 Sep 2026 | "Both" respondents count toward both quotas; segment comparisons use the role of the most recent purchase (DL-05) | Keeps sample size and gives mutually exclusive groups for analysis |

## Pilot changes

| # | Date | Change | Reason | Pilot respondent(s) |
|---|---|---|---|---|
| | | | | |

## Decision DL-13 (30 Sep 2026): guardrail test set authorship

The 40 guardrail test claims were drafted with AI assistance and each label is derived from a named clause in the knowledge-base documents (column `clause_you_relied_on`), rather than written and labelled independently by the author as DL-04 required. Mitigations: every label cites its clause; the guardrail is run on a different model (Gemini); a classmate's independent labels are to be added in `classmate_label`. AI1 (sentiment three ways) is dropped rather than scored against AI-made labels.

## Decision DL-14 (1 Oct 2026): first AI4 run invalid; GOTS added to the knowledge base

The first Colab run of `07_claims_guardrail.ipynb` returned `404 NOT_FOUND` on all 40 calls (model name not available to the API key). Because a failed call is routed to a person, it counted as "flagged", so the run showed recall 1.0 and a pass. That result is discarded. `evaluate()` now reports `valid_run` (at most 5% failed calls) and the pass requires it; the notebook lists the models the key can use and makes one test call before scoring. GOTS Version 8.0 (2 March 2026) was added, limited to PDF pages 12–15 (sections 2.5.10–3.2.10: GOTS signs, label grades, fibre blends); clause ids of the other documents are unchanged, so the cited clauses in the 40 test claims still resolve. The GOTS label-grades web page (`GOTS-LABEL`) is not included; GOTS 2.7.6 states the same grades.
