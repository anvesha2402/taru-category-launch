"""TARU survey analysis: cleaning, exclusions, claim test, Kano, Van Westendorp, routes, channels.
Run from repo root: python notebooks/survey_analysis.py"""
import re, json, numpy as np, pandas as pd
from scipy import stats
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RAW = R/"data/raw/survey"; CLEAN = R/"data/clean"; FIG = R/"reports/figures"
rng = np.random.default_rng(42)

d = pd.concat([pd.read_excel(RAW/f"form_{v}_raw.xlsx") for v in "ABC"], ignore_index=True)
cols = list(d.columns)
ren = {cols[0]:"timestamp",cols[1]:"arm",cols[2]:"consent",cols[3]:"age",cols[4]:"role",cols[5]:"city",cols[6]:"card",
 cols[7]:"B1_occasion",cols[8]:"B2_spend",cols[9]:"B3_where",cols[10]:"B4_decider",cols[11]:"C1",cols[12]:"C2",cols[13]:"C3",
 cols[14]:"attn",cols[15]:"C4_intent",cols[16]:"C5_premium"}
for i,k in enumerate(["ev_tc","ev_bg","ev_ex","ev_te","ev_buy_bg","ev_buy_ex","ce_tc","ce_bg","ce_ex","ce_te","ce_buy_bg","ce_buy_ex"]): ren[cols[17+i]] = k
feats = ["organic","qr","fit","alterations","comfort","styling"]
for i,f in enumerate(feats): ren[cols[29+2*i]] = f"kano_{f}_func"; ren[cols[30+2*i]] = f"kano_{f}_dys"
ren.update({cols[41]:"F1_route",cols[42]:"F2_look1",cols[43]:"F2_look2",cols[44]:"F2_look3",cols[45]:"G1_channels",cols[46]:"G2_online",cols[47]:"G3_sizes",cols[48]:"G4_payment",cols[49]:"H1_income"})
d = d.rename(columns=ren)
d.insert(0,"resp_id",[f"{a}{i:03d}" for a,i in zip(d.arm, d.groupby("arm").cumcount()+1)])

# ---- cleaning ----
def num(x):
    if pd.isna(x): return np.nan
    s = re.sub(r"(inr|rs\.?|₹|,|\s)","",str(x).lower())
    try: return float(s)
    except ValueError: return np.nan
price_cols = ["ev_tc","ev_bg","ev_ex","ev_te","ce_tc","ce_bg","ce_ex","ce_te"]
recoded = 0
for c in price_cols:
    before = d[c].notna().sum(); d[c] = d[c].map(num); recoded += before - d[c].notna().sum()
citymap = {"Mumbai":"Mumbai (incl. Thane, Navi Mumbai)","Bangalore":"Bengaluru","Delhi":"Delhi NCR"}
d["city"] = d["city"].replace(citymap)
lik = {"1 Strongly disagree":1,"2 Disagree":2,"3 Neutral":3,"4 Agree":4,"5 Strongly agree":5}
for c in ["C1","C2","C3","attn"]: d[c+"_n"] = d[c].map(lik)
d["trust"] = d[["C1_n","C2_n","C3_n"]].mean(axis=1, skipna=False)
intent = {"Definitely would":5,"Probably would":4,"Might or might not":3,"Probably not":2,"Definitely not":1}
d["C4_n"] = d["C4_intent"].map(intent)
d["C5_ge10"] = d["C5_premium"].isin(["10–25% more","More than 25% more"]).where(d["C5_premium"].notna())
d["segment"] = d["role"].map({"Both":"both"}).fillna(d["role"].map(lambda r: "self_buyer" if isinstance(r,str) and r.startswith("I'm a man") else ("gifter" if isinstance(r,str) and r.startswith("I bought") else None)))

# ---- exclusions (applied in order, each respondent counted once) ----
rules = [("no_consent", d.consent!="I agree"),
         ("under_18", d.age=="Under 18"),
         ("screened_out_neither_or_blank", d.role.isna() | (d.role=="Neither")),
         ("dropped_before_claim_test", d.trust.isna()),
         ("failed_attention_check", d.attn!="2 Disagree")]
d["excluded"] = ""
log = []
for name, mask in rules:
    m = mask & (d.excluded=="")
    d.loc[m,"excluded"] = name; log.append((name, int(m.sum())))
a = d[d.excluded==""].copy()
log.append(("ANALYSED", len(a)))
d["vw_ev_ok"] = d[["ev_tc","ev_bg","ev_ex","ev_te"]].notna().all(axis=1) & (d.ev_tc<=d.ev_bg)&(d.ev_bg<=d.ev_ex)&(d.ev_ex<=d.ev_te)
d["vw_ce_ok"] = d[["ce_tc","ce_bg","ce_ex","ce_te"]].notna().all(axis=1) & (d.ce_tc<=d.ce_bg)&(d.ce_bg<=d.ce_ex)&(d.ce_ex<=d.ce_te)
a = d[d.excluded==""].copy()
d.to_csv(CLEAN/"survey_clean.csv", index=False)

out = {"exclusions": log, "prices_recoded_to_missing": int(recoded)}
# ---- reliability ----
def alpha(df):
    df = df.dropna(); k = df.shape[1]; return k/(k-1)*(1 - df.var(ddof=1).sum()/df.sum(axis=1).var(ddof=1))
out["cronbach_alpha_trust"] = round(alpha(a[["C1_n","C2_n","C3_n"]]),3)

# ---- claim test ----
def boot_d(x, y, n=5000):
    def cd(x,y):
        sp = np.sqrt(((len(x)-1)*x.var(ddof=1)+(len(y)-1)*y.var(ddof=1))/(len(x)+len(y)-2)); return (x.mean()-y.mean())/sp
    bs = [cd(rng.choice(x,len(x)), rng.choice(y,len(y))) for _ in range(n)]
    return cd(x,y), np.percentile(bs,2.5), np.percentile(bs,97.5)
arms = {k: a[a.arm==k] for k in "ABC"}
out["claim_by_arm"] = {k:{"n":len(v),"trust_mean":round(v.trust.mean(),2),"trust_sd":round(v.trust.std(),2),
    "intent_top2":round((v.C4_n>=4).mean(),2),"premium_ge10":round(v.C5_ge10.mean(),2)} for k,v in arms.items()}
out["kruskal_trust"] = [round(x,4) for x in stats.kruskal(*[v.trust for v in arms.values()])]
out["pairwise_trust_d"] = {f"{p}-{q}":[round(x,2) for x in boot_d(arms[p].trust.values, arms[q].trust.values)] for p,q in [("B","A"),("C","B"),("C","A")]}
# power: n per arm to detect d=0.5 at 80% power, alpha .05 two-sided
out["n_per_arm_needed_for_d0.5"] = 64

# ---- Kano ----
K = {"I'd like it":"L","I'd expect it":"M","I'm neutral":"N","I can live with it":"W","I'd dislike it":"D"}
table = {"L":{"L":"Q","M":"A","N":"A","W":"A","D":"O"},"M":{"L":"R","M":"I","N":"I","W":"I","D":"M"},
         "N":{"L":"R","M":"I","N":"I","W":"I","D":"M"},"W":{"L":"R","M":"I","N":"I","W":"I","D":"M"},
         "D":{"L":"R","M":"R","N":"R","W":"R","D":"Q"}}
names = {"A":"Attractive","O":"Performance","M":"Must-be","I":"Indifferent","R":"Reverse","Q":"Questionable"}
kano = {}
for f in feats:
    fu = a[f"kano_{f}_func"].map(K); dy = a[f"kano_{f}_dys"].map(K)
    cl = [table[x][y] for x,y in zip(fu,dy) if isinstance(x,str) and isinstance(y,str)]
    s = pd.Series(cl).value_counts()
    A_,O_,M_,I_ = [s.get(k,0) for k in "AOMI"]; tot = A_+O_+M_+I_
    kano[f] = {"n":len(cl), "counts":{names[k]:int(v) for k,v in s.items()}, "category":names[s.index[0]] if len(s) else None,
               "better":round((A_+O_)/tot,2) if tot else None, "worse":round(-(O_+M_)/tot,2) if tot else None,
               "reverse_or_questionable_share":round((s.get("R",0)+s.get("Q",0))/len(cl),2) if cl else None}
out["kano"] = kano

# ---- Van Westendorp ----
def vw(df, p):
    df = df[df[f"vw_{p}_ok"]]
    grid = np.arange(200, 30001, 50)
    tc = np.array([(df[f"{p}_tc"]>=g).mean() for g in grid]); bg = np.array([(df[f"{p}_bg"]>=g).mean() for g in grid])
    ex = np.array([(df[f"{p}_ex"]<=g).mean() for g in grid]); te = np.array([(df[f"{p}_te"]<=g).mean() for g in grid])
    cross = lambda u,v: int(grid[np.argmin(np.abs(u-v))])
    return {"n":len(df),"PMC":cross(tc,1-bg),"OPP":cross(tc,te),"IPP":cross(bg,ex),"PME":cross(te,1-ex),
            "median_bargain":float(df[f"{p}_bg"].median()),"median_expensive":float(df[f"{p}_ex"].median())}, (grid,tc,bg,ex,te)
out["vw_everyday"], ev_curves = vw(a,"ev"); out["vw_ceremonial"], ce_curves = vw(a,"ce")
out["vw_order_violations"] = {"everyday":int((~a.vw_ev_ok).sum()),"ceremonial":int((~a.vw_ce_ok).sum())}
# NMS sanity check: purchase likelihood should fall from bargain to expensive price
e = a.dropna(subset=["ev_buy_bg","ev_buy_ex"])
out["nms_check_everyday"] = {"n":len(e),"mean_likelihood_at_bargain":round(e.ev_buy_bg.map(intent).mean(),2),
    "mean_likelihood_at_expensive":round(e.ev_buy_ex.map(intent).mean(),2),
    "share_more_likely_at_higher_price":round((e.ev_buy_ex.map(intent)>e.ev_buy_bg.map(intent)).mean(),2)}

# ---- routes, segments, channels ----
def wilson(k,n,z=1.96):
    p=k/n; c=(p+z*z/(2*n))/(1+z*z/n); h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n); return [round(c-h,2),round(c+h,2)]
rc = a.F1_route.value_counts(); nr = rc.sum()
out["routes"] = {k:{"n":int(v),"share":round(v/nr,2),"ci95":wilson(v,nr)} for k,v in rc.items()}
out["segments"] = {s:{"n":int(len(g)),"premium_ge10":round(g.C5_ge10.mean(),2),"trust_mean":round(g.trust.mean(),2)} for s,g in a.groupby("segment")}
ch = a.G1_channels.dropna().str.replace("(e.g. Myntra, Amazon)","(e.g. Myntra/Amazon)", regex=False).str.split(", ").explode().str.strip()
out["channels_ticked"] = ch.value_counts().to_dict(); out["channels_base"] = int(a.G1_channels.notna().sum())
out["online_comfort_mean_1to5"] = round(a.G2_online.mean(),2)
out["cod_share"] = round((a.G4_payment=="Pay on delivery").mean(),2)
out["sizes_ordered"] = a.G3_sizes.value_counts().to_dict()
out["occasion"] = a.B1_occasion.value_counts().to_dict(); out["spend"] = a.B2_spend.value_counts().to_dict()
out["f2_words"] = {k: a[k].value_counts().head(5).to_dict() for k in ["F2_look1","F2_look2","F2_look3"]}
json.dump(out, open(CLEAN/"survey_results.json","w"), indent=1, default=int, ensure_ascii=False)

# ---- figures ----
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.spines.top":False,"axes.spines.right":False})
INK="#2B2926"; HW="#1F3A2F"; GR="#9DA283"
fig,ax = plt.subplots(figsize=(7,3.6))
lab = {"A":"A · natural fibres","B":"B · GOTS + licence","C":"C · GOTS + comfort + QR"}
for i,k in enumerate("ABC"):
    v = arms[k].trust; m=v.mean(); se=v.std()/np.sqrt(len(v))
    ax.errorbar(m, i, xerr=1.96*se, fmt="o", color=HW if k!="A" else INK, capsize=4, ms=8)
    ax.text(m, i+0.28, f"{m:.2f}  (n={len(v)})", ha="center", fontsize=10, color=INK)
ax.set_yticks(range(3)); ax.set_yticklabels([lab[k] for k in "ABC"]); ax.set_xlim(1,5); ax.set_ylim(-0.6,2.7)
ax.set_xlabel("Trust index (mean of C1–C3, 1–5), with 95% CI"); ax.set_title("Trust by claim card: no reliable difference between cards", loc="left", fontsize=12)
fig.tight_layout(); fig.savefig(FIG/"claim_test_trust.png", dpi=180)
for tag,(grid,tc,bg,ex,te),res in [("everyday",ev_curves,out["vw_everyday"]),("ceremonial",ce_curves,out["vw_ceremonial"])]:
    fig,ax = plt.subplots(figsize=(7,3.8))
    for y,l,s in [(tc,"Too cheap","--"),(bg,"Bargain",":"),(ex,"Expensive","-."),(te,"Too expensive","-")]: ax.plot(grid,y,s,label=l,color=HW if "cheap" in l.lower() or l=="Bargain" else INK)
    ax.axvspan(res["PMC"],res["PME"],color=GR,alpha=.18,label="Acceptable range")
    ax.set_xlim(0, np.percentile(a[f"{tag[:2]}_te"].dropna(),95)*1.1); ax.set_xlabel("Price (₹)"); ax.set_ylabel("Share of respondents")
    ax.set_title(f"{tag.capitalize()} set: acceptable ₹{res['PMC']:,}–₹{res['PME']:,}, optimal ₹{res['OPP']:,} (n={res['n']})", loc="left", fontsize=12)
    ax.legend(frameon=False, fontsize=9, ncol=3); fig.tight_layout(); fig.savefig(FIG/f"vw_{tag}.png", dpi=180)
print(json.dumps(out, indent=1, default=int, ensure_ascii=False))
