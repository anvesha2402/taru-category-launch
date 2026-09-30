"""Price audit + Google Trends seasonality and geography. Run from repo root."""
import json, numpy as np, pandas as pd
from pathlib import Path
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1]; FIG = R/"reports/figures"; out = {}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.spines.top":False,"axes.spines.right":False})
HW, INK, GR, MD = "#1F3A2F", "#2B2926", "#9DA283", "#84302A"

# ---- price audit ----
p = pd.read_csv(R/"data/raw/price_audit/price_audit.csv")
p["discount"] = 1 - p.selling_price_inr / p.mrp_inr
f = p.fabric_composition.str.lower()
p["natural_only"] = ~f.str.contains("viscose|georgette|art silk|not shown|brocade") 
sets = p[p.brand != "Isha Life"]
out["price_by_brand"] = sets.groupby("brand").agg(n=("sku_id","count"), mrp_median=("mrp_inr","median"),
    sell_median=("selling_price_inr","median"), sell_min=("selling_price_inr","min"), sell_max=("selling_price_inr","max"),
    avg_discount=("discount","mean"), natural_fibre_share=("natural_only","mean")).round(2).to_dict("index")
out["price_by_line"] = sets.groupby("line").selling_price_inr.describe()[["count","min","50%","max"]].round(0).to_dict("index")
out["certified_organic_claims_in_sets"] = int((sets.certification_claim != "none").sum())
out["manyavar_everyday_natural_price"] = float(sets[(sets.brand=="Manyavar")&(sets.line=="everyday")].selling_price_inr.median())

fig, ax = plt.subplots(figsize=(7.2,3.8))
for b, c, m in [("Manyavar", HW, "o"), ("Sojanya", MD, "s")]:
    s = sets[sets.brand == b]
    ax.scatter(s.selling_price_inr, s.line.map({"everyday":0,"festive":1,"ceremonial":2}) + np.where(s.natural_only, 0.12, -0.12),
               c=c, marker=m, s=46, label=f"{b} (filled = natural fibre only)", facecolors=np.where(s.natural_only, c, "none"), edgecolors=c)
ax.axvline(750, color=GR, ls="--"); ax.text(820, 0.45, "Isha Life\norganic kurta\n₹750", fontsize=8.5, color=INK)
ax.set_yticks([0,1,2]); ax.set_yticklabels(["Everyday","Festive","Ceremonial"]); ax.set_xlabel("Selling price (₹), 30 Sep 2026")
ax.set_title("No priced set carries an organic claim; Manyavar leans on viscose", loc="left", fontsize=12)
ax.legend(frameon=False, fontsize=8.5, loc="lower right"); fig.tight_layout(); fig.savefig(FIG/"price_audit.png", dpi=180)

# ---- trends ----
terms = ["kurta_for_men","sherwani","linen_kurta","organic_cotton","wedding_outfit_for_men"]
T = {}
for t in terms:
    d = pd.read_csv(R/f"data/raw/trends/trends_{t}.csv", skiprows=2); d.columns = ["week","v"]
    d["week"] = pd.to_datetime(d.week); d["v"] = pd.to_numeric(d.v, errors="coerce"); T[t] = d
seas = {}
for t, d in T.items():
    m = d.assign(y=d.week.dt.year, mo=d.week.dt.month).groupby(["y","mo"]).v.mean().reset_index()
    m["idx"] = m.v / m.groupby("y").v.transform("mean") * 100   # each year's own mean = 100
    seas[t] = m[(m.y >= 2022) & (m.y <= 2025)].groupby("mo").idx.mean().round(0)
S = pd.DataFrame(seas); S.index = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
out["seasonal_index_2022_2025"] = S.astype(int).to_dict()
out["peak_months"] = {t: S[t].nlargest(3).index.tolist() for t in terms}
out["trough_months"] = {t: S[t].nsmallest(2).index.tolist() for t in terms}
oc = T["organic_cotton"]; out["organic_cotton_feb_2026_spike"] = int(oc[(oc.week >= "2026-02-01") & (oc.week <= "2026-02-28")].v.max())
yr = {t: T[t].assign(y=T[t].week.dt.year).groupby("y").v.mean().round(1).to_dict() for t in terms}; out["annual_mean"] = yr
geo = {}
for t in terms:
    g = pd.read_csv(R/f"data/raw/trends/geo_{t}.csv", skiprows=2); g.columns = ["region","v"]
    geo[t] = g.set_index("region").v
G = pd.DataFrame(geo).loc[["Delhi","Maharashtra","Karnataka","Telangana","Haryana","Tamil Nadu","Goa","Gujarat"]]
out["geo_launch_states"] = G.fillna(0).astype(int).to_dict("index")

fig, ax = plt.subplots(figsize=(7.2,3.8))
for t, c, lw in [("kurta_for_men", HW, 2.2), ("wedding_outfit_for_men", MD, 1.6), ("sherwani", INK, 1.2), ("linen_kurta", GR, 1.6)]:
    ax.plot(range(12), S[t], color=c, lw=lw, label=t.replace("_"," "))
ax.axhline(100, color="#ccc", lw=.8); ax.set_xticks(range(12)); ax.set_xticklabels(S.index)
ax.set_ylabel("Seasonal index (year mean = 100)"); ax.axvspan(8.6, 10.4, color=GR, alpha=.15)
ax.set_title("Kurta search peaks in Oct; wedding wear peaks Nov, with a second rise Jan–Apr", loc="left", fontsize=12)
ax.legend(frameon=False, fontsize=9, ncol=2); fig.tight_layout(); fig.savefig(FIG/"trends_seasonality.png", dpi=180)
json.dump(out, open(R/"data/clean/desk_results.json","w"), indent=1, default=str, ensure_ascii=False)
print(json.dumps(out, indent=1, default=str, ensure_ascii=False))
