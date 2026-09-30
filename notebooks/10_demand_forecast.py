"""AI7 Demand forecast. Question: can a model forecast monthly search demand for men's ethnic wear better than
'same month last year', and what monthly demand shape should the stock and cash plan use for Jul 2027 - Jun 2029?
Data: Google Trends India, weekly, Sep 2021 - Sep 2026 (data/raw/trends). Holdout: last 12 full months (Oct 2025 - Sep 2026).
Models: (1) seasonal naive, (2) Holt-Winters exponential smoothing, (3) SARIMAX with a Diwali-month regressor.
Run from repo root: python notebooks/10_demand_forecast.py"""
import json, warnings, numpy as np, pandas as pd
from pathlib import Path
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
R = Path(__file__).resolve().parents[1]
# Diwali dates (public calendars); the month containing Diwali gets the regressor
DIWALI = {2021:"2021-11-04",2022:"2022-10-24",2023:"2023-11-12",2024:"2024-10-31",2025:"2025-10-20",2026:"2026-11-08",2027:"2027-10-29",2028:"2028-10-17",2029:"2029-11-05"}
def diwali_flag(idx): return pd.Series([1.0 if any(pd.Timestamp(d).to_period("M")==p for d in DIWALI.values()) else 0.0 for p in idx.to_period("M")], index=idx)

def monthly(term):
    d = pd.read_csv(R/f"data/raw/trends/trends_{term}.csv", skiprows=2); d.columns=["week","v"]
    d["week"]=pd.to_datetime(d.week); d["v"]=pd.to_numeric(d.v, errors="coerce")
    m = d.set_index("week").v.resample("MS").mean()
    return m.loc["2021-10-01":"2026-09-01"]          # full months only

def mape(a,f): return float(np.mean(np.abs((a-f)/a))*100)
def mae(a,f): return float(np.mean(np.abs(a-f)))
out = {}
fig, axes = plt.subplots(2,1,figsize=(8,6.4),sharex=False)
for ax,(term,label) in zip(axes,[("kurta_for_men","kurta for men"),("wedding_outfit_for_men","wedding outfit for men")]):
    y = monthly(term); train, test = y.iloc[:-12], y.iloc[-12:]
    fc = {}
    fc["Seasonal naive (same month last year)"] = train.iloc[-12:].values
    hw = ExponentialSmoothing(train, trend="add", damped_trend=True, seasonal="mul", seasonal_periods=12).fit()
    fc["Holt-Winters"] = hw.forecast(12).values
    ex_tr, ex_te = diwali_flag(train.index), diwali_flag(test.index)
    sx = SARIMAX(train, exog=ex_tr, order=(1,0,0), seasonal_order=(0,1,1,12), trend="c").fit(disp=False)
    fc["SARIMAX + Diwali month"] = sx.forecast(12, exog=ex_te).values
    res = {k:{"MAPE_%":round(mape(test.values,v),1),"MAE":round(mae(test.values,v),2)} for k,v in fc.items()}
    best = min(res, key=lambda k: res[k]["MAPE_%"])
    # refit best on all data and forecast Oct 2026 - Jun 2029 (33 months)
    fut = pd.date_range("2026-10-01", periods=33, freq="MS")
    if best.startswith("SARIMAX"):
        m = SARIMAX(y, exog=diwali_flag(y.index), order=(1,0,0), seasonal_order=(0,1,1,12), trend="c").fit(disp=False); f = m.forecast(33, exog=diwali_flag(fut))
    elif best.startswith("Holt"):
        f = ExponentialSmoothing(y, trend="add", damped_trend=True, seasonal="mul", seasonal_periods=12).fit().forecast(33)
    else:
        f = pd.Series(np.tile(y.iloc[-12:].values, 3)[:33], index=fut)
    f = pd.Series(np.clip(np.asarray(f), 0, None), index=fut)
    plan = f.loc["2027-07-01":"2029-06-01"]
    w = (plan / plan.groupby(np.arange(len(plan))//12).transform("sum")).round(4)
    out[term] = {"holdout_Oct2025_Sep2026": res, "best_model": best,
                 "plan_weights_Jul27_Jun29": {d.strftime("%b %y"): float(v) for d,v in w.items()},
                 "peak_month_2027": plan.loc["2027-07-01":"2028-06-01"].idxmax().strftime("%b %Y"),
                 "peak_month_2028": plan.loc["2028-07-01":"2029-06-01"].idxmax().strftime("%b %Y")}
    ax.plot(y.index, y.values, color="#2B2926", lw=1.3, label="Actual (monthly mean)")
    for (k,v),c in zip(fc.items(),["#9DA283","#26324D","#84302A"]): ax.plot(test.index, v, color=c, lw=1.6, ls="--" if k.startswith("Seasonal") else "-", label=f"{k}: MAPE {res[k]['MAPE_%']}%")
    ax.plot(f.index, f.values, color="#1F3A2F", lw=1.6, alpha=.6, label=f"Forecast to Jun 2029 ({best.split(' (')[0]})")
    ax.axvspan(test.index[0], test.index[-1], color="#D9C9A8", alpha=.3)
    ax.set_title(f"'{label}': holdout Oct 2025–Sep 2026 shaded", loc="left", fontsize=11); ax.legend(frameon=False, fontsize=7.5, ncol=2)
    ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig(R/"reports/figures/ai7_demand_forecast.png", dpi=170)
json.dump(out, open(R/"data/clean/ai7_forecast_results.json","w"), indent=1)
print(json.dumps({k:{kk:vv for kk,vv in v.items() if kk!="plan_weights_Jul27_Jun29"} for k,v in out.items()}, indent=1))
