"""
TARU unit economics: a line-by-line copy of model/taru_economics.xlsx
(sheets Assumptions, Range_Cost and Channel_Waterfalls), so the Streamlit app
gives the same numbers as the spreadsheet. Tested in app/tests/test_model.py.

All money in rupees per set. Prices include GST; revenue is computed ex-GST.
"""
from __future__ import annotations

import copy

LINES = ["Everyday", "Festive", "Ceremonial"]
CHANNELS = ["D2C website", "Marketplace", "Pop-up", "Corporate gifting", "Retail partner"]

# ---------------------------------------------------------------------------
# Defaults = the spreadsheet's "plan as briefed" (base scenario)
# ---------------------------------------------------------------------------
BASE = {
    "line": {
        #             price  fab_m fab_rate cmt  trims pack cert waste mix
        "Everyday":   dict(price=2499, fab_m=5.0, fab_rate=180, cmt=350, trims=60, pack=90, cert=30, waste=0.08, mix=0.45),
        "Festive":    dict(price=4999, fab_m=5.0, fab_rate=350, cmt=500, trims=120, pack=150, cert=30, waste=0.08, mix=0.40),
        "Ceremonial": dict(price=8999, fab_m=7.5, fab_rate=450, cmt=1200, trims=250, pack=300, cert=40, waste=0.10, mix=0.15),
    },
    "gst": dict(low=0.05, high=0.18, cut=2500),
    "channel": {
        "D2C website":       dict(mix=0.35, disc=0.0,  comm=0.0,   fixed_fee=0,  pg=0.0236, ship=60, ret=0.20, rev_ship=70, loss=0.10, cod=0.64, rto=0.20, acq=550),
        "Marketplace":       dict(mix=0.30, disc=0.0,  comm=0.275, fixed_fee=25, pg=0.0,    ship=90, ret=0.25, rev_ship=90, loss=0.10, cod=0.0,  rto=0.0,  acq=150),
        "Pop-up":            dict(mix=0.20, disc=0.0,  comm=0.0,   fixed_fee=0,  pg=0.0236, ship=0,  ret=0.03, rev_ship=0,  loss=0.10, cod=0.0,  rto=0.0,  acq=450),
        "Corporate gifting": dict(mix=0.15, disc=0.15, comm=0.0,   fixed_fee=0,  pg=0.0,    ship=30, ret=0.02, rev_ship=0,  loss=0.10, cod=0.0,  rto=0.0,  acq=200),
        # Not in the spreadsheet: added for the brief's "retailer margin" and "sale-or-return" inputs.
        # Off by default (mix 0) so the defaults still match the spreadsheet. All values are assumptions.
        "Retail partner":    dict(mix=0.0,  disc=0.0,  comm=0.0,   fixed_fee=0,  pg=0.0,    ship=30, ret=0.0,  rev_ship=0,  loss=0.10, cod=0.0,  rto=0.0,  acq=100,
                                  retailer_margin=0.40, sor=0.30, sor_handling=60),
    },
    "fixed_m": 265000,      # fixed overheads per month
    "mkt_m": 75000,         # brand content and PR per month
    "acq_mult": 1.0,        # Scenarios!C8 (base)
    "year2_sets_per_month": 250,
}

# The pivot recommended in the findings report (model/sensitivity_results.json, "pivot_definition")
PIVOT_CHANGES = {
    ("channel", "D2C website", "mix"): 0.40, ("channel", "Marketplace", "mix"): 0.0,
    ("channel", "Pop-up", "mix"): 0.30, ("channel", "Corporate gifting", "mix"): 0.30,
    ("fixed_m",): 150000, ("mkt_m",): 40000, ("line", "Everyday", "fab_rate"): 140,
}


def params(preset: str = "briefed") -> dict:
    p = copy.deepcopy(BASE)
    if preset == "pivot":
        for path, v in PIVOT_CHANGES.items():
            d = p
            for k in path[:-1]:
                d = d[k]
            d[path[-1]] = v
    return p


# Comparison points from the research (price audit 30 Sep 2026; survey Van Westendorp, order-consistent answers)
MANYAVAR_MEDIAN = {"Everyday": 2624, "Festive": 3999, "Ceremonial": 6999}
VW_RANGE = {"Everyday": (1250, 3800), "Ceremonial": (4800, 11250)}   # no festive question was asked

# ---------------------------------------------------------------------------
# Range_Cost
# ---------------------------------------------------------------------------

def gst_rate(price: float, p: dict) -> float:
    return p["gst"]["low"] if price <= p["gst"]["cut"] else p["gst"]["high"]


def net_price(line: str, p: dict) -> float:
    price = p["line"][line]["price"]
    return price / (1 + gst_rate(price, p))


def cogs_parts(line: str, p: dict) -> dict:
    L = p["line"][line]
    fabric = L["fab_m"] * L["fab_rate"]
    return {"Fabric": fabric, "Wastage": (fabric + L["trims"]) * L["waste"], "Stitching (CMT)": L["cmt"],
            "Trims": L["trims"], "Packaging": L["pack"], "Certification": L["cert"]}


def cogs(line: str, p: dict) -> float:
    return sum(cogs_parts(line, p).values())

# ---------------------------------------------------------------------------
# Channel_Waterfalls
# ---------------------------------------------------------------------------

def waterfall(line: str, channel: str, p: dict) -> list[tuple[str, float]]:
    """Ordered steps from net price to contribution per set sold (costs negative)."""
    C = p["channel"][channel]
    net = net_price(line, p)
    disc = -net * C["disc"]
    rev = net + disc
    steps = [("Net price ex-GST", net), ("Discount", disc)]
    if channel == "Retail partner":
        steps.append(("Retailer margin", -rev * C["retailer_margin"]))
        rev = rev * (1 - C["retailer_margin"])
    steps.append(("COGS", -cogs(line, p)))
    steps += [
        ("Commission", -rev * C["comm"]),
        ("Fixed fee", -C["fixed_fee"]),
        ("Payment gateway", -rev * C["pg"]),
        ("Forward shipping", -C["ship"]),
        ("Returns", -C["ret"] * (C["ship"] + C["rev_ship"] + rev * C["loss"])),
        ("COD return-to-origin", -C["cod"] * C["rto"] * (C["ship"] + C["rev_ship"])),
    ]
    if channel == "Retail partner":
        s = C["sor"]
        returned_per_sold = s / (1 - s) if s < 1 else float("inf")
        steps.append(("Sale-or-return stock back", -returned_per_sold * (C["sor_handling"] + cogs(line, p) * C["loss"])))
    steps.append(("Acquisition / venue", -C["acq"] * p["acq_mult"]))
    return steps


def revenue(line: str, channel: str, p: dict) -> float:
    C = p["channel"][channel]
    r = net_price(line, p) * (1 - C["disc"])
    return r * (1 - C.get("retailer_margin", 0.0)) if channel == "Retail partner" else r


def contribution(line: str, channel: str, p: dict) -> float:
    return sum(v for _, v in waterfall(line, channel, p))


def channel_mix(p: dict) -> dict:
    """Channel shares normalised to sum to 1 (sliders need not add up exactly)."""
    tot = sum(p["channel"][c]["mix"] for c in CHANNELS)
    return {c: (p["channel"][c]["mix"] / tot if tot else 0.0) for c in CHANNELS}


def line_mix(p: dict) -> dict:
    tot = sum(p["line"][l]["mix"] for l in LINES)
    return {l: (p["line"][l]["mix"] / tot if tot else 0.0) for l in LINES}


def blended(p: dict) -> dict:
    cm, lm = channel_mix(p), line_mix(p)
    out = {"revenue": 0.0, "cogs": 0.0, "contribution": 0.0}
    for l in LINES:
        for c in CHANNELS:
            w = lm[l] * cm[c]
            if not w:
                continue
            out["revenue"] += revenue(l, c, p) * w
            out["cogs"] += cogs(l, p) * w
            out["contribution"] += contribution(l, c, p) * w
    out["channel_costs"] = out["revenue"] - out["cogs"] - out["contribution"]
    out["contribution_pct"] = out["contribution"] / out["revenue"] if out["revenue"] else 0.0
    return out


def breakeven_sets_per_month(p: dict, fixed_m: float | None = None, mkt_m: float | None = None) -> float | None:
    """(fixed overheads + brand content) / blended contribution per set. None = never (contribution <= 0)."""
    fixed = p["fixed_m"] if fixed_m is None else fixed_m
    mkt = p["mkt_m"] if mkt_m is None else mkt_m
    c = blended(p)["contribution"]
    return None if c <= 0 else (fixed + mkt) / c


def premium_vs_manyavar(line: str, p: dict) -> float:
    return p["line"][line]["price"] / MANYAVAR_MEDIAN[line] - 1


def vw_check(line: str, p: dict) -> tuple[str, str]:
    """('ok' | 'outside' | 'none', message)."""
    price = p["line"][line]["price"]
    if line not in VW_RANGE:
        return "none", "No Van Westendorp question was asked for the festive set."
    lo, hi = VW_RANGE[line]
    if lo <= price <= hi:
        return "ok", f"Inside the acceptable range from the survey (₹{lo:,}–₹{hi:,})."
    return "outside", f"Outside the acceptable range from the survey (₹{lo:,}–₹{hi:,})."
