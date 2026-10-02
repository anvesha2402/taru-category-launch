# AI6 Image generation with a bias audit: results

**Model:** Stable Diffusion XL base 1.0 (CreativeML Open RAIL++-M) with the fp16-fix VAE, 20 steps, guidance 6.5, 1024 × 1024, Kaggle GPU (median 17 s per image). **Images:** 100 = 10 prompts × 5 fixed seeds × 2 versions. **Baseline** prompts are written as a marketer would; **revised** prompts describe the same man explicitly and add a negative prompt (young, slim, fair skin, logos…). The same seeds are used in both versions, so each baseline image has a revised twin. Every image carries a visible "AI-generated image" label.

**Coding:** one coder (the author's friend) coded all 100 images from the blind coding sheet, where images are shuffled under IDs that do not show the prompt or version. Codes: apparent age band, build (slim / average / fuller), Monk Skin Tone (1–10), visible text or logo. No second coder, so coder reliability is unknown.

## 1. Headline

| Did the image match what the prompt asked? | Baseline | Revised | Paired test (same seed) |
|---|---|---|---|
| Age band as asked | 78% (39/50) | 76% (38/50) | 9 fixed, 10 broken; exact McNemar p = 1.0 |
| **Fuller build, when asked (4 prompts)** | **5% (1/20)** | **40% (8/20)** | **7 fixed, 0 broken; p = 0.016** |
| Skin tone in the asked Monk range (3 prompts) | 60% (9/15) | 60% (9/15) | 3 fixed, 3 broken; p = 1.0 |

All 100 images were usable (one adult man clearly the main subject).

## 2. Findings

1. **The model slims bodies.** When asked for a fuller or heavy build, it drew one in 1 of 20 baseline images: 19 of 20 came out slim or average. Explicit wording ("heavyset, broad waist, round belly") plus a negative prompt raised this to 8 of 20, a significant improvement on paired seeds, but 12 of 20 were still slimmer than asked. For a brand whose promise is "cut for the body you have", this is the decisive finding: **the model cannot be relied on to show TARU's customer without checking every image.**
2. **Age drifts older, not younger.** Most age bands matched. Of the misses, 8 of 11 (baseline) and 11 of 12 (revised) looked older than asked. The revised prompts' age cues ("grey hair, wrinkles") overshot: the early-40s man (P07) came out 50+ in 4 of 5 revised images, against 0 of 5 in baseline. More explicit prompting fixed one attribute and pushed another off target.
3. **Skin tone did not respond to prompting.** For prompts asking for deep dark brown skin (Monk 7–10), codes were mostly 6–7; for P09 baseline, 4 of 5 images were coded lighter than asked. Rewording ("deep dark brown skin, true-to-life skin tone") and "fair skin" in the negative prompt did not change the match rate (9/15 both versions). When the prompt did not specify skin tone, the median coded tone was 6.
4. **Background text.** 7 of 100 images contained visible text or sign-like marks, all in the wedding-venue (P06) and temple-courtyard (P09) scenes. Any such image needs checking for stray brand-like marks before use.

## 3. What it means for TARU
- AI imagery may be used only as labelled mood or concept images (brand book; D7 CL18), never as product photography, which must show the real garment on real bodies.
- Every AI image must be reviewed against the casting brief (age 40–65, at least one fuller build in every three images, unlightened skin) before use. Prompting alone does not meet the brief.
- Autonomy level stays at 2: the model generates; a person selects.

## 4. Limitations
- **One coder.** Apparent age, build and skin tone are judgements; with a single coder their reliability cannot be measured. The codes are concentrated (Monk 6 for 64% of images; "average" build for 78%), which can mean either real similarity or limited discrimination by the coder. A second coder on 20+ images would settle this (the notebook's second-coder cell computes agreement).
- Monk tone was judged from on-screen images whose lighting varies.
- One model, one sampler setting, 5 seeds per prompt; the 20-image build comparison is small, though the paired test is significant.
- The revised version changes two things at once (wording and negative prompt), so their separate effects cannot be told apart.

Files: `ai/eval/ai6/` (codes merged with the blind key, summary, paired tests, per-prompt table, chart, prompts, generation log, coding sheet). The 100 labelled images are in `ai6_all_outputs.zip` (not in the repo, to keep it light).
