"""AI2 Review complaint map + AI1 test-set preparation.
Question: what do buyers of the leading brands praise and complain about, and where does a fit- and fabric-led brand have room?
Data: 296 Myntra reviews copied by hand (Fabindia 207, Manyavar 86, Tasva 3), 30 Sep 2026. Reviewer names are dropped on load.
Methods: (1) aspect tagging with a transparent keyword lexicon, (2) NMF topic model on TF-IDF (unsupervised ML) as a cross-check.
Run from repo root: python notebooks/02_review_complaint_map.py [raw csv ...]"""
import sys, re, json, numpy as np, pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1]
RAW = R/"data/raw/reviews/reviews_combined.csv"
if len(sys.argv) > 1:   # first run: combine the hand-collected files, dropping reviewer names
    fr = []
    for f in sys.argv[1:]:
        d = pd.read_csv(f); d = d.rename(columns={"review_date_as_provided":"review_date"})
        fr.append(d[["brand","product_name","site","product_url","rating","review_text","review_date"]])
    pd.concat(fr, ignore_index=True).to_csv(RAW, index=False)
d = pd.read_csv(RAW)
n_raw = len(d)
d["review_text"] = d.review_text.fillna("").str.strip()
d = d[d.review_text != ""]
n_text = len(d)
d = d.drop_duplicates(subset=["product_url","review_text","review_date"])
n_dedup = len(d)
d["words"] = d.review_text.str.split().str.len()
HINGLISH = r"\b(ghatiya|raddi|accha|acha|bahut|bekar|bakwas|mast|nahi|hai|kapda|sahi)\b"
d["language"] = np.where(d.review_text.str.lower().str.contains(HINGLISH), "Hinglish", "English")
d["sentiment_from_stars"] = pd.cut(d.rating, [0,2,3,5], labels=["negative","neutral","positive"])
d.insert(0, "review_id", [f"V{i:04d}" for i in range(1, len(d)+1)])
lex = {
 "Fit and size": r"\b(size|sizes|fit|fits|fitting|fitted|tight|loose|long|length|big|small|broad|sleeve|sleeves|xl|xxl|exchange[d]? .*size)\b",
 "Fabric and material": r"\b(fabric|febric|material|meterial|cotton|cloth|texture|linen|lenin|transparent|pure)\b",
 "Comfort and feel": r"\b(comfortable|comfort|comfy|soft|breathable|light|hot|soothing|itch)\b",
 "Quality and durability": r"\b(quality|tear|tearing|torn|stitch|stitching|durable|thread|genuine|wear and tear)\b",
 "Colour and look": r"\b(colou?r|look|looks|design|picture|photo|shade|elegant|beautiful|style|dull)\b",
 "Price and value": r"\b(price|priced|overpriced|worth|money|discount|affordable|expensive)\b",
 "Delivery and returns": r"\b(deliver|delivery|delivered|return|refund|pick up|customer support|late)\b",
 "Bought as a gift": r"\b(dad|father|papa|appa|husband|brother|son|gift|gifted|teacher)\b",
}
for k, pat in lex.items(): d[k] = d.review_text.str.lower().str.contains(pat)
d.to_csv(R/"data/clean/reviews_clean.csv", index=False)

neg = d.rating <= 3
rows = []
for k in lex:
    m = d[k]
    rows.append({"aspect":k, "mentions":int(m.sum()), "share_of_all_reviews":round(m.mean(),3),
                 "share_of_low_rated (1-3 stars)":round(d.loc[neg,k].mean(),3), "share_of_high_rated (4-5 stars)":round(d.loc[~neg,k].mean(),3),
                 "low_rated_share_among_mentions":round(neg[m].mean(),3) if m.sum() else None})
A = pd.DataFrame(rows).sort_values("mentions", ascending=False)
fit = d[d["Fit and size"]].review_text.str.lower()
fit_dir = {"too big / loose / long": int(fit.str.contains(r"\b(big|loose|long|broad)\b").sum()),
           "too small / tight": int(fit.str.contains(r"\b(tight|small)\b").sum()),
           "fits well": int(fit.str.contains(r"(perfect|good|nice|excellent|great|exact|well|true to size|correct)").sum())}
# NMF topics on reviews of 4+ words
long = d[d.words >= 4]
vec = TfidfVectorizer(stop_words="english", min_df=3, ngram_range=(1,2)); X = vec.fit_transform(long.review_text)
nmf = NMF(n_components=5, random_state=42, init="nndsvda", max_iter=500); W = nmf.fit_transform(X); terms = vec.get_feature_names_out()
topics = {f"T{i+1}": {"top_terms":[terms[j] for j in comp.argsort()[-8:][::-1]], "n_reviews":int((W.argmax(1)==i).sum()),
          "mean_rating":round(long.rating[W.argmax(1)==i].mean(),2)} for i,comp in enumerate(nmf.components_)}
out = {"counts":{"raw_rows":n_raw,"with_text":n_text,"after_dedup":n_dedup,"by_brand":d.brand.value_counts().to_dict(),
                 "by_language":d.language.value_counts().to_dict(),"low_rated_1to3":int(neg.sum()),"four_plus_words":int((d.words>=4).sum())},
       "mean_rating_by_brand": d.groupby("brand").rating.mean().round(2).to_dict(),
       "aspects": A.to_dict("records"), "fit_direction": fit_dir, "nmf_topics": topics}
json.dump(out, open(R/"data/clean/ai2_review_results.json","w"), indent=1, ensure_ascii=False)

fig, ax = plt.subplots(figsize=(7.4,3.9))
A2 = A[A.aspect != "Bought as a gift"].sort_values("share_of_all_reviews")
y = np.arange(len(A2))
ax.barh(y+0.18, A2["share_of_high_rated (4-5 stars)"]*100, height=0.36, color="#9DA283", label="in 4–5 star reviews")
ax.barh(y-0.18, A2["share_of_low_rated (1-3 stars)"]*100, height=0.36, color="#84302A", label="in 1–3 star reviews")
ax.set_yticks(y); ax.set_yticklabels(A2.aspect); ax.set_xlabel("% of reviews mentioning the aspect")
ax.set_title(f"Fit and size dominate complaints (n = {len(d)} Myntra reviews)", loc="left", fontsize=11.5)
ax.legend(frameon=False, fontsize=9); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(R/"reports/figures/ai2_complaint_map.png", dpi=180)

# AI1: 120-review test set for hand labelling (text only; star rating hidden)
pool = d[d.words >= 3]
test = pool.groupby("sentiment_from_stars", observed=True, group_keys=False).apply(
    lambda g: g.sample(min(len(g), {"negative":30,"neutral":30,"positive":60}[g.name]), random_state=42))
if len(test) < 120: test = pd.concat([test, pool.drop(test.index).sample(120-len(test), random_state=42)])
test = test.sample(frac=1, random_state=7)[["review_id","brand","review_text"]]
test["your_label (negative / neutral / positive)"] = ""
test.to_csv(R/"ai/eval/sentiment_test_120_TO_LABEL.csv", index=False)
print(json.dumps(out, indent=1, ensure_ascii=False)); print("test set:", len(test))
