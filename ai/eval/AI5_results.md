# AI5 Launch Content Agents: results

**Model:** Qwen2.5-7B-Instruct (open-weight, 4-bit, Colab T4) in every role: brief, copywriter, guardrail, critic. **Outputs:** 21 (12 social posts, 6 product descriptions, 3 emails). **Human rater:** the author, scoring blind to the critic's scores. **Runs:** run 1 = pipeline v1 (2 Oct 2026); run 2 = pipeline v2 (DL-18).

## 1. Headline: both pass tests failed

| Pass test (from the brief) | Target | Run 1 | Run 2 | Met? |
|---|---|---|---|---|
| Outputs passing the checks within 2 revisions | ≥ 90% | 10% (2/21) | **67% (14/21)** | No |
| Outputs the author scored ≥ 4 of 5 for brand voice | ≥ 80% | not scored | **38% (8/21)** | No |
| LLM judge vs author agreement (reported) | — | — | exact 19%, within 1 point 48%, weighted κ 0.22 | — |

Author decisions on run 2: **2 approve, 12 edit, 7 reject.** Mean revisions 1.43. Run time 39 minutes for 21 outputs on a free T4.

## 2. What the v2 changes did
Code-level formatting fixes and approved-claim pass-through raised the check pass rate from 10% to 67%. They removed the failures caused by exclamation marks, hashtags and the guardrail rejecting D7's own wording. They did not make the copy good.

## 3. Passing the checks does not mean the copy is good

| | Author ≥ 4 | Author ≤ 3 |
|---|---|---|
| Passed checks (14) | 7 | 7 |
| Failed checks (7) | 1 | 6 |

The checks catch rule breaks; they do not judge voice. Half the outputs that passed were still rated "needs rework" or worse.

## 4. Failure patterns in the run-2 copy (counted from the 21 outputs)

| Pattern | Outputs | Example | Caught by checks? |
|---|---|---|---|
| Sales openers and calls to action ("Shop now", "Elevate", "Discover", "Experience") | 17 of 21 | CR09 "Elevate your corporate gifting…" | No: not on the avoid list |
| **Placeholder filled with an invented figure** | 3 (CR09, CR16, CR18) | "made with 95% organic cotton"; "Our goal: 95%…" | **No.** CR09 passed. The most serious failure: an unverifiable number written as fact |
| Claim stacking (4–5 approved claims in one piece), including "organic cotton" and "made with [X]% organic" together, which describe two different GOTS grades | 3 (CR01, CR06, CR13) | CR01 lists five claims in a row | No |
| Avoid-list stem missed: "sustainability" | 1 (CR05) | "Give the gift of sustainability this Diwali" | **No.** The list had "sustainable", not the stem. Code gap |
| Hashtag words left behind after the # was removed | 3 (CR01, CR05, CR10) | "KnowWhatYouWear DiwaliGift" | Partly: CR10 failed on them |
| "X" placeholder losing its brackets | 1 (CR12) | "licence no. X" | No |

The author's 12 edits cut the copy by 24% (512 → 388 words). They mostly removed the sales opener and extra claims, and replaced the ending with a factual next step ("See the size guide", "Book a fitting").

## 5. The critic cannot replace the author
The critic scored 15 of 21 outputs at 5; the author gave two 5s. On average it rated each output **1.6 points higher** than the author. It gave 5 to drafts the author rejected (CR07, CR09, CR20). Weighted κ = 0.22 is "fair" agreement at best. Calibration instructions added in v2 ("give 5 only if publishable unchanged") did not fix this. Likely cause: the same model writes and judges its own text (self-preference). Implication: the critic is not fit to screen copy, and **autonomy level 2 (agents draft; a person approves every public line) is the correct setting.**

## 6. Business-case input
Usable with minor edits (author approve, or edit with score ≥ 4): **8 of 21 (38%)**. That is the automation share for the content business case, not the 90% the brief hoped for. The other 62% needed rework or rejection, and three outputs contained invented figures. The cost of review time must be counted against the drafting time saved.

## 7. What a v3 would change (not run)
1. Detect any number in the output that is not in the brief or the approved claims (catches filled placeholders).
2. Match avoid-list words by stem (sustainab*, perfect*); add sales openers ("Shop now", "Elevate", "Discover", "Experience") to the list.
3. Delete hashtag tokens rather than keep the words.
4. Cap approved claims at two per piece; never pair the "organic" and "made with" grades.
5. Use a different model as critic, or give it few-shot examples scored by the author.

A v3 tuned on these 21 outputs would need a **fresh** set of requests to be tested fairly; re-running on the same 21 would overfit to them.

## 8. Limitations
- One rater (the author). No second rater, so the human scores' own reliability is unknown.
- 21 outputs; one output moves a percentage by about 5 points.
- One small open model (7B, 4-bit) in every role. A larger model would likely follow negative rules better; not tested.
- Pipeline v2 was changed after run 1's results (DL-18). Both runs are reported.
- The competitor copy check used product titles only (DL-17). Maximum similarity 0.79, below the 0.9 flag threshold; this check is weak.
