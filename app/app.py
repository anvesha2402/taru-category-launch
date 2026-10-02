"""TARU Premium and Channel Calculator (deliverable D9). Run: streamlit run app/app.py"""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import ai_layer
import storefront
import taru_model as m

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
REPO_URL = "https://github.com/anvesha2402/taru-category-launch"
HW, MADDER, INK = "#1F3A2F", "#84302A", "#2B2926"

st.set_page_config(page_title="TARU Premium and Channel Calculator", page_icon="◎", layout="wide")


def inr(x: float, dec: int = 0) -> str:
    """Indian digit grouping: 12,34,567."""
    neg = x < 0
    s = f"{abs(x):.{dec}f}"
    whole, _, frac = s.partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while len(head) > 2:
            groups.insert(0, head[-2:]); head = head[:-2]
        if head:
            groups.insert(0, head)
        whole = ",".join(groups + [tail])
    return ("−" if neg else "") + "₹" + whole + (f".{frac}" if frac else "")


st.title("TARU Premium and Channel Calculator")
st.caption("TARU is a fictional brand created for an independent student portfolio project. Market, competitor and regulatory facts "
           "come from public sources as cited. Consumer findings come from the author's own research with a convenience sample. "
           "Costs, targets and financial projections are illustrative assumptions.")

tab_calc, tab_shop, tab_ai, tab_ev, tab_about = st.tabs(["Calculator", "Storefront (mock-up)", "AI layer", "Evidence", "About and disclaimer"])

# =============================================================================
# Calculator
# =============================================================================
with tab_calc:
    preset_label = st.radio("Start from", ["Plan as briefed: four channels, full team", "Recommended pivot: no marketplace, lean team"],
                            horizontal=True, help="Loads every input below from that scenario. You can then change anything.")
    preset = "pivot" if preset_label.startswith("Recommended") else "briefed"
    d = m.params(preset)          # defaults for this preset
    p = m.params(preset)          # working copy the widgets write into
    k = lambda name: f"{preset}:{name}"   # widget keys per preset, so switching preset reloads its defaults

    left, right = st.columns([1, 2], gap="large")
    with left:
        st.subheader("Inputs")
        line = st.selectbox("Line and tier", m.LINES, key=k("line"))
        L, Ld = p["line"][line], d["line"][line]
        L["price"] = st.number_input(f"Retail price, {line} (₹, incl. GST)", 500, 50000, int(Ld["price"]), 100, key=k(f"price_{line}"),
                                     help="GST is 5% at or below ₹2,500 per set and 18% above (applied per set, as in the spreadsheet).")
        L["fab_rate"] = st.number_input(f"Certified-organic fabric cost, {line} (₹ per metre)", 50, 2000, int(Ld["fab_rate"]), 10,
                                        key=k(f"fab_{line}"), help=f"{Ld['fab_m']} m per set. Source: IndiaMART GOTS listings ₹110–350/m (30 Sep 2026); "
                                        "festive and ceremonial linen or handloom premium is an assumption.")
        L["cmt"] = st.number_input(f"Cut-make-trim (stitching), {line} (₹ per set)", 100, 5000, int(Ld["cmt"]), 50, key=k(f"cmt_{line}"),
                                   help="IndiaMART kurta-pyjama job work ₹300–700 per set; ceremonial includes the jacket (assumption).")
        # keep the other lines' edits when switching the line shown
        for other in m.LINES:
            if other != line:
                for fld, key in (("price", "price"), ("fab_rate", "fab"), ("cmt", "cmt")):
                    v = st.session_state.get(k(f"{key}_{other}"))
                    if v is not None:
                        p["line"][other][fld] = v

        st.markdown("**Channel mix** (share of sets sold; rescaled to 100%)")
        for ch in m.CHANNELS:
            p["channel"][ch]["mix"] = st.slider(ch, 0, 100, int(round(d["channel"][ch]["mix"] * 100)), 5, key=k(f"mix_{ch}")) / 100
        cm = m.channel_mix(p)
        if sum(p["channel"][c]["mix"] for c in m.CHANNELS) == 0:
            st.error("Set at least one channel above 0%.")

        with st.expander("Own website (D2C)", expanded=True):
            D2 = p["channel"]["D2C website"]; D2d = d["channel"]["D2C website"]
            D2["acq"] = st.number_input("Customer acquisition cost, CAC (₹ per set)", 0, 5000, int(D2d["acq"]), 50, key=k("cac"),
                                        help="Assumption: paid social. Other channels' acquisition costs are under 'Other channel costs'.")
            D2["ret"] = st.slider("Return rate (%)", 0, 60, int(D2d["ret"] * 100), 1, key=k("ret")) / 100
            D2["cod"] = st.slider("Cash-on-delivery share of orders (%)", 0, 100, int(D2d["cod"] * 100), 1, key=k("cod"),
                                  help="Survey G4: 64% (direction only; small pilot survey).") / 100
            D2["rto"] = st.slider("Return-to-origin rate on COD orders (%)", 0, 60, int(D2d["rto"] * 100), 1, key=k("rto"),
                                  help="Register R064: RTO peaks around 39%; 20% assumed for an average month.") / 100
        with st.expander("Retail partner (sale or return)"):
            RP = p["channel"]["Retail partner"]; RPd = d["channel"]["Retail partner"]
            st.caption("Not in the spreadsheet; off unless you give it a share above. All values are assumptions.")
            RP["retailer_margin"] = st.slider("Retailer margin (% of net price)", 0, 60, int(RPd["retailer_margin"] * 100), 1, key=k("rmargin")) / 100
            RP["sor"] = st.slider("Sale-or-return: share of stock sent back unsold (%)", 0, 80, int(RPd["sor"] * 100), 5, key=k("sor")) / 100
        with st.expander("Other channel costs"):
            MP = p["channel"]["Marketplace"]
            MP["comm"] = st.slider("Marketplace commission (%)", 0.0, 40.0, d["channel"]["Marketplace"]["comm"] * 100, 0.5, key=k("comm"),
                                   help="Register R069: Myntra 25–30% (press estimate, low confidence).") / 100
            for ch in ["Marketplace", "Pop-up", "Corporate gifting", "Retail partner"]:
                p["channel"][ch]["acq"] = st.number_input(f"Acquisition or venue cost, {ch} (₹ per set)", 0, 5000,
                                                          int(d["channel"][ch]["acq"]), 25, key=k(f"acq_{ch}"))
        st.markdown("**Fixed-cost base** (for break-even)")
        p["fixed_m"] = st.number_input("Fixed overheads per month (₹)", 0, 2_000_000, int(d["fixed_m"]), 5000, key=k("fixed"))
        p["mkt_m"] = st.number_input("Brand content and PR per month (₹)", 0, 1_000_000, int(d["mkt_m"]), 5000, key=k("mkt"))

    with right:
        b = m.blended(p)
        be = m.breakeven_sets_per_month(p)
        prem = m.premium_vs_manyavar(line, p)
        vw_status, vw_msg = m.vw_check(line, p)

        c1, c2, c3 = st.columns(3)
        c1.metric("Blended contribution per set", inr(b["contribution"]))
        c1.caption(f"{b['contribution_pct']:.1%} of net revenue, across your line and channel mix")
        c2.metric("Break-even sets per month", "never" if be is None else f"{be:,.0f}")
        c2.caption(f"The plan's year-2 average is {p['year2_sets_per_month']} sets a month")
        c3.metric(f"{line} premium vs Manyavar", f"{prem:+.0%}")
        c3.caption(f"Manyavar median {inr(m.MANYAVAR_MEDIAN[line])} for a comparable {line.lower()} set (price audit, 30 Sep 2026)")
        if be is None:
            st.error("Contribution per set is zero or negative: TARU loses money on every set before overheads, so no volume breaks even.")
        if vw_status == "outside":
            st.warning(f"Price warning: {inr(L['price'])} for the {line} set. {vw_msg} The survey is a pilot (direction only).")
        elif vw_status == "ok":
            st.info(f"{inr(L['price'])}: {vw_msg} The survey is a pilot (direction only).")
        else:
            st.info(vw_msg)

        # ---- contribution by channel for the selected line
        rows = [{"Channel": ch, "Contribution per set (₹)": m.contribution(line, ch, p), "Share of sets": cm[ch]} for ch in m.CHANNELS]
        df = pd.DataFrame(rows)
        df["Channel"] = [f"{c} ({cm[c]:.0%} of sets)" for c in m.CHANNELS]
        lo_v, hi_v = df["Contribution per set (₹)"].min(), df["Contribution per set (₹)"].max()
        span = max(hi_v, 0) - min(lo_v, 0) or 1
        xdom = [min(lo_v, 0) - 0.18 * span, max(hi_v, 0) + 0.18 * span]
        df["Result"] = df["Contribution per set (₹)"].map(lambda v: "Profit" if v >= 0 else "Loss")
        df["label"] = df["Contribution per set (₹)"].map(inr)
        st.subheader(f"{line} set: contribution per set, by channel")
        base = alt.Chart(df).encode(
            y=alt.Y("Channel:N", sort=list(df["Channel"]), title=None, scale=alt.Scale(paddingInner=0.35), axis=alt.Axis(labelLimit=260)),
            x=alt.X("Contribution per set (₹):Q", title="Contribution per set sold (₹)", scale=alt.Scale(domain=xdom, nice=False)),
            tooltip=["Channel", alt.Tooltip("label:N", title="Contribution per set"), alt.Tooltip("Share of sets:Q", format=".0%", title="Share of sets")])
        bars = base.mark_bar(cornerRadiusEnd=4).encode(
            color=alt.Color("Result:N", scale=alt.Scale(domain=["Profit", "Loss"], range=[HW, MADDER]), legend=alt.Legend(title=None, orient="top")))
        pos = base.transform_filter("datum['Contribution per set (₹)'] >= 0").mark_text(align="left", dx=6, color=INK).encode(text="label:N")
        neg = base.transform_filter("datum['Contribution per set (₹)'] < 0").mark_text(align="right", dx=-6, color=INK).encode(text="label:N")
        rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=INK, strokeWidth=1).encode(x="x:Q")
        st.altair_chart((bars + pos + neg + rule).properties(height=240), use_container_width=True)
        st.caption("Each bar: what one set sold through that channel leaves after product, channel and acquisition costs, before fixed overheads.")

        # ---- waterfall for one channel
        ch_w = st.selectbox("Show the cost waterfall for", m.CHANNELS, key=k("wf_channel"))
        steps = [s for s in m.waterfall(line, ch_w, p) if abs(s[1]) > 0.005]
        wf, run = [], 0.0
        for name, v in steps:
            wf.append({"Step": name, "start": run, "end": run + v, "value": v, "Type": "Revenue" if v > 0 else "Cost"})
            run += v
        wf.append({"Step": "Contribution", "start": 0, "end": run, "value": run, "Type": "Contribution" if run >= 0 else "Loss"})
        wdf = pd.DataFrame(wf)
        wdf["order"] = range(len(wdf)); wdf["label"] = wdf["value"].map(inr)
        wdf["lo"] = wdf[["start", "end"]].min(axis=1); wdf["hi"] = wdf[["start", "end"]].max(axis=1)
        wbase = alt.Chart(wdf).encode(y=alt.Y("Step:N", sort=list(wdf["Step"]), title=None, scale=alt.Scale(paddingInner=0.3), axis=alt.Axis(labelLimit=260)))
        wbars = wbase.mark_bar(cornerRadius=2).encode(
            x=alt.X("lo:Q", title="₹ per set", scale=alt.Scale(domain=[min(0, wdf["lo"].min()), wdf["hi"].max() * 1.15], nice=False)), x2="hi:Q",
            color=alt.Color("Type:N", scale=alt.Scale(domain=["Revenue", "Cost", "Contribution", "Loss"], range=[HW, MADDER, "#C8912F", "#5A1F1B"]),
                            legend=alt.Legend(title=None, orient="top")),
            tooltip=["Step", alt.Tooltip("label:N", title="₹ per set")])
        wtext = wbase.mark_text(align="left", dx=6, color=INK, fontSize=11).encode(x="hi:Q", text="label:N")
        st.altair_chart((wbars + wtext).properties(height=34 * len(wdf) + 40), use_container_width=True)
        st.caption("Read top to bottom: the net price, minus each cost, leaves the contribution in the last bar.")

        # ---- full table
        with st.expander("Contribution per set for every line and channel"):
            tbl = pd.DataFrame({ch: [m.contribution(l, ch, p) for l in m.LINES] for ch in m.CHANNELS}, index=m.LINES)
            st.dataframe(tbl.map(inr), use_container_width=True)
            st.caption(f"Blended across the line mix (Everyday {m.line_mix(p)['Everyday']:.0%}, Festive {m.line_mix(p)['Festive']:.0%}, "
                       f"Ceremonial {m.line_mix(p)['Ceremonial']:.0%}) and your channel mix: net revenue {inr(b['revenue'])}, "
                       f"COGS {inr(-b['cogs'])}, channel and acquisition costs {inr(-b['channel_costs'])}, contribution {inr(b['contribution'])} per set.")
        st.caption("Contribution = net revenue ex-GST − product cost − commission, fees, shipping, returns, COD return-to-origin and acquisition. "
                   "Break-even = (fixed overheads + brand content) ÷ blended contribution per set. Same formulas as model/taru_economics.xlsx; "
                   "the defaults reproduce it exactly (tested in app/tests/test_model.py). Launch spend, stock timing and cash are in the spreadsheet only.")

# =============================================================================
# Storefront mock-up
# =============================================================================
with tab_shop:
    st.markdown("A design mock-up of TARU's website in the brand identity (brand book sections 3 and 5.2). **Nothing here is for sale**: "
                "buttons do nothing and there is no checkout. Every line of copy is an approved claim from the claims matrix (D7) or "
                "a content-agent draft the author edited and approved (AI5). Images are AI-generated concept images, each labelled; they are not photographs of a real garment.")
    notes = st.toggle("Show where each line of copy comes from", value=False)
    components.html(storefront.render(show_notes=notes), height=1800, scrolling=True)

# =============================================================================
# AI layer
# =============================================================================
with tab_ai:
    st.markdown("How the five AI tools in this project fit into the launch, what each one does, and what its test found. "
                "Full results: `ai/eval/` in the repository.")
    components.html(ai_layer.render(), height=2850, scrolling=True)

# =============================================================================
# Evidence
# =============================================================================
with tab_ev:
    st.markdown("The research behind the defaults, with an honest status for each source. Full detail: "
                "`reports/TARU_Research_Economics_Recommendation.pdf` in the repository.")
    sr = json.loads((ROOT / "data" / "clean" / "survey_results.json").read_text())

    def fig(name, caption):
        f = FIG / name
        if f.exists():
            st.image(str(f), caption=caption, width=760)

    st.subheader("Claim test (survey)")
    st.warning("Status: inconclusive, not used for decisions. The pilot sample was too small: 47 usable responses (13–20 per card; 64 needed "
               "per card). The answers were also inconsistent on standard quality checks (trust items α = −0.13; 79% more likely "
               "to buy at the 'expensive' price; 40% of price answers out of order). Shown for transparency only. "
               "The question it was meant to answer is still open: a larger survey would be needed.")
    fig("claim_test_trust.png", "Mean trust by claim card (n = 20 / 14 / 13). Kruskal-Wallis p = 0.71; every effect-size interval spans zero.")

    st.subheader("Kano (survey)")
    st.warning("Status: inconclusive (same pilot survey). All six features classify as Indifferent, which more likely reflects the small, "
               "inconsistent sample than real indifference.")
    kano = pd.DataFrame([{"Feature": f, "Category": v["category"], "Better": v["better"], "Worse": v["worse"], "n": v["n"],
                          "Reverse or questionable": f"{v['reverse_or_questionable_share']:.0%}"} for f, v in sr["kano"].items()])
    kano["Feature"] = kano["Feature"].map({"organic": "Certified organic", "qr": "QR trail", "fit": "Fuller-build cut",
                                           "alterations": "Free alterations", "comfort": "Comfort guarantee", "styling": "Styling help"})
    st.dataframe(kano, hide_index=True, use_container_width=True)

    st.subheader("Acceptable price range (Van Westendorp)")
    st.warning("Status: direction only. Order-consistent answers only (n = 28 everyday, 32 ceremonial). These ranges agree with the interviews, "
               "the one place survey and interviews line up. The calculator's price warning uses them.")
    a, b2 = st.columns(2)
    with a:
        fig("vw_everyday.png", "Everyday set: acceptable ₹1,250–3,800")
    with b2:
        fig("vw_ceremonial.png", "Ceremonial set: acceptable ₹4,800–11,250")

    st.subheader("Competitor prices (price audit)")
    st.warning("Status: direction only. 30 sets on 30 Sep 2026; only Manyavar and Sojanya pages could be read in full.")
    fig("price_audit.png", "Price audit by brand and line")

    st.subheader("Interviews")
    st.warning("Status: direction only. 9 buyers and 2 partners, convenience sample. Fit, price and proof gave usable direction; "
               "4 of 9 buyers leaned towards the certification tag as the proof they would trust.")

    st.subheader("What buyers complain about (AI2, review mining)")
    st.warning("Status: direction only. 287 public reviews, 33 rated 1–3 stars; fit is the top complaint (30% of low-rated reviews).")
    fig("ai2_complaint_map.png", "Complaint themes in low-rated reviews")

    st.subheader("Seasonality and demand (AI7)")
    st.info("Google Trends measures search interest, not sales. A seasonal-naive baseline beat the models for 'kurta for men' (MAPE 12.3%).")
    fig("trends_seasonality.png", "Search interest by month, 2022–2025")
    fig("ai7_demand_forecast.png", "Forecast comparison")

    st.subheader("Which assumptions matter most")
    fig("tornado_ebitda.png", "24-month EBITDA when each input moves ±10–20% (plan as briefed)")

# =============================================================================
# About
# =============================================================================
with tab_about:
    st.markdown(f"""
**What this is.** A calculator for the TARU capstone: a fictional certified-organic men's ethnic wear brand. It answers one question:
*at a given price, cost and channel mix, does each set make money, and how many sets a month cover the fixed costs?*

**Recommendation it supports.** As briefed (four channels including a marketplace, full team), blended contribution is about ₹355 per set
and break-even needs about 957 sets a month, against a year-2 plan of 250. The recommended pivot (no marketplace; own site, pop-ups and
corporate gifting; leaner overheads; ₹140/m everyday fabric) lifts contribution to about ₹677 per set and break-even to about 281 sets a month.
Use the two presets at the top of the Calculator to see both.

**How it is calculated.** The same formulas as `model/taru_economics.xlsx`, sheets Range_Cost and Channel_Waterfalls:
- Net price = retail price ÷ (1 + GST); GST 5% at or below ₹2,500 per set, 18% above.
- Product cost (COGS) = fabric (metres × ₹/m) + wastage + stitching + trims + packaging + certification.
- Contribution per set = net revenue − COGS − commission − fixed fee − payment gateway − shipping − returns − COD return-to-origin − acquisition.
- Blended = weighted by the line mix (Everyday 45%, Festive 40%, Ceremonial 15%) and your channel mix.
- Break-even sets per month = (fixed overheads + brand content) ÷ blended contribution per set.

**Added beyond the spreadsheet.** The *Retail partner* channel (retailer margin and sale-or-return), requested in the brief. Its defaults
(40% margin, 30% returned unsold, ₹60 handling, ₹30 freight, ₹100 trade support per set) are assumptions, and it is off by default.

**Not included.** Launch spend, stock paid ahead of sales, marketplace settlement delay and the 24-month cash curve (all in the spreadsheet);
GST input credit; inflation. The brief's "fibre cost premium %" is entered as the certified fabric's price per metre, because no
conventional-fabric benchmark was collected.

**Confidence.** Inputs marked as assumptions in the spreadsheet are low confidence. The survey is a small pilot whose sample was too small and inconsistent to rely on
(see Evidence), so no survey number drives a default except as labelled "direction only".

**Source code and data:** [{REPO_URL}]({REPO_URL})

**Author:** Anvesha · PGDM (E-Business), WeSchool Mumbai. Independent student portfolio project; no employer-confidential information.
""")
