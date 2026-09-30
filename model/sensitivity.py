"""Tornado + pivot test: edits a copy of the model, recalculates with LibreOffice, reads results. Run from repo root."""
import shutil, subprocess, json, tempfile, os
from openpyxl import load_workbook
SRC="model/taru_economics.xlsx"; RC="/mnt/skills/public/xlsx/scripts/recalc.py"
def run(edits):
    d=tempfile.mkdtemp(); p=os.path.join(d,"m.xlsx"); shutil.copy(SRC,p)
    wb=load_workbook(p); A=wb["Assumptions"]
    for (sheet,cell),v in edits.items(): wb[sheet][cell]=v
    wb.save(p); subprocess.run(["python3",RC,p,"60"],capture_output=True)
    w=load_workbook(p,data_only=True); S=w["Scenarios"]; W=w["Channel_Waterfalls"]
    return {"ebitda24":S["C15"].value,"low_cash":S["C17"].value,"cm_per_set":W["B25"].value,"breakeven_sets_m":S["C21"].value}
A=load_workbook(SRC)["Assumptions"]
def find(key):
    for r in range(1,A.max_row+1):
        if A.cell(r,1).value==key.replace("ch_",""): return r
base=run({})
drivers={ "Price, all lines ±10%":[("C","price"),("D","price"),("E","price")],
 "Fabric cost ±20%":[("C","fab_rate"),("D","fab_rate"),("E","fab_rate")],
 "Stitching (CMT) ±20%":[("C","cmt"),("D","cmt"),("E","cmt")],
 "Acquisition cost ±20%":[("C","ch_acq"),("D","ch_acq"),("E","ch_acq"),("F","ch_acq")],
 "Marketplace commission ±20%":[("D","ch_comm")],
 "Volume ±20%":[("C","units_y1"),("C","units_y2")],
 "Fixed overheads ±20%":[("C","fixed_m")],
 "Return rates ±20%":[("C","ch_ret"),("D","ch_ret"),("E","ch_ret"),("F","ch_ret")]}
tor={}
for name,cells in drivers.items():
    pct=0.10 if name.startswith("Price") else 0.20; res=[]
    for sgn in (-1,1):
        ed={}
        for col,key in cells:
            r=find(key); v=A[f"{col}{r}"].value; ed[("Assumptions",f"{col}{r}")]=v*(1+sgn*pct)
        res.append(run(ed)["ebitda24"])
    tor[name]={"low":res[0],"high":res[1]}
# pivot: drop marketplace, lean team, cheaper everyday fabric at IndiaMART low end, ceremonial priced at survey IPP+
mix=find("ch_mix"); pv={("Assumptions",f"C{mix}"):0.40,("Assumptions",f"D{mix}"):0.0,("Assumptions",f"E{mix}"):0.30,("Assumptions",f"F{mix}"):0.30,
    ("Assumptions",f"C{find('fixed_m')}"):150000,("Assumptions",f"C{find('mkt_m')}"):40000,("Assumptions",f"C{find('capex')}"):500000,
    ("Assumptions",f"C{find('fab_rate')}"):140}
pivot=run(pv)
out={"base":base,"tornado_24m_ebitda":tor,"pivot":pivot,
     "pivot_definition":"No marketplace (D2C 40%, pop-ups 30%, corporate gifting 30%); overheads ₹1.5 lakh/month; content ₹40k/month; launch spend ₹5 lakh; everyday fabric at ₹140/m (IndiaMART GOTS poplin listing)"}
json.dump(out,open("model/sensitivity_results.json","w"),indent=1,default=str); print(json.dumps(out,indent=1,default=str))
