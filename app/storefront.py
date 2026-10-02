"""
Storefront mock-up for the TARU app: a static, non-functional shop page built from the brand book
(section 3 identity, section 5.2 website structure) and copy the author has approved:
D7 claims (compliance/claims_matrix.csv) and edited AI5 drafts (ai/eval/content_approval_queue_v2_scored.csv).

Nothing here sells anything: no cart, checkout or payment fields.
Images are AI-generated concept images supplied by the author (originals: brand/concept_images/storefront_collage_*),
cropped so that no text baked into an image makes a claim the claims matrix does not allow. Each carries an
"AI-generated image" label (D7 CL18). They are concepts, not photographs of a real garment (AI6).
"""
from __future__ import annotations

import base64
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "brand" / "logo"
IMG = Path(__file__).resolve().parent / "static" / "storefront"

C = dict(heartwood="#1F3A2F", kora="#F3EEE4", ink="#2B2926", indigo="#26324D", madder="#84302A",
         haldi="#C8912F", khadi="#D9C9A8", lichen="#9DA283")


def _svg(name: str, viewbox: str | None = None, strip_bg: bool = False, label: str = "") -> str:
    p = LOGO / name
    if not p.exists():
        return f'<span class="wordtext">TARU</span>'
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'\s(width|height)="[^"]*"', "", s, count=2)
    if viewbox:
        s = re.sub(r'viewBox="[^"]*"', f'viewBox="{viewbox}"', s, count=1)
    if strip_bg:
        s = re.sub(r"<rect[^>]*/>", "", s, count=1)
    return s.replace("<svg ", f'<svg role="img" aria-label="{html.escape(label)}" ', 1)


def _ph(label: str, brief: str = "", ratio: str = "4 / 5", ai: bool = False) -> str:
    """A labelled image placeholder."""
    tag = '<span class="ai">AI-generated image</span>' if ai else ""
    b = f'<span class="brief">{html.escape(brief)}</span>' if brief else ""
    return (f'<div class="ph" style="aspect-ratio:{ratio}"><span class="phl">IMAGE PLACEHOLDER</span>'
            f'<span class="pht">{html.escape(label)}</span>{b}{tag}</div>')


def _img(name: str, alt: str, ratio: str = "4 / 5", pos: str = "center") -> str:
    """An AI-generated concept image, embedded so the page needs no file server. Falls back to a placeholder."""
    p = IMG / f"{name}.jpg"
    if not p.exists():
        return _ph(alt, ratio=ratio)
    b64 = base64.b64encode(p.read_bytes()).decode()
    return (f'<figure class="img" style="aspect-ratio:{ratio}"><img src="data:image/jpeg;base64,{b64}" alt="{html.escape(alt)}" '
            f'style="object-position:{pos}"><span class="ai">AI-generated image</span></figure>')


def _note(text: str) -> str:
    return f'<span class="cnote">{html.escape(text)}</span>'


PROOF_STRIP = ('<div class="strip" aria-label="Proof strip">'
               '<span>FIBRE [X]% ORGANIC COTTON</span><span>GOTS</span><span>LIC. [X]</span>'
               '<span>CB [BODY]</span><span>SCAN FOR TRAIL</span></div>')

# Colours and styles follow the concept images available (author's images, 2 Oct 2026).
PRODUCTS = [
    ("Everyday", "Kurta-pyjama set", "Ivory", "₹2,499", "everyday_ivory"),
    ("Everyday", "Kurta-pyjama set, striped", "Indigo", "₹2,499", "everyday_indigo"),
    ("Festive", "Kurta set, patch pocket", "Sage", "₹4,999", "rack_sage"),
    ("Festive", "Kurta set, woven buta", "Bottle green", "₹4,999", "festive_green"),
    ("Ceremonial", "Jacquard kurta set", "Ivory and gold", "₹8,999", "ceremonial_ivory_gold"),
    ("Ceremonial", "Jacquard kurta set", "Navy", "₹8,999", "rack_navy"),
]

PHOTO_BRIEF = "Brief: man aged 40–65; at least one fuller build in every three images; skin tone unlightened"


def render(show_notes: bool = False) -> str:
    wordmark = _svg("taru_wordmark_heartwood.svg", "98 94 378 112", label="TARU")
    wordmark_rev = _svg("taru_wordmark_reversed.svg", "98 94 378 112", strip_bg=True, label="TARU")

    cards = "".join(
        f'<article class="card">{_img(img, f"{line} {name.lower()}, {col.lower()}", "1 / 1", "center top")}'
        f'<p class="desc">{line.upper()}</p><h4>{html.escape(name)} · {html.escape(col)}</h4>'
        f'<p class="price">{price}</p></article>'
        for line, name, col, price, img in PRODUCTS)

    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=IBM+Plex+Mono:wght@400&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
    :root {{ --hw:{C['heartwood']}; --kora:{C['kora']}; --ink:{C['ink']}; --khadi:{C['khadi']}; --indigo:{C['indigo']}; --madder:{C['madder']}; }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ background:var(--kora); color:var(--ink); font:400 16px/1.5 'IBM Plex Sans', Arial, sans-serif; }}
    .hero > *, .proof > *, .img, .pdp > *, .two > *, .lines > *, .grid6 > *, .gallery > *, footer .cols > * {{ min-width:0; }}
    .wrap {{ max-width:1200px; margin:0 auto; padding:0 24px; }}
    .mock {{ background:var(--ink); color:var(--kora); font:500 12px/1.4 'IBM Plex Mono', 'Courier New', monospace;
             letter-spacing:.04em; padding:8px 24px; text-align:center; }}
    header {{ border-bottom:1px solid var(--hw); }}
    header .wrap {{ display:flex; align-items:center; justify-content:space-between; height:72px; gap:24px; }}
    header svg {{ height:28px; width:auto; display:block; }}
    nav {{ display:flex; gap:24px; flex-wrap:wrap; font:500 13px/1 'IBM Plex Sans', Arial, sans-serif; letter-spacing:.1em; text-transform:uppercase; }}
    nav a, .link {{ color:var(--hw); text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:4px; }}
    .bag {{ font:500 13px 'IBM Plex Sans', Arial, sans-serif; color:var(--ink); }}
    h1,h2,h3 {{ font-family:'Fraunces', Georgia, serif; font-weight:500; color:var(--hw); }}
    h1 {{ font-size:56px; line-height:1.05; letter-spacing:-.01em; font-variation-settings:'opsz' 144; }}
    h2 {{ font-size:36px; line-height:1.15; font-variation-settings:'opsz' 72; }}
    h3 {{ font-size:24px; line-height:1.25; }}
    h4 {{ font:500 16px/1.4 'IBM Plex Sans', Arial, sans-serif; margin-top:8px; }}
    section {{ padding:64px 0; border-bottom:1px solid var(--hw); }}
    .hero {{ display:grid; grid-template-columns:1fr 2fr; gap:48px; align-items:end; }}
    .hero .lead {{ padding-bottom:48px; }}
    .hero p {{ margin-top:24px; max-width:320px; }}
    .lines {{ display:grid; grid-template-columns:repeat(3,1fr); gap:24px; margin-top:32px; }}
    .desc {{ font:500 12px/1 'IBM Plex Sans', Arial, sans-serif; letter-spacing:.12em; margin-top:16px; color:var(--ink); }}
    .price {{ font:400 15px 'IBM Plex Sans', Arial, sans-serif; margin-top:4px; }}
    .grid6 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:24px; margin-top:32px; }}
    .proof {{ display:grid; grid-template-columns:1fr 2fr; gap:48px; align-items:center; }}
    .proof svg {{ width:100%; max-width:240px; height:auto; }}
    .rings {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:24px 0; }}
    .rings div {{ border-top:1px solid var(--hw); padding-top:8px; font-size:14px; }}
    .rings b {{ display:block; font:500 12px 'IBM Plex Sans', Arial, sans-serif; letter-spacing:.12em; text-transform:uppercase; }}
    .strip {{ display:flex; flex-wrap:wrap; background:var(--khadi); color:var(--ink); font:400 13px/1.4 'IBM Plex Mono', 'Courier New', monospace;
              padding:16px; margin:24px 0 8px; }}
    .strip span {{ white-space:nowrap; }}
    .strip span:not(:last-child)::after {{ content:"│"; margin:0 12px; }}
    .pdp {{ display:grid; grid-template-columns:3fr 2fr; gap:48px; }}
    .gallery {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    .sizes {{ display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 16px; }}
    .sizes span {{ border:1px solid var(--ink); padding:8px 12px; font:500 14px 'IBM Plex Sans', Arial, sans-serif; }}
    .btn {{ display:inline-block; background:var(--hw); color:var(--kora); font:600 15px 'IBM Plex Sans', Arial, sans-serif; padding:16px 32px; margin-top:16px; border:0; opacity:.9; cursor:not-allowed; }}
    .small {{ font-size:13px; color:var(--ink); opacity:.85; }}
    .block {{ margin-top:32px; }}
    .block h5 {{ font:500 12px 'IBM Plex Sans', Arial, sans-serif; letter-spacing:.12em; text-transform:uppercase; margin-bottom:8px; }}
    .two {{ display:grid; grid-template-columns:1fr 1fr; gap:48px; align-items:center; }}
    .ph {{ position:relative; width:100%; background:#E8DFCC; border:1px dashed var(--ink); display:flex; flex-direction:column;
           justify-content:center; padding:16px; gap:8px; }}
    .phl {{ font:400 11px 'IBM Plex Mono', 'Courier New', monospace; letter-spacing:.08em; opacity:.7; }}
    .pht {{ font:500 14px/1.35 'IBM Plex Sans', Arial, sans-serif; }}
    .brief {{ font:400 12px/1.4 'IBM Plex Sans', Arial, sans-serif; opacity:.75; }}
    .img {{ position:relative; width:100%; overflow:hidden; background:#E8DFCC; }}
    .img img {{ width:100%; height:100%; object-fit:cover; display:block; }}
    .ai {{ position:absolute; right:8px; bottom:8px; background:#000; color:#fff; font:500 11px 'IBM Plex Sans', Arial, sans-serif; padding:4px 8px; }}
    .cnote {{ display:{'inline-block' if show_notes else 'none'}; font:400 11px/1.3 'IBM Plex Mono', 'Courier New', monospace; background:var(--indigo);
              color:var(--kora); padding:2px 6px; margin:4px 0; }}
    footer {{ background:var(--hw); color:var(--kora); padding:48px 0; font-size:13px; }}
    footer svg {{ height:28px; width:auto; }}
    footer path {{ fill:var(--kora); }}
    footer .cols {{ display:grid; grid-template-columns:1fr 1fr 2fr; gap:32px; margin-top:24px; }}
    footer a {{ color:var(--kora); }}
    @media (max-width:720px) {{
      h1 {{ font-size:40px; }} h2 {{ font-size:28px; }}
      .hero, .proof, .pdp, .two, footer .cols {{ grid-template-columns:1fr; gap:24px; }}
      .lines, .grid6 {{ grid-template-columns:1fr 1fr; }} .rings {{ grid-template-columns:1fr 1fr; }}
      .wrap {{ padding:0 16px; }} nav {{ display:none; }}
    }}"""

    body = f"""
<div class="mock">DESIGN MOCK-UP OF A FICTIONAL BRAND (STUDENT PORTFOLIO PROJECT) · NOTHING HERE IS FOR SALE · IMAGES ARE AI-GENERATED CONCEPTS · [PLACEHOLDERS] MARK FACTS TARU DOES NOT HOLD YET</div>
<header><div class="wrap">{wordmark}
  <nav><a>Everyday</a><a>Festive</a><a>Ceremonial</a><a>Gifting</a><a>Proof</a></nav>
  <span class="bag">Bag (0)</span></div></header>

<main class="wrap">
<section class="hero">
  <div class="lead">
    <h1>Know what you wear.</h1>{_note("D7 CL10 · Use")}
    <p>Scan to see where your fabric was grown and woven.</p>{_note("D7 CL03 · Conditional: only once certificates exist")}
    <p><span class="link">Shop the Everyday line</span></p>
  </div>
  <div>{_img("hero_banyan", "An older man in an ivory kurta set sitting under a banyan tree", "3 / 2")}{_note("Casting brief: man 40–65 met; fuller build not shown (AI6 finding)")}</div>
</section>

<section>
  <h2>Three occasions, one standard.</h2>
  <div class="lines">
    <div>{_img("hanging_ivory", "Ivory Everyday kurta on a brass rail", "4 / 3", "center top")}<p class="desc">EVERYDAY</p><h4>Cotton sets for daily wear</h4><p class="price">From ₹2,499</p></div>
    <div>{_img("occ_festive", "Bottle-green Festive kurta folded on gold cloth", "4 / 3")}<p class="desc">FESTIVE</p><h4>Cotton-linen sets for Diwali and family days</h4><p class="price">From ₹4,999</p></div>
    <div>{_img("occ_ceremonial", "Ivory and gold Ceremonial kurta folded beside a brass lamp", "4 / 3")}<p class="desc">CEREMONIAL</p><h4>Wedding sets, made to be handed down</h4>
      <p class="price">From ₹8,999 · No markdowns on the Ceremonial line.</p>{_note("D7 CL22 · Use")}</div>
  </div>
</section>

<section class="proof">
  <div>{_img("rings", "Rings of cotton bolls, seeds, yarn and woven cloth around a wooden TARU disc", "1 / 1")}
    {_note("Image text cropped out: it claimed every stage is certified (D7 CL11, Conditional)")}</div>
  <div>
    <h2>How we prove it</h2>
    <p style="margin-top:16px">Each ring stands for one stage of the garment. Scan the tag to see the certificate for each stage.</p>{_note("Brand book 3.1 · Conditional: only once certificates exist")}
    <div class="rings">
      <div><b>Farm</b>Grown in [district]</div><div><b>Gin</b>Ginned in [town]</div>
      <div><b>Mill</b>Woven in [town]</div><div><b>Garment</b>Cut and stitched in [town]</div>
    </div>
    <p>Organic cotton fabric, certified by [certification body], licence no. [X]. Scan to see the certificate and what it covers.</p>{_note("D7 CL01 · Conditional")}
    {PROOF_STRIP}{_note("Proof Strip, brand book 3.5: every field or none")}
  </div>
</section>

<section class="two">
  <div>
    <h2>Cut for the body you have.</h2>
    <p style="margin-top:16px">Cut with 4 cm more room through the waist than our standard block.</p>{_note("D7 CL06 · Use")}
    <p style="margin-top:8px">Free alterations within 30 days of delivery.</p>{_note("D7 CL07 · Use")}
    <p style="margin-top:24px">Step into ceremony. Try on the Ceremonial set and get it tailored just for you at our pop-up store.</p>{_note("AI5 CR11 · approved by the author")}
    <p style="margin-top:16px"><span class="link">Book a fitting</span> · <span class="link">See the size guide</span></p>
  </div>
  <div>{_img("fit_mannequin", "Ivory kurta on a tailor's dummy with a measuring tape", "4 / 3")}{_note("Brief asked for two builds on body; replace with real fit photography")}</div>
</section>

<section>
  <h2>The range</h2>
  <div class="grid6">{cards}</div>
</section>

<section class="pdp">
  <div class="gallery">
    {_img("flatlay_set", "Ivory Everyday kurta and pyjama, flat lay", "1 / 1")}
    {_img("weave_macro", "Close-up of the slub weave and embroidery", "1 / 1")}
    {_img("occ_everyday", "Ivory Everyday kurta folded beside a brass pot", "1 / 1")}
    {_img("pyjama", "Ivory drawstring pyjama, folded", "1 / 1")}
  </div>
  <div>
    <p class="desc">EVERYDAY</p>
    <h3 style="margin-top:8px">Kurta-pyjama set · Ivory</h3>
    <p class="price" style="font-size:18px;margin-top:8px">₹2,499 <span class="small">incl. GST</span></p>
    <div class="block"><h5>Fit first: choose by chest measurement</h5>
      <div class="sizes"><span>38</span><span>40</span><span>42</span><span>44</span><span>46</span><span>48</span><span>50</span><span>52</span></div>
      <p class="small">Cut with 4 cm more room through the waist than our standard block. <span class="link">Fuller-build guide</span></p>{_note("D7 CL06 · Use")}
    </div>
    <span class="btn" aria-disabled="true">Add to bag (mock-up)</span>
    <div class="block"><h5>Fabric and construction</h5>
      <p>Organic cotton fabric, certified by [certification body], licence no. [X]. Scan to see where your fabric was grown and woven. Fibre: 100% cotton. Care: gentle wash, dry in shade. Made in India. See the size guide.</p>
      {_note("AI5 CR14 · edited and approved by the author (written for the indigo set; the text names no colour)")}
    </div>
    {PROOF_STRIP}
    <div class="block"><h5>Alterations and returns</h5>
      <p>Free alterations within 30 days of delivery.</p>{_note("D7 CL07 · Use")}
      <p class="small" style="margin-top:4px">Returns: [return window and conditions].</p>
    </div>
  </div>
</section>

<section class="two">
  <div>{_img("gift_box", "Kurta folded in a dark green gift box with printed tissue and a TARU tag", "4 / 3")}{_note("Box lid and card text cropped out (not in the claims matrix)")}</div>
  <div>
    <h2>Chosen with care. The proof is inside the box, if he wants it.</h2>{_note("Brand book 2.3 · gift tone")}
    <p style="margin-top:16px">No price appears anywhere in the box.</p>{_note("Brand book 5.1 · gift edition")}
    <p style="margin-top:16px"><span class="link">Shop gifting</span></p>
  </div>
</section>

<section>
  <h2>Journal</h2>
  <div class="lines">
    <div>{_img("wedding", "Men in ivory, sage and cream kurtas at a wedding courtyard", "4 / 3")}<h4>Lookbook image created using AI.</h4>{_note("D7 CL18 · Use (mandatory on AI images)")}</div>
    <div>{_img("qr_tag", "TARU swing tag with a QR code: Scan to see its story", "4 / 3")}{_note("QR in the image is not functional")}<h4>What does 'certified organic' actually certify? Four steps, no jargon.</h4></div>
    <div>{_img("tailor_tools", "Pattern paper, scissors and a measuring tape on a tailor's table", "4 / 3")}<h4>How a free alteration works</h4></div>
  </div>
</section>
</main>

<footer><div class="wrap">
  {wordmark_rev}
  <div class="cols">
    <div><a>Proof</a><br><a>Size guide</a><br><a>Alterations</a></div>
    <div><a>About</a><br><a>Gifting</a><br><a>Contact</a></div>
    <div>TARU is a fictional brand created for an independent student portfolio project. Images marked "AI-generated image" were created with AI.
      Facts in [square brackets] are placeholders: TARU holds no certificate. Every public line passes the claims guardrail (AI4) and a person.</div>
  </div>
</div></footer>"""
    return f'<!doctype html><html lang="en-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>{css}</style></head><body>{body}</body></html>'
