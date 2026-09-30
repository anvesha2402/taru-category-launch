---
title: "TARU Survey Stimuli Spec"
subtitle: "3 claim-test cards · 1 ceremonial card · 3 interview proof cards · 3 brand routes"
---

**Status:** v1.0, 29 Sep 2026. Build everything in Canva from this spec. Every stimulus is test-only: it goes into the claims matrix (D7) as a test-only row and never appears in public brand material.

# 1. Rules for all cards

| Rule | Why |
|---|---|
| One photo, used identically on every claim card (same crop, size, position) | The claim must be the only thing that differs between arms |
| Label strip at the top of every card: **"Hypothetical test stimulus"** | Brief 6.12; respondents must not think it is a real product |
| No price anywhere | Price is measured separately in Block D |
| No GOTS logo, no certifier logo, no competitor names or marks | Using a certification mark without a licence is trademark misuse; text carries the claim |
| No real QR code: use a generic QR-style icon that links nowhere | A working QR would lead to a page that doesn't exist |
| Size 1080 × 1350 px (portrait), exported as PNG | Readable on a phone, where most responses will come from |
| Same font, size and box for the claim text on every card | A bigger or bolder claim would win for design reasons, not content |

**The photo.** A man aged roughly 45–55, average-to-fuller build, in a plain off-white or light-coloured cotton kurta set, neutral background. Use a stock photo whose licence allows commercial use (e.g. Unsplash or Pexels), or an AI-generated image carrying an "AI-generated image" note in small text on every card. Record the photo's source and licence as a register row. No celebrity or recognisable public figure.

# 2. Layout (identical for cards A, B, C and the ceremonial card)

| Zone (top to bottom) | Height | Content |
|---|---|---|
| Label strip | ~6% | "Hypothetical test stimulus" in small caps, grey band |
| Photo | ~60% | The one shared photo |
| Brand line | ~6% | **TARU** wordmark in a plain neutral serif or sans-serif (not one of the three brand routes) |
| Product line | ~6% | "Everyday Kurta Set" (ceremonial card: see below) |
| Claim box | ~16% | The arm's claim, same font and size on every card |
| Footer | ~6% | Blank on A and B; QR icon + "Scan to see the farm-to-tag trail" sits inside the claim box on C, so the footer stays blank everywhere |

# 3. Claim-test cards (Block C)

| Card | Arm | Claim text (exact) |
|---|---|---|
| Card A | Control | Made from natural fibres. |
| Card B | Certification | GOTS-certified organic cotton. Licence no. [placeholder] |
| Card C | Benefit + proof bundle | GOTS-certified organic cotton that stays soft through a 6-hour function. Licence no. [placeholder] Scan to see the farm-to-tag trail. [QR icon] |

**Licence number placeholder.** Use the same obviously illustrative string on B and C, e.g. `Licence no. XX-GOTS-000000`, so no one can mistake it for a real certificate.

**Wording change on Card C (logged as DL-11).** The brief's Card C reads "Certified organic cotton that stays soft through a 6-hour function. Scan to see the farm-to-tag trail." That wording drops both "GOTS" and the licence number that Card B shows. C vs B would then change three things at once: it would remove the certifier name and the licence number, while adding the benefit and the QR. Keeping B's full wording inside C means C vs B isolates what the brief intends to test: adding a benefit and traceability to the same certification. If you prefer the brief's original wording, revert it and note that C vs B is then confounded.

**Card C is longer than A and B.** That can't be avoided; note it as a limitation in the write-up.

# 4. Ceremonial card (Block D, second price set)

Same layout, same label strip, a different photo of the same model in a ceremonial set if available (otherwise the same photo). No claim box text other than a neutral description:

> TARU Ceremonial Set: kurta, churidar and Nehru jacket, for weddings and family functions.

No organic, certification or fibre claim: this card is neutral by design, per brief 8.5.

# 5. Interview proof cards (P1–P3)

Used only in interviews (guide question 6 for self-buyers, question 5 for gifters). Each card shows **one proof type**, on a mock swing tag or card, without the product photo.

| Card | Proof | Content |
|---|---|---|
| P1 | Certification on the tag | Mock swing tag: "GOTS-certified organic cotton · Licence no. XX-GOTS-000000 · Certified by [certification body]" |
| P2 | QR traceability trail | Mock tag with QR icon + a simple strip: Farm → Gin → Mill → Garment, each with a place name and a transaction-certificate reference |
| P3 | Comfort guarantee | Mock card: "Comfort guarantee. If the fabric irritates your skin, return it within 30 days for a full refund." |

Label each card "Hypothetical test stimulus" in the corner.

# 6. Brand routes (Block F)

Three rough visual routes. **No claims and no taglines on the route cards**, so respondents judge the look, not the words. Each route is one 1080 × 1350 card showing the wordmark, the palette as swatches, one styled image of the same model, and a sample swing tag with only "TARU" and a size.

| | Route 1: Heritage | Route 2: Quiet Proof | Route 3: Occasion |
|---|---|---|---|
| Idea | Rooted, crafted, generational | Understated, precise, evidence-led | Warm, celebratory, family |
| Palette | Deep forest green #2F4F3E · ivory #F4EFE3 · raw umber #7A5C3E | Charcoal #2B2B2B · warm off-white #F7F5F0 · muted sage #A3B18A | Indigo #2E3A6B · turmeric #D9A441 · maroon #7B2D26 |
| Type (Google Fonts) | Cormorant Garamond (wordmark) + Lora | Inter (all text), wordmark in tracked capitals | Tenor Sans (wordmark) + Source Serif 4 |
| Imagery | Soft daylight, wood and handloom textures | Clean studio light, close-ups of fabric weave and the tag | Evening light, festive setting, family occasion |
| Tag style | Kraft card, string tie | Minimal white card, fibre data layout | Textured card with a block-print border |

**Starting tagline.** The brief's "Rooted in nature. Refined by time." is kept off the route cards. "Nature" is a generic environmental term that the CCPA 2024 guidelines treat as needing qualification, so the tagline needs its own row in D7 before any public use.

# 7. Where the images go

1. Export all cards as PNG from Canva.
2. Upload them to the Drive folder `taru-category-launch` → subfolder `survey_images`.
3. For each image, open it in Drive, click **Share → Copy link**, and copy the ID (the long string between `/d/` and `/view`).
4. Paste the IDs into the `CONFIG` block at the top of `build_taru_survey.gs` before running it. If you run the script before the images exist, it adds placeholder text where each image goes, and you insert the images by hand in the Forms editor.

| Image | CONFIG key |
|---|---|
| Card A | `CARD_A` |
| Card B | `CARD_B` |
| Card C | `CARD_C` |
| Ceremonial card | `CARD_CEREMONIAL` |
| Route 1, 2, 3 | `ROUTE_1`, `ROUTE_2`, `ROUTE_3` |
