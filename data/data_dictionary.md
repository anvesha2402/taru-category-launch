# Data dictionary

One table per dataset. Add a row for every field before the dataset is used in a notebook.

## Template

| Field | Type | Allowed values / unit | Source | Notes |
|---|---|---|---|---|
| _example: `star_rating`_ | integer | 1–5 | Public product page | Copied by hand; no reviewer names |

## `data/raw/price_audit/price_audit.csv`

| Field | Type | Allowed values / unit | Source | Notes |
|---|---|---|---|---|
| brand | text | | Brand site / marketplace | |
| product | text | | | |
| line | text | everyday / festive / ceremonial | Author's classification | |
| fabric_composition | text | e.g. "100% cotton" | Listing | Copy exactly |
| certification_claim | text | exact words, or "none" | Listing | Copy exactly |
| mrp_inr | number | ₹ | Listing | |
| selling_price_inr | number | ₹ | Listing | |
| discount_pct | number | fraction | Calculated | |
| return_policy | text | | Listing | |
| url | text | | | |
| date_collected | date | YYYY-MM-DD | | |

## `data/raw/reviews/reviews.csv`

| Field | Type | Allowed values / unit | Source | Notes |
|---|---|---|---|---|
| brand | text | Manyavar / Fabindia / Tasva / Ethnix | | |
| product | text | | | |
| fabric | text | from listing | | |
| star_rating | integer | 1–5 | | |
| review_text | text | | | No names, handles or photos |
| review_date | date | YYYY-MM-DD | | |
| date_collected | date | YYYY-MM-DD | | |

## `data/clean/survey_clean.csv`

_To be completed when the form is built._
