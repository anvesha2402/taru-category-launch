# TARU Capstone: what to keep

Final archive of the TARU category-launch capstone, 3 October 2026.
Everything worth keeping is in this folder; anything not here was a duplicate, an old version, or a working file.

## Links

| What | Where |
|---|---|
| Live app (calculator, storefront, AI layer, evidence) | https://taru-category-launch-pqj9ydg5bqruvwrz8mjxch.streamlit.app/ |
| GitHub repository | https://github.com/anvesha2402/taru-category-launch |
| Capstone project document (editable, online) | https://claude.ai/code/artifact/6ffae8b7-6647-4e78-b7cf-4abf9138e367 |
| Project brief (editable, online) | https://claude.ai/code/artifact/8c9045df-5b62-4b68-805b-1f6a70408db9 |
| Brand book (editable, online) | https://claude.ai/code/artifact/d8f335a7-5787-46c1-95e9-ee8e1320303d |

## Folders

| Folder | What it holds | When you need it |
|---|---|---|
| `01_Key_Documents` | Capstone project document, project brief, brand book, research and economics report, regulation brief, interview pack, survey stimuli spec (PDF; Word copies of the first two) | Reading, sharing, interviews. The capstone PDF is the complete version; its Word copy has the text and screenshots but not the drawn diagrams |
| `02_Repository/taru-category-launch` | The final repository, identical to what is deployed: research data, economics model, claims matrix, AI tools and notebooks (07, 08, 09), evaluation results, brand assets, storefront images, Streamlit app, sources register | Re-deploying, editing the app, re-running analysis. Upload this folder to GitHub if the repo ever needs rebuilding |
| `03_AI6_Image_Audit_100_Images` | The 100 AI-generated audit images, prompts, generation log, blind key and the coded sheet | Evidence for the image bias audit (results are in the repo under `ai/eval/ai6/`) |
| `04_PRIVATE_Do_Not_Publish` | Interview transcripts | Keep private. Never upload to GitHub, LinkedIn or any public place |
| `05_Reference_Sources_Regulations` | The rule texts behind the claims guardrail (CCPA, ASCI, GOTS, Legal Metrology, IT Rules, Textiles Committee draft) | Re-building the guardrail's knowledge base. Kept locally; not republished in the repo |

## Where things are inside the repository

| Looking for | Path |
|---|---|
| Survey: raw exports, build script, stimuli images | `data/raw/survey/`, `research/build_taru_survey.gs`, `research/stimuli/` |
| Interview coding (anonymised) | `research/interviews/interview_coding.csv` |
| Sources register (R001–R095), decision log DL-01–DL-10, hypotheses | `research/sources_register/` |
| Later decisions (DL-11 onwards) | `research/survey_change_log.md` |
| Economics model | `model/taru_economics.xlsx` |
| Claims matrix and guardrail pre-screen | `compliance/` |
| AI notebooks | `notebooks/07_claims_guardrail.ipynb`, `08_content_agents.ipynb`, `09_image_bias_audit.ipynb` |
| AI results | `ai/eval/AI4_results.md`, `AI5_results.md`, `AI6_results.md` |
| Brand logos, colour and type sheets, concept images | `brand/` |
| App code | `app/` (run: `pip install -r app/requirements.txt && streamlit run app/app.py`) |

## Safe to delete from your laptop

All the `*_update.zip` files, `stage_*_repo_update.zip`, `TARU_repo_FULL.zip`, `taru_repo_COMPLETE.zip`, `taru-category-launch_FINAL.zip`, `logs.zip`, `survey_images.zip` (same images as `research/stimuli/`), the separate `08_content_agents_run2.ipynb` and `09_image_bias_audit.ipynb` downloads (same as the repo copies), `TARU_Data_Collection.xlsx` (in `data/`), the two register spreadsheets (now in `research/sources_register/`), `sentiment_test_120_TO_LABEL.csv` (that tool was dropped), preview PNGs, error screenshots, and loose regulation PDFs (in folder 05).

Keep the Marketing Management textbook volumes separately: they are not part of this project.
