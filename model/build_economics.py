"""Adds Assumptions, Range_Cost, Channel_Waterfalls, Demand_Cash_24M and Scenarios to model/taru_economics.xlsx.
All outputs are Excel formulas; every blue input carries a source or 'Assumption'."""
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter as CL
P = "/home/claude/taru-category-launch/model/taru_economics.xlsx"
wb = load_workbook(P)
for n in ["Assumptions","Range_Cost","Channel_Waterfalls","Demand_Cash_24M","Scenarios"]:
    if n in wb.sheetnames: del wb[n]
AR=Font(name="Arial",size=10); B=Font(name="Arial",size=10,bold=True); BL=Font(name="Arial",size=10,color="0000FF")
GRN=Font(name="Arial",size=10,color="008000"); HB=Font(name="Arial",size=10,bold=True,color="FFFFFF")
HF=PatternFill("solid",start_color="2F4F3E"); YEL=PatternFill("solid",start_color="FFF2CC"); GRY=PatternFill("solid",start_color="EFEFEF")
WR=Alignment(wrap_text=True,vertical="top"); TOP=Border(top=Side(style="thin"))
INR='#,##0;(#,##0);"-"'; PCT='0.0%;(0.0%);"-"'
def hdr(ws,r,vals,widths=None):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=HB; c.fill=HF; c.alignment=Alignment(wrap_text=True,vertical="center")
        if widths: ws.column_dimensions[CL(i)].width=widths[i-1]
def title(ws,t,sub):
    ws["A1"]=t; ws["A1"].font=Font(name="Arial",size=13,bold=True); ws["A2"]=sub; ws["A2"].font=Font(name="Arial",size=9,italic=True)

# ================= Assumptions =================
A=wb.create_sheet("Assumptions",2); title(A,"Assumptions for range, cost, channel and cash","Blue = input. Every row cites a source or says 'Assumption'. Yellow = low confidence; test in Scenarios.")
hdr(A,4,["Key","Input","Everyday","Festive","Ceremonial","Unit","Source / note"],[16,40,13,13,13,12,70])
rows=[
("price","Retail price per set (MRP = selling; no markdowns)",2499,4999,8999,"₹","Price audit + VW: everyday held under ₹2,500 GST slab; festive ~10% over Manyavar festive median (₹4,499); ceremonial inside survey acceptable range (₹4,800–11,250)"),
("fab_m","Fabric per set",5.0,5.0,7.5,"metres","Assumption: kurta ~2.75 m + pyjama ~2.25 m; ceremonial adds Nehru jacket"),
("fab_rate","Certified-organic fabric cost",180,350,450,"₹/m","IndiaMART GOTS organic cotton listings ₹110–350/m (30 Sep 2026); festive/ceremonial = linen or handloom premium (assumption)"),
("cmt","Cut-make-trim (stitching) per set",350,500,1200,"₹","IndiaMART kurta-pajama job work ₹300–700/set; ceremonial with jacket (assumption)"),
("trims","Buttons, thread, labels, swing tag",60,120,250,"₹","Assumption"),
("pack","Packaging (bag / box, tissue, proof card)",90,150,300,"₹","Assumption; ceremonial = rigid box (brand book 5.1)"),
("cert","Certification and traceability per set",30,30,40,"₹","Assumption: GOTS licence + QR trail spread over volume"),
("waste","Fabric wastage and QC rejects",0.08,0.08,0.10,"% of materials","Assumption"),
("line_mix","Share of units",0.45,0.40,0.15,"%","Assumption; Trends: festive/wedding searches dominate Oct–Nov"),
]
r=5; names={}
for k,lab,e,f,c,u,src in rows:
    A.cell(r,1,k).font=AR; A.cell(r,2,lab).font=AR
    for j,v in enumerate([e,f,c],3):
        x=A.cell(r,j,v); x.font=BL; x.number_format = PCT if u.startswith("%") else INR
        if "Assumption" in src and "IndiaMART" not in src: x.fill=YEL
    A.cell(r,6,u).font=AR; s=A.cell(r,7,src); s.font=AR; s.alignment=WR
    names[k]=r; r+=1
r+=1; A.cell(r,1,"GST").font=B; r+=1
A.cell(r,1,"gst_low").font=AR; A.cell(r,2,"GST at or below ₹2,500 per piece").font=AR; A.cell(r,3,0.05).font=BL; A.cell(r,3).number_format=PCT; A.cell(r,7,"Register R048 (w.e.f. 22 Sep 2025)").font=AR; names["gst_low"]=r; r+=1
A.cell(r,1,"gst_high").font=AR; A.cell(r,2,"GST above ₹2,500 per piece").font=AR; A.cell(r,3,0.18).font=BL; A.cell(r,3).number_format=PCT; A.cell(r,7,"Register R048").font=AR; names["gst_high"]=r; r+=1
A.cell(r,1,"gst_cut").font=AR; A.cell(r,2,"GST threshold").font=AR; A.cell(r,3,2500).font=BL; A.cell(r,3).number_format=INR; A.cell(r,7,"Register R048. Applied per set here; per-piece billing of a set could lower tax (note for D8)").font=AR; names["gst_cut"]=r; r+=2

A.cell(r,1,"CHANNELS").font=B; r+=1
hdr(A,r,["Key","Input","D2C website","Marketplace","Pop-up","Corporate gifting","Source / note"]); ch_hdr=r; r+=1
crow=[
("mix","Share of units",0.35,0.30,0.20,0.15,"Assumption; survey G1 ranks marketplace and brand website first (direction only)"),
("disc","Price discount to customer / buyer",0,0,0,0.15,"Assumption: gifting bulk rate 15%"),
("comm","Commission (% of selling price)",0,0.275,0,0,"Register R069: Myntra 25–30% (press estimate, L)"),
("fixed_fee","Fixed fee per order",0,25,0,0,"Register R070: ₹15–35 (L)"),
("pg","Payment gateway (% incl. 18% GST on fee)",0.0236,0,0.0236,0,"Register R076: Razorpay 2% + GST"),
("ship","Forward shipping per order",60,90,0,30,"Register R073/R071: ₹25–45/500 g aggregator; ₹55–120 Myntra; gifting = bulk"),
("ret","Return rate",0.20,0.25,0.03,0.02,"Register R062/R063: fashion 25–40%; own site with fit guide lower (assumption)"),
("rev_ship","Reverse shipping per return",70,90,0,0,"Register R071: reverse ≈ forward"),
("loss","Unsellable share of returned value",0.10,0.10,0.10,0.10,"Assumption"),
("cod","COD share of orders",0.64,0,0,0,"Survey G4 (64%, direction only)"),
("rto","Return-to-origin rate on COD orders",0.20,0,0,0,"Register R064: RTO peaks ~39%; 20% assumed on an average month"),
("acq","Acquisition or venue cost per unit",550,150,450,200,"Assumption: D2C paid social CAC; marketplace ads; pop-up stall ~₹40k per 3-day event ÷ ~90 sets; gifting sales effort"),
]
for k,lab,*v,src in crow:
    A.cell(r,1,k).font=AR; A.cell(r,2,lab).font=AR
    for j,x in enumerate(v,3):
        c=A.cell(r,j,x); c.font=BL; c.number_format = PCT if (isinstance(x,float) and x<1) or k in("mix","disc","comm","pg","ret","loss","cod","rto") else INR
        if "Assumption" in src or "(L)" in src: c.fill=YEL
    s=A.cell(r,7,src); s.font=AR; s.alignment=WR; names["ch_"+k]=r; r+=1
r+=1; A.cell(r,1,"OVERHEADS AND VOLUME").font=B; r+=1
orow=[("fixed_m","Fixed overheads per month (2 staff + founder draw, studio, software, audits)",265000,"₹/month","Assumption"),
("mkt_m","Brand content and PR per month (on top of per-unit acquisition)",75000,"₹/month","Assumption"),
("capex","Launch spend in month 1 (samples, shoot, website, certification set-up)",800000,"₹","Assumption"),
("units_y1","Units, year 1 (Jul 2027–Jun 2028)",1800,"sets","Sizing v1: 24-month SOM ≈ 4,200 sets at 0.5% of SAM (Sizing!B27)"),
("units_y2","Units, year 2 (Jul 2028–Jun 2029)",3000,"sets","Sizing v1 (growth as channels add)"),
("mp_lag","Marketplace settlement delay",1,"months","Register / practitioner norm; assumption"),
("lead","Production lead time (stock paid a month before sale)",1,"months","Assumption; Trends peak Oct–Nov means stock lands by Sep"),
]
for k,lab,v,u,src in orow:
    A.cell(r,1,k).font=AR; A.cell(r,2,lab).font=AR; c=A.cell(r,3,v); c.font=BL; c.number_format=INR; c.fill=YEL if src.startswith("Assumption") else PatternFill()
    A.cell(r,6,u).font=AR; A.cell(r,7,src).font=AR; names[k]=r; r+=1
r+=1; A.cell(r,1,"SEASONALITY").font=B; r+=1
hdr(A,r,["Month","kurta for men index","wedding outfit index","Blend","Weight","","Source: Google Trends India, 2022–2025 average, each year's mean = 100 (data/clean/desk_results.json)"]); r+=1
kur=[93,103,121,129,75,57,53,80,106,178,129,77]; wed=[120,121,98,140,79,51,41,50,64,113,195,128]
mon=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]; s0=r
for i in range(12):
    A.cell(r,1,mon[i]).font=AR; A.cell(r,2,kur[i]).font=BL; A.cell(r,3,wed[i]).font=BL
    A.cell(r,4,f"=AVERAGE(B{r}:C{r})").font=AR; A.cell(r,5,f"=D{r}/SUM($D${s0}:$D${s0+11})").font=AR; A.cell(r,5).number_format=PCT; r+=1
names["season_first"]=s0
A.freeze_panes="C5"
def a(k,col="C"): return f"Assumptions!${col}${names[k]}"
LC={"Everyday":"C","Festive":"D","Ceremonial":"E"}; CC={"D2C website":"C","Marketplace":"D","Pop-up":"E","Corporate gifting":"F"}

# ================= Range_Cost =================
R=wb.create_sheet("Range_Cost",3); title(R,"Range, price and cost stack per set","All formulas. Green = link to Assumptions.")
hdr(R,4,["Line","Price (₹)","GST rate","Net price ex-GST (₹)","Fabric (₹)","Wastage (₹)","CMT (₹)","Trims (₹)","Packaging (₹)","Certification (₹)","COGS (₹)","Gross margin (₹)","Gross margin %","Clears 50% floor (H4)?","Units share"],[12,11,9,13,11,11,10,10,11,12,11,12,11,13,10])
rr={}
for i,(ln,col) in enumerate(LC.items()):
    r=5+i; rr[ln]=r; R.cell(r,1,ln).font=B
    f=[f"={a('price',col)}", f"=IF(B{r}<={a('gst_cut')},{a('gst_low')},{a('gst_high')})", f"=B{r}/(1+C{r})",
       f"={a('fab_m',col)}*{a('fab_rate',col)}", f"=(E{r}+H{r})*{a('waste',col)}", f"={a('cmt',col)}", f"={a('trims',col)}", f"={a('pack',col)}", f"={a('cert',col)}",
       f"=SUM(E{r}:J{r})", f"=D{r}-K{r}", f"=IF(D{r}=0,0,L{r}/D{r})", f'=IF(M{r}>=0.5,"yes","NO")', f"={a('line_mix',col)}"]
    for j,x in enumerate(f,2):
        c=R.cell(r,j,x); c.font=GRN if j in (2,6+1,8,9,10,15) and "Assumptions" in x and "*" not in x else AR
        c.number_format = PCT if j in (3,13,15) else INR
r=8; R.cell(r,1,"Weighted").font=B
for j,colL in [(4,"D"),(11,"K"),(12,"L")]:
    R.cell(r,j,f"=SUMPRODUCT({colL}5:{colL}7,$O$5:$O$7)").font=B; R.cell(r,j).number_format=INR
R.cell(r,13,"=IF(D8=0,0,L8/D8)").font=B; R.cell(r,13).number_format=PCT
R.cell(10,1,"Reading: the everyday line is held under the ₹2,500 GST slab and priced below Manyavar's ₹2,624 natural-fibre set, so it cannot reach a 50% gross margin with certified fabric. It works as an entry and traffic line; margin comes from festive and ceremonial.").font=AR
R.merge_cells("A10:O11"); R["A10"].alignment=WR

# ================= Channel_Waterfalls =================
W=wb.create_sheet("Channel_Waterfalls",4); title(W,"Contribution per set, by line and channel","One column per line × channel. Contribution = net revenue − COGS − channel costs − acquisition.")
combos=[(ln,ch) for ln in LC for ch in CC]
W.column_dimensions["A"].width=38
for j,(ln,ch) in enumerate(combos,2):
    c=W.cell(4,j,f"{ln}\n{ch}"); c.font=HB; c.fill=HF; c.alignment=Alignment(wrap_text=True,horizontal="center"); W.column_dimensions[CL(j)].width=13
W.row_dimensions[4].height=30; W.cell(4,1,"₹ per set sold").font=HB; W.cell(4,1).fill=HF
lines=["Net price ex-GST","Customer / buyer discount","Net revenue","COGS","Gross margin","Commission","Fixed fee","Payment gateway","Forward shipping","Returns cost","COD return-to-origin cost","Acquisition / venue","Contribution","Contribution %","Unit mix weight"]
for i,l in enumerate(lines,5): W.cell(i,1,l).font=B if l in("Net revenue","Gross margin","Contribution") else AR
for j,(ln,ch) in enumerate(combos,2):
    L=CL(j); rc=rr[ln]; cc=CC[ch]
    ch_=lambda k: f"Assumptions!${cc}${names['ch_'+k]}"
    fs=[f"=Range_Cost!$D${rc}", f"=-{L}5*{ch_('disc')}", f"={L}5+{L}6", f"=-Range_Cost!$K${rc}", f"={L}7+{L}8",
        f"=-{L}7*{ch_('comm')}", f"=-{ch_('fixed_fee')}", f"=-{L}7*{ch_('pg')}", f"=-{ch_('ship')}",
        f"=-{ch_('ret')}*({ch_('ship')}+{ch_('rev_ship')}+{L}7*{ch_('loss')})",
        f"=-{ch_('cod')}*{ch_('rto')}*({ch_('ship')}+{ch_('rev_ship')})",
        f"=-{ch_('acq')}*Scenarios!$C$8", f"=SUM({L}9:{L}16)", f"=IF({L}7=0,0,{L}17/{L}7)",
        f"=Range_Cost!$O${rc}*{ch_('mix')}"]
    for i,x in enumerate(fs,5):
        c=W.cell(i,j,x); c.font=B if i in (7,9,17) else AR; c.number_format = PCT if i in (18,19) else INR
        if i==17: c.border=TOP
W.cell(21,1,"Blended per set (mix-weighted)").font=B
for i,(lab,row) in enumerate([("Net revenue",7),("COGS",8),("Channel + acquisition costs",None),("Contribution",17)],22):
    W.cell(i,1,lab).font=AR
    last=CL(len(combos)+1)
    if row: W.cell(i,2,f"=SUMPRODUCT(B{row}:{last}{row},B19:{last}19)")
    else: W.cell(i,2,f"=SUMPRODUCT(B10:{last}16,B19:{last}19*1)" )
    W.cell(i,2).number_format=INR; W.cell(i,2).font=B
# fix channel-cost blended (rows 10-16 sum per column × weight)
W.cell(24,2,"="+"+".join(f"SUM({CL(j)}10:{CL(j)}16)*{CL(j)}19" for j in range(2,len(combos)+2)))
W.cell(25,1,"Blended contribution %").font=AR; W.cell(25,2,"=IF(B22=0,0,B25_/B22)".replace("B25_","B25")); 
W.cell(26,1,"Blended contribution %").font=B; W.cell(26,2,"=IF(B22=0,0,B25/B22)"); W.cell(26,2).number_format=PCT
W.cell(25,1,"Contribution per set").font=B; W.cell(25,2,"=B22+B23+B24")
W.cell(25,2).number_format=INR; W.cell(25,2).font=B
W.delete_rows(21+0,0)
W.freeze_panes="B5"

# ================= Scenarios =================
S=wb.create_sheet("Scenarios",5); title(S,"Scenario switch and results","Pick a scenario in C5. Every sheet recalculates.")
hdr(S,4,["","Driver","Selected","Downside","Base","Upside"],[4,40,13,13,13,13])
S["B5"]="Scenario (1 = Downside, 2 = Base, 3 = Upside)"; S["C5"]=2; S["C5"].font=BL; S["C5"].fill=YEL
dv=DataValidation(type="list",formula1='"1,2,3"'); S.add_data_validation(dv); dv.add("C5")
drv=[("Volume multiplier",0.6,1.0,1.4),("Price realisation (share of list price achieved)",0.95,1.0,1.0),("Acquisition cost multiplier",1.4,1.0,0.8),("Fixed overhead multiplier",1.1,1.0,1.0)]
for i,(lab,d,b_,u) in enumerate(drv,6):
    S.cell(i,2,lab).font=AR
    for j,v in enumerate([d,b_,u],4): c=S.cell(i,j,v); c.font=BL; c.number_format='0.00"x"'
    S.cell(i,3,f"=CHOOSE($C$5,D{i},E{i},F{i})").font=AR; S.cell(i,3).number_format='0.00"x"'
# row8 = acquisition multiplier used by Channel_Waterfalls (C8)

# ================= Demand_Cash_24M =================
D=wb.create_sheet("Demand_Cash_24M",6); title(D,"24-month demand, P&L and cash (Jul 2027 – Jun 2029)","Units follow the Google Trends season; stock is paid one month before it sells; marketplace cash lands one month late.")
D.column_dimensions["A"].width=36
import datetime
labels=["Month","Calendar month no.","Year of plan","Season weight","Units sold","Revenue ex-GST","COGS","Channel + acquisition costs","Contribution","Fixed overheads","Brand content","Launch spend","EBITDA","Cumulative EBITDA","Stock purchase (next month's COGS)","Marketplace receivable change","Cash flow","Cumulative cash"]
for i,l in enumerate(labels,4): D.cell(i,1,l).font=B if l in("Contribution","EBITDA","Cash flow","Cumulative cash") else AR
start=datetime.date(2027,7,1); ncol=24
mp_share=f"(Assumptions!$D${names['ch_mix']})"
for m in range(ncol+1):   # extra column 26 = month 25 for next-month COGS
    j=2+m; L=CL(j); y=start.year+(start.month-1+m)//12; mo=(start.month-1+m)%12+1
    D.cell(4,j,datetime.date(y,mo,1)).number_format="mmm yy"; D.cell(4,j).font=HB; D.cell(4,j).fill=HF
    D.cell(5,j,mo); D.cell(6,j,1 if m<12 else 2)
    D.cell(7,j,f"=INDEX(Assumptions!$E${names['season_first']}:$E${names['season_first']+11},{L}5)"); D.cell(7,j).number_format=PCT
    D.cell(8,j,f"=IF({L}6=1,{a('units_y1')},{a('units_y2')})*{L}7*Scenarios!$C$6"); D.cell(8,j).number_format=INR
    D.cell(9,j,f"={L}8*Channel_Waterfalls!$B$22*Scenarios!$C$7")
    D.cell(10,j,f"={L}8*Channel_Waterfalls!$B$23")
    D.cell(11,j,f"={L}8*Channel_Waterfalls!$B$24")
    D.cell(12,j,f"={L}9+{L}10+{L}11")
    D.cell(13,j,f"=-{a('fixed_m')}*Scenarios!$C$9"); D.cell(14,j,f"=-{a('mkt_m')}")
    D.cell(15,j,f"=-{a('capex')}" if m==0 else 0)
    D.cell(16,j,f"=SUM({L}12:{L}15)")
    D.cell(17,j,f"={L}16" if m==0 else f"={CL(j-1)}17+{L}16")
    N=CL(j+1)
    D.cell(18,j,f"={N}10" if m<ncol-1 else f"={L}10")
    D.cell(19,j,f"=-{L}9*{mp_share}" if m==0 else f"=-({L}9-{CL(j-1)}9)*{mp_share}")
    D.cell(20,j,(f"={L}16-{L}10+{L}18+{L}19-{L}10" if False else f"={L}16-{L}10+{L}18+{L}19") + ("" if m else f"+{L}10"))
    D.cell(21,j,f"={L}20" if m==0 else f"={CL(j-1)}21+{L}20")
    for rrow in range(8,22): D.cell(rrow,j).number_format=INR; D.cell(rrow,j).font=AR
    for rrow in (12,16,20,21): D.cell(rrow,j).font=B
    if m==ncol: 
        for rrow in range(4,22): D.cell(rrow,j).fill=GRY
D.cell(3,26,"Month 25 shown only to time the last stock purchase").font=Font(name="Arial",size=8,italic=True)
# Month-1 stock purchase must also cover month-1 sales -> add month-1 COGS as upfront purchase
D.cell(20,2,"=B16+B18+B19")  # month 1: EBITDA excludes COGS timing: pay month1 and month2 stock; EBITDA already includes -COGS m1
D.freeze_panes="B5"
last="Y"
# results on Scenarios
res=[("24-month revenue ex-GST (₹)",f"=SUM(Demand_Cash_24M!B9:{last}9)"),("24-month contribution (₹)",f"=SUM(Demand_Cash_24M!B12:{last}12)"),
("24-month EBITDA (₹)",f"=SUM(Demand_Cash_24M!B16:{last}16)"),("Year-2 EBITDA (₹)",f"=SUM(Demand_Cash_24M!N16:{last}16)"),
("Peak funding need: lowest cumulative cash (₹)",f"=MIN(Demand_Cash_24M!B21:{last}21)"),
("Month of lowest cash",f"=INDEX(Demand_Cash_24M!B4:{last}4,MATCH(MIN(Demand_Cash_24M!B21:{last}21),Demand_Cash_24M!B21:{last}21,0))"),
("First month with positive EBITDA",f'=IFERROR(INDEX(Demand_Cash_24M!B4:{last}4,MATCH(TRUE,INDEX(Demand_Cash_24M!B16:{last}16>0,0),0)),"none in 24 months")'),
("Blended contribution per set (₹)","=Channel_Waterfalls!B25*Scenarios!C7"),
("Break-even sets per month (fixed + content ÷ contribution per set)",f"=IF(Channel_Waterfalls!B25<=0,\"never\",({a('fixed_m')}*C9+{a('mkt_m')})/Channel_Waterfalls!B25)"),
("Average sets per month, year 2",f"={a('units_y2')}*C6/12")]
S.cell(12,2,"RESULTS (selected scenario)").font=B
for i,(lab,fx) in enumerate(res,13):
    S.cell(i,2,lab).font=AR; c=S.cell(i,3,fx); c.font=B
    c.number_format = "mmm yy" if "Month" in lab or "month with" in lab else INR
S.column_dimensions["B"].width=58
wb.move_sheet("Scenarios", offset=-(wb.sheetnames.index("Scenarios")-1))
wb["README"]["B2"]="30 Sep 2026. Tabs: README, Scenarios (switch + results), Inputs + Sizing (market), Assumptions, Range_Cost, Channel_Waterfalls, Demand_Cash_24M."
wb.save(P); print("saved")
