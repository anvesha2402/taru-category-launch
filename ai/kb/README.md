# Claims Guardrail knowledge base (AI4)

The guardrail answers only from the documents in `raw/`. Download each one yourself from the official source and save it in `ai/kb/raw/` under **exactly** the file name shown, because `ai/guardrail.py` looks for these names.

| doc_id | Save as | What to download | Where |
|---|---|---|---|
| CCPA | `ccpa_greenwashing_guidelines_2024.pdf` | Guidelines for Prevention and Regulation of Greenwashing or Misleading Environmental Claims, 2024 (gazette / official PDF) | Department of Consumer Affairs website (consumeraffairs.nic.in / doca.gov.in). Search the site for "greenwashing guidelines 2024". The Khaitan & Co note in the register (R042) links to it |
| ASCI-GREEN | `asci_environmental_green_claims_2024.pdf` | ASCI Guidelines for Advertisements Making Environmental/Green Claims | https://www.ascionline.in/wp-content/uploads/2024/01/Guidelines-for-Advertisements-Making-Environmental-Green-Claims.pdf |
| ASCI-AI | `asci_ai_labelling_2026_final.pdf` | ASCI Guidelines for Responsible Labelling of Synthetically Generated Content in Advertising (**final**, released 29 Sep 2026) | ascionline.in → Guidelines. Do not use the May 2026 draft |
| LM-PCR | `legal_metrology_packaged_commodities_rules.pdf` | Legal Metrology (Packaged Commodities) Rules, 2011, latest consolidated version including e-commerce amendments | Department of Consumer Affairs / Legal Metrology section of consumeraffairs.nic.in |
| TC-DRAFT | `textiles_committee_draft_labelling_2026.pdf` | Draft labelling regulations, March 2026 | https://textilescommittee.gov.in/wp-content/uploads/2026/03/Draft-regualtions.pdf |
| GOTS | `gots_standard.pdf` | Global Organic Textile Standard, current version (full standard) | global-standard.org → The Standard → download |
| GOTS-LABEL | `gots_label_grades.txt` | The label-grades page: select all text on the page, paste into a plain-text file | https://global-standard.org/certification-and-labelling/labelling/label-grades |
| ITR-2026 | `it_amendment_rules_2026.pdf` | IT (Intermediary Guidelines and Digital Media Ethics Code) Amendment Rules, 2026, as notified | MeitY website (meity.gov.in) → notifications. The Khaitan & Co note (R049) links to it |

## After downloading

1. Run the "Build the knowledge base" cell in `notebooks/07_claims_guardrail.ipynb`. It prints how many clauses it found per document.
2. Any document marked `CHECK` (fewer than 5 clauses found) has a layout the automatic splitter didn't recognise. Open it, and add its clauses by hand to `ai/kb/manual_chunks.jsonl`, one JSON object per line:
   `{"doc_id": "GOTS-LABEL", "clause_id": "organic", "text": "<exact text of the clause>", "page": 1, "title": "GOTS label grades"}`
   Manual chunks replace the automatic ones for that document.
3. Spot-check 5 random clauses against the PDF: the clause number and text must match the source exactly, because every citation the guardrail makes is checked word for word against these chunks.

## Copyright note

Keep the raw PDFs in `ai/kb/raw/` on your own machine or Drive; `raw/` is git-ignored so the repo doesn't republish them. The generated `chunks.jsonl` holds short regulatory excerpts used for checking and can stay in the repo.
