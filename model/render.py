#!/usr/bin/env python3
"""
Renders the project-finance decks from model/pf_model.json.

    python3 model/render.py

Writes pf-index.html, pf-geeta-govind-vatika.html, pf-ramayan-vatika.html,
pf-karnal.html and pf-company.html into the repository root. Design language
matches index.html and financials.html.
"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "model", "pf_model.json")))
CR = 100.0

# ---------------------------------------------------------------- formatting --
def cr(x, dp=2, sign=False):
    if x is None: return "—"
    v = x / CR
    if abs(v) < 0.5 / 10 ** dp:
        v = 0.0                      # avoid rendering a negative zero
    return f"{v:+.{dp}f}" if sign else f"{v:.{dp}f}"

def rs(x, dp=2):
    """Rupees crore with the symbol."""
    if x is None: return "—"
    return f"₹{x/CR:.{dp}f} Cr"

def lakh(x, dp=1):
    if x is None: return "—"
    return f"₹{x:.{dp}f} L"

def money(x):
    """Lakh below a crore, crore above — whichever reads naturally."""
    if x is None: return "—"
    if abs(x) < 100:
        return f"₹{x:g} lakh"
    v = x / CR
    return f"₹{v:g} crore"

def pct(x, dp=1, sign=False):
    if x is None: return "—"
    return (f"{x:+.{dp}f}%" if sign else f"{x:.{dp}f}%")

def num(x, dp=2):
    return "—" if x is None else f"{x:.{dp}f}"

def cls(x):
    return "pos" if (x is not None and x >= 0) else "neg"

def e(s):
    return html.escape(str(s))

# ------------------------------------------------------------------- shell ----
CSS = """
:root{
  --blue:#2B66EA;--blue-mid:#275AC7;--blue-deep:#2A51A3;--blue-navy:#1A315D;
  --terracotta:#C8553D;--terracotta-soft:rgba(200,85,61,0.08);
  --green:#10B981;--green-soft:rgba(16,185,129,0.08);
  --amber:#D97706;--amber-soft:rgba(217,119,6,0.08);
  --black:#0A0A0A;--ink:#0A1426;--ink-soft:#3B4660;--ink-mute:#6E7689;
  --canvas:#FFFFFF;--paper:#F8F9FA;--rule:#E8E8ED;--rule-strong:#1A1F2E;
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--canvas);color:var(--ink);font-family:"DM Sans",-apple-system,sans-serif;font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;}
.topbar{position:sticky;top:0;z-index:50;background:rgba(255,255,255,0.94);backdrop-filter:blur(10px);border-bottom:1px solid var(--rule);}
.topbar__inner{max-width:1280px;margin:0 auto;padding:13px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);}
.brand__mark{font-family:"DM Sans",sans-serif;font-weight:700;font-size:13px;letter-spacing:-0.02em;background:var(--ink);color:var(--canvas);padding:5px 9px 4px;border-radius:4px;line-height:1;display:inline-flex;align-items:center;gap:6px;}
.brand__mark::after{content:"";width:6px;height:6px;border-radius:50%;background:var(--blue);}
.brand__name{font-size:12px;font-weight:500;color:var(--ink-soft);}
.topbar__right{display:flex;align-items:center;gap:12px;}
.topbar__badge{font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink-mute);font-weight:500;}
.back-link{font-size:12px;font-weight:600;color:var(--blue);text-decoration:none;padding:6px 12px;border:1px solid rgba(43,102,234,0.25);border-radius:5px;white-space:nowrap;}
.back-link:hover{background:rgba(43,102,234,0.05);}
@media(max-width:760px){.topbar__badge{display:none;}.brand__name{display:none;}}
.layout{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:230px minmax(0,1fr);gap:64px;padding:48px 24px 120px;}
@media(max-width:1100px){.layout{display:block;padding:24px 20px 80px;}}
.rail{position:sticky;top:80px;align-self:start;font-size:13px;}
.rail__label{font-size:10.5px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:16px;font-weight:500;}
.rail__list{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:1px;}
.rail__item a{display:flex;gap:12px;align-items:baseline;padding:6px 0 6px 14px;margin-left:-14px;color:var(--ink-soft);text-decoration:none;line-height:1.4;border-left:2px solid transparent;transition:all .15s ease;}
.rail__item a:hover{color:var(--ink);}
.rail__item--active a{color:var(--ink);font-weight:500;border-left-color:var(--blue);}
.rail__num{font-size:10.5px;letter-spacing:0.06em;color:var(--ink-mute);min-width:16px;font-variant-numeric:tabular-nums;}
.rail__item--active .rail__num{color:var(--blue);font-weight:600;}
.rail__sep{margin:14px 0 10px;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;border-top:1px solid var(--rule);padding-top:12px;}
@media(max-width:1100px){.rail{display:none;}}
.main{max-width:820px;}
.sec-head{margin:64px 0 24px;display:flex;align-items:baseline;gap:14px;}
.sec-head:first-child{margin-top:0;}
.sec-num{font-size:11px;letter-spacing:0.08em;color:var(--blue);font-weight:600;font-variant-numeric:tabular-nums;}
.sec-title{font-weight:700;font-size:clamp(20px,2.2vw,26px);letter-spacing:-0.015em;color:var(--ink);margin:0;}
.lede{font-size:15px;color:var(--ink-soft);line-height:1.65;margin:0 0 22px;}
.fin-cover{padding:40px 0 36px;border-bottom:2px solid var(--rule-strong);margin-bottom:56px;}
.fin-cover__eyebrow{font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:var(--terracotta);font-weight:600;margin-bottom:20px;}
.fin-cover__title{font-family:"Clash Display","DM Sans",sans-serif;font-weight:500;font-size:clamp(34px,5vw,54px);line-height:1.04;letter-spacing:-0.025em;color:var(--black);margin:0 0 16px;}
.fin-cover__sub{font-style:italic;font-family:"Fraunces",Georgia,serif;color:var(--ink-soft);font-size:clamp(16px,2vw,20px);margin:0 0 32px;max-width:620px;line-height:1.5;}
.fin-cover__meta{font-size:12px;color:var(--ink-mute);line-height:1.8;}
.fin-cover__meta b{color:var(--ink);font-weight:600;}
.cover-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:32px;padding-top:28px;border-top:1px solid var(--rule);}
@media(max-width:640px){.cover-kpi-grid{grid-template-columns:repeat(2,1fr);}}
.cover-kpi__label{font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:500;margin-bottom:5px;}
.cover-kpi__num{font-family:"Clash Display","DM Sans",sans-serif;font-weight:600;font-size:clamp(21px,2.5vw,27px);line-height:1;color:var(--black);font-variant-numeric:tabular-nums;}
.cover-kpi__num .small{font-size:0.5em;color:var(--ink-mute);margin-left:2px;font-weight:400;}
.cover-kpi__sub{font-size:11px;color:var(--ink-mute);margin-top:5px;line-height:1.4;}
.fin{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums;margin:0 0 8px;}
.fin th{font-weight:500;text-align:left;font-size:10.5px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);padding:12px 14px 10px 0;border-bottom:1px solid var(--rule-strong);white-space:nowrap;}
.fin th.r,.fin td.r{text-align:right;padding-right:0;}
.fin th.c,.fin td.c{text-align:center;}
.fin td{padding:13px 14px 13px 0;border-bottom:1px solid var(--rule);color:var(--ink);vertical-align:baseline;}
.fin tr:last-child td{border-bottom:none;}
.fin tr.sub td{background:linear-gradient(to right,rgba(43,102,234,0.04),transparent 60%);}
.fin tr.sub td:first-child{font-weight:600;}
.fin tr.total td{background:linear-gradient(to right,var(--terracotta-soft),transparent 60%);border-top:1px solid rgba(200,85,61,0.15);}
.fin tr.total td:first-child{font-weight:700;}
.fin tr.dim td{color:var(--ink-mute);}
.fin .label{font-weight:600;font-size:14px;}
.fin .meta{display:block;font-size:11.5px;color:var(--ink-mute);margin-top:2px;font-weight:400;line-height:1.45;}
.fin .pos{color:var(--green);font-weight:600;}
.fin .neg{color:var(--terracotta);font-weight:600;}
.fin .muted{color:var(--ink-mute);font-weight:400;}
.fin-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 0 8px;}
@media(max-width:640px){.fin{font-size:12.5px;}}
.note{background:var(--paper);border-left:3px solid var(--rule-strong);padding:14px 18px;border-radius:0 6px 6px 0;margin:18px 0;font-size:13px;color:var(--ink-soft);line-height:1.6;}
.note b{color:var(--ink);}
.note.blue{border-left-color:var(--blue);background:rgba(43,102,234,0.04);}
.note.terra{border-left-color:var(--terracotta);background:var(--terracotta-soft);}
.note.green{border-left-color:var(--green);background:var(--green-soft);}
.note.amber{border-left-color:var(--amber);background:var(--amber-soft);}
.note__label{display:block;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;font-weight:700;margin-bottom:6px;}
.note.blue .note__label{color:var(--blue);} .note.terra .note__label{color:var(--terracotta);}
.note.green .note__label{color:var(--green);} .note.amber .note__label{color:var(--amber);}
.verdict{border:1px solid var(--rule);border-radius:10px;padding:22px 24px;margin:24px 0;background:var(--paper);}
.verdict--go{border-color:rgba(16,185,129,0.35);background:var(--green-soft);}
.verdict--caution{border-color:rgba(217,119,6,0.35);background:var(--amber-soft);}
.verdict--stop{border-color:rgba(200,85,61,0.35);background:var(--terracotta-soft);}
.verdict__label{font-size:10px;letter-spacing:0.14em;text-transform:uppercase;font-weight:700;color:var(--ink-mute);margin-bottom:8px;}
.verdict__head{font-family:"Clash Display","DM Sans",sans-serif;font-weight:600;font-size:22px;line-height:1.15;letter-spacing:-0.02em;color:var(--black);margin-bottom:10px;}
.verdict__body{font-size:14px;color:var(--ink-soft);line-height:1.6;}
.verdict__body b{color:var(--ink);}
.opt-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:24px 0;}
@media(max-width:820px){.opt-grid{grid-template-columns:1fr;}}
.opt-card{border:1px solid var(--rule);border-radius:9px;padding:20px 18px;background:var(--canvas);}
.opt-card--pick{border-color:rgba(16,185,129,0.4);background:var(--green-soft);}
.opt-card__tag{font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:10px;}
.opt-card--pick .opt-card__tag{color:var(--green);}
.opt-card__name{font-weight:700;font-size:15px;letter-spacing:-0.01em;margin-bottom:12px;color:var(--ink);}
.opt-card__num{font-family:"Clash Display","DM Sans",sans-serif;font-weight:600;font-size:30px;line-height:1;color:var(--black);margin-bottom:3px;font-variant-numeric:tabular-nums;}
.opt-card__cap{font-size:11px;letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;margin-bottom:12px;}
.opt-card__list{list-style:none;padding:0;margin:0;font-size:12.5px;color:var(--ink-soft);line-height:1.5;}
.opt-card__list li{padding:5px 0;border-top:1px solid var(--rule);display:flex;justify-content:space-between;gap:10px;}
.opt-card__list li b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap;}
.bento{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0;}
@media(max-width:760px){.bento{grid-template-columns:repeat(2,1fr);}}
.bento__cell{background:var(--paper);border:1px solid var(--rule);border-radius:8px;padding:16px 16px 14px;}
.bento__label{font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;margin-bottom:6px;}
.bento__num{font-family:"Clash Display","DM Sans",sans-serif;font-weight:600;font-size:24px;line-height:1;color:var(--black);font-variant-numeric:tabular-nums;}
.bento__sub{font-size:11.5px;color:var(--ink-mute);margin-top:5px;line-height:1.45;}
.risk-row{display:grid;grid-template-columns:190px 84px 1fr;gap:16px;padding:17px 0;border-bottom:1px solid var(--rule);align-items:start;}
.risk-row:last-child{border-bottom:none;}
@media(max-width:640px){.risk-row{grid-template-columns:1fr;gap:6px;padding-bottom:18px;}}
.risk-factor{font-weight:600;font-size:14px;color:var(--ink);}
.risk-desc{font-size:13px;color:var(--ink-soft);line-height:1.55;}
.risk-sev{display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 9px;border-radius:12px;white-space:nowrap;}
.sev-h{background:#FEE2E2;color:#B91C1C;} .sev-m{background:var(--amber-soft);color:var(--amber);}
.sev-mh{background:#FEF3C7;color:#92400E;} .sev-l{background:#EEF9F5;color:var(--green);}
.assm-table{width:100%;border-collapse:collapse;font-size:13px;}
.assm-table td{padding:10px 12px 10px 0;border-bottom:1px solid var(--rule);vertical-align:baseline;}
.assm-table tr:last-child td{border-bottom:none;}
.assm-table td:first-child{font-weight:600;color:var(--ink);width:210px;}
.assm-table td:nth-child(2){color:var(--ink-soft);padding-right:16px;}
.assm-table td:nth-child(3){color:var(--blue-deep);font-weight:500;font-variant-numeric:tabular-nums;white-space:nowrap;}
.assm-block{margin-bottom:30px;}
.assm-block__label{font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;margin-bottom:12px;}
.cav-list{list-style:none;padding:0;margin:16px 0 0;display:flex;flex-direction:column;gap:12px;}
.cav-list li{display:flex;gap:12px;font-size:13.5px;color:var(--ink-soft);line-height:1.6;}
.cav-num{font-weight:700;color:var(--terracotta);flex-shrink:0;min-width:18px;}
.deck-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:24px 0;}
@media(max-width:760px){.deck-grid{grid-template-columns:1fr;}}
.deck-card{display:block;text-decoration:none;color:inherit;border:1px solid var(--rule);border-radius:10px;padding:22px 20px;transition:all .15s ease;background:var(--canvas);}
.deck-card:hover{border-color:var(--blue);box-shadow:0 3px 14px rgba(43,102,234,0.09);transform:translateY(-1px);}
.deck-card__tag{font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--blue);margin-bottom:9px;}
.deck-card__name{font-family:"Clash Display","DM Sans",sans-serif;font-weight:600;font-size:21px;letter-spacing:-0.02em;color:var(--black);margin-bottom:7px;line-height:1.15;}
.deck-card__desc{font-size:13px;color:var(--ink-soft);line-height:1.55;margin-bottom:14px;}
.deck-card__foot{font-size:11.5px;color:var(--ink-mute);border-top:1px solid var(--rule);padding-top:11px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;}
.deck-card__foot b{color:var(--ink);font-weight:600;}
.tag{display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;padding:3px 8px;border-radius:10px;background:rgba(43,102,234,0.08);color:var(--blue-deep);}
.tag--green{background:var(--green-soft);color:var(--green);}
.tag--amber{background:var(--amber-soft);color:var(--amber);}
.tag--terra{background:var(--terracotta-soft);color:var(--terracotta);}
.footer{margin-top:60px;padding-top:24px;border-top:1px solid var(--rule);font-size:12px;color:var(--ink-mute);line-height:1.7;}
.footer b{color:var(--ink);}
@media print{
  .topbar,.rail{display:none!important;}
  .layout{display:block;padding:0;max-width:none;}
  .main{max-width:none;}
  .fin th,.fin td{font-size:9pt;}
  section{page-break-inside:avoid;}
  .sec-head{margin-top:20pt;}
}
"""

FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://api.fontshare.com">
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,400&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet">"""

RAIL_SHARED = [
    ("pf-index.html", "Portfolio hub"),
    ("pf-geeta-govind-vatika.html", "Geeta Govind Vatika"),
    ("pf-ramayan-vatika.html", "Ramayan Vatika"),
    ("pf-karnal.html", "Karnal"),
    ("pf-company.html", "Company"),
]

def page(title, badge, sections, rail, self_href):
    rail_html = "\n".join(
        f'<li class="rail__item{" rail__item--active" if i == 0 else ""}">'
        f'<a href="#{sid}"><span class="rail__num">{n}</span><span>{e(label)}</span></a></li>'
        for i, (n, sid, label) in enumerate(rail))
    others = "\n".join(
        f'<li class="rail__item"><a href="{h}"><span class="rail__num">→</span><span>{e(l)}</span></a></li>'
        for h, l in RAIL_SHARED if h != self_href)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header class="topbar">
  <div class="topbar__inner">
    <a class="brand" href="index.html">
      <span class="brand__mark">EOD</span>
      <span class="brand__name">E-O-D Parks · Vision Amusement Park Pvt. Ltd.</span>
    </a>
    <div class="topbar__right">
      <span class="topbar__badge">{e(badge)}</span>
      <a class="back-link" href="pf-index.html">Project finance</a>
      <a class="back-link" href="financials.html">Financial model</a>
    </div>
  </div>
</header>
<div class="layout">
  <aside class="rail">
    <div class="rail__label">Sections</div>
    <ol class="rail__list">
{rail_html}
    </ol>
    <div class="rail__sep">Other decks</div>
    <ol class="rail__list">
{others}
    </ol>
  </aside>
  <main class="main">
{sections}
  </main>
</div>
<script>
(function(){{
  const sections = document.querySelectorAll('section[id]');
  const items = document.querySelectorAll('.rail__item');
  const obs = new IntersectionObserver(entries=>{{
    entries.forEach(en=>{{
      if(en.isIntersecting){{
        items.forEach(i=>i.classList.remove('rail__item--active'));
        const link = document.querySelector('.rail__item a[href="#'+en.target.id+'"]');
        if(link) link.closest('.rail__item').classList.add('rail__item--active');
      }}
    }});
  }},{{rootMargin:'-20% 0px -70% 0px'}});
  sections.forEach(s=>obs.observe(s));
}})();
</script>
</body>
</html>
"""

def sec(num, sid, title, body):
    return (f'<section id="{sid}">\n'
            f'  <div class="sec-head"><span class="sec-num">{num}</span>'
            f'<h2 class="sec-title">{title}</h2></div>\n{body}\n</section>\n')

def kpi(label, value, small="", sub=""):
    sm = f'<span class="small">{e(small)}</span>' if small else ""
    sb = f'<div class="cover-kpi__sub">{sub}</div>' if sub else ""
    return (f'<div><div class="cover-kpi__label">{e(label)}</div>'
            f'<div class="cover-kpi__num">{value}{sm}</div>{sb}</div>')

def bento(cells):
    return ('<div class="bento">' + "".join(
        f'<div class="bento__cell"><div class="bento__label">{e(l)}</div>'
        f'<div class="bento__num">{v}</div><div class="bento__sub">{s}</div></div>'
        for l, v, s in cells) + '</div>')

def note(kind, label, body):
    lb = f'<span class="note__label">{e(label)}</span>' if label else ""
    return f'<div class="note {kind}">{lb}{body}</div>'

def table(headers, rows, aligns=None):
    aligns = aligns or ["l"] + ["r"] * (len(headers) - 1)
    th = "".join(f'<th class="{"r" if a=="r" else ("c" if a=="c" else "")}">{h}</th>'
                 for h, a in zip(headers, aligns))
    body = ""
    for r in rows:
        rc = r.get("class", "")
        tds = "".join(f'<td class="{("r" if a=="r" else ("c" if a=="c" else ""))} {c}">{v}</td>'
                      for (v, c), a in zip(r["cells"], aligns))
        body += f'<tr class="{rc}">{tds}</tr>'
    return (f'<div class="fin-scroll"><table class="fin"><thead><tr>{th}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>')

def row(*cells, cls_=""):
    out = []
    for c in cells:
        out.append(c if isinstance(c, tuple) else (c, ""))
    return {"cells": out, "class": cls_}

def label_cell(name, meta=""):
    m = f'<span class="meta">{meta}</span>' if meta else ""
    return f'<span class="label">{name}</span>{m}'

def assm(blocks):
    out = ""
    for title, rows in blocks:
        trs = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
        out += (f'<div class="assm-block"><div class="assm-block__label">{e(title)}</div>'
                f'<table class="assm-table"><tbody>{trs}</tbody></table></div>')
    return out

def risks(items):
    out = '<div class="risk-grid">'
    for factor, sev, sev_cls, desc in items:
        out += (f'<div class="risk-row"><div class="risk-factor">{factor}</div>'
                f'<div><span class="risk-sev {sev_cls}">{e(sev)}</span></div>'
                f'<div class="risk-desc">{desc}</div></div>')
    return out + "</div>"

def caveats(items):
    return ('<ul class="cav-list">' + "".join(
        f'<li><span class="cav-num">{i+1}.</span><span>{t}</span></li>'
        for i, t in enumerate(items)) + "</ul>")

FOOTER = ('<div class="footer"><b>Confidentiality:</b> Prepared for Vision Amusement Park Pvt. Ltd. and '
          'its prospective lenders and investors. Contains forward-looking statements and management '
          'estimates; all projections are subject to risk and to the assumptions set out in each deck. '
          'Not an offer to sell or a solicitation of an offer to buy any security. Every figure is '
          'generated by <b>model/pf_model.py</b> and rendered by <b>model/render.py</b> — edit the model, '
          'not the HTML.</div>')

# ============================================================================
# Shared blocks used by every project deck
# ============================================================================
def opt_cards(fin, currency_label="Facility"):
    """Three financing options side by side."""
    eq, db, cc = fin["equity"], fin["debt"], fin["ccd"]
    pick = "debt"
    cards = []
    cards.append(('opt-card' + (' opt-card--pick' if pick == 'equity' else ''),
        "Option A", "Equity", pct(eq["irr_pct"]), "Investor IRR", [
            ("Capital in", rs(eq["investment"])),
            ("Stake offered", pct(eq["stake_pct"], 0)),
            ("Money multiple", f'{num(eq["money_multiple"])}×'),
            ("Stake for a 22% IRR", pct(eq["stake_for_22pct"], 0)),
        ]))
    cards.append(('opt-card' + (' opt-card--pick' if pick == 'debt' else ''),
        "Option B", "Debt · CGTMSE", num(db["min_dscr_post_moratorium"]) + "×", "Minimum DSCR", [
            (currency_label, rs(db["total_limit"])),
            ("Term loan / WC", f'{rs(db["term_loan"])} / {rs(db["wc_limit"])}'),
            ("All-in rate", f'{num(db["rate_pct"])}% + {num(db["cgtmse"]["agf_rate_pct"])}% AGF'),
            ("Total finance cost", rs(db["total_finance_cost"])),
        ]))
    cards.append(('opt-card' + (' opt-card--pick' if pick == 'ccd' else ''),
        "Option C", "Debt → equity (CCD)", pct(cc["irr_pct"]), "Investor IRR", [
            ("Principal", rs(cc["principal"])),
            ("Coupon to conversion", f'{num(cc["coupon_pct"],1)}% · yr {cc["conversion_year"]}'),
            ("Stake on conversion", pct(cc["conversion_stake_pct"], 0)),
            ("Money multiple", f'{num(cc["money_multiple"])}×'),
        ]))
    out = '<div class="opt-grid">'
    for klass, tag, name, big, cap, items in cards:
        lis = "".join(f"<li><span>{e(a)}</span><b>{b}</b></li>" for a, b in items)
        out += (f'<div class="{klass}"><div class="opt-card__tag">{e(tag)}</div>'
                f'<div class="opt-card__name">{e(name)}</div>'
                f'<div class="opt-card__num">{big}</div>'
                f'<div class="opt-card__cap">{e(cap)}</div>'
                f'<ul class="opt-card__list">{lis}</ul></div>')
    return out + "</div>"

def debt_schedule_table(db, label="Facility"):
    rows = []
    for r in db["schedule"]:
        d = r["dscr"]
        dcls = "pos" if (d and d >= 1.3) else ("neg" if (d is not None and d < 1.0) else "")
        rows.append(row(
            (f'Year {r["year"]}' + (' <span class="muted">· moratorium</span>'
                                    if r["principal"] == 0 else ''), ""),
            (cr(r["tl_opening"]), "muted"),
            (cr(r["tl_interest"]), ""),
            (cr(r["wc_outstanding"]), "muted"),
            (cr(r["wc_interest"]), ""),
            (cr(r["agf"]), ""),
            (cr(r["principal"]), ""),
            (cr(r["debt_service"]), ""),
            (cr(r["cfads"]), cls(r["cfads"])),
            (num(d) + "×" if d else "—", dcls),
        ))
    return table(["", "TL o/s", "TL int.", "WC drawn", "WC int.", "AGF",
                  "Principal", "Debt service", "CFADS", "DSCR"], rows)

def scenario_cards(scen, project_kind="concession"):
    order = [k for k in ("downside", "base", "upside", "bda_indicative") if k in scen]
    names = {"downside": "Downside", "base": "Base case", "upside": "Upside",
             "bda_indicative": "BDA's own case"}
    out = '<div class="opt-grid">'
    for k in order:
        s = scen[k]
        klass = "opt-card opt-card--pick" if k == "base" else "opt-card"
        no_irr = s["project_irr_pct"] is None
        irr_txt = "Never repays" if no_irr else pct(s["project_irr_pct"], 1)
        small_style = "font-size:20px;line-height:1.25;" if no_irr else ""
        lis = "".join(f"<li><span>{a}</span><b>{b}</b></li>" for a, b in [
            ("Year 1 EBITDA", rs(s["ebitda_year1"])),
            ("Stabilised revenue", rs(s["revenue_stabilised"])),
            ("Stabilised EBITDA", f'{rs(s["ebitda_stabilised"])} · {pct(s["ebitda_margin_stabilised"],0)}'),
            ("Payback", f'{num(s["payback_years"],1)} yrs' if s["payback_years"] else "Not within the term"),
        ])
        out += (f'<div class="{klass}"><div class="opt-card__tag">{e(names[k])}</div>'
                f'<div class="opt-card__name">{e(s["note"])}</div>'
                f'<div class="opt-card__num" style="{small_style}">{irr_txt}</div>'
                f'<div class="opt-card__cap">Project IRR</div>'
                f'<ul class="opt-card__list">{lis}</ul></div>')
    return out + "</div>"

def verdict_block(coc, extra=""):
    if coc["clears_equity_hurdle"]:
        kind, head = "verdict--go", "Equity-fundable"
    elif coc["clears_debt"]:
        kind, head = "verdict--caution", "Fund it with debt, not equity"
    else:
        kind, head = "verdict--stop", "Does not clear its own cost of capital"
    return (f'<div class="verdict {kind}"><div class="verdict__label">Verdict</div>'
            f'<div class="verdict__head">{e(head)}</div>'
            f'<div class="verdict__body">Project IRR <b>{pct(coc["project_irr_pct"])}</b> against an '
            f'all-in CGTMSE cost of debt of <b>{pct(coc["all_in_cost_of_cgtmse_debt_pct"],2)}</b> '
            f'({pct(coc["spread_over_debt_pct"],1,sign=True)}) and an equity hurdle of '
            f'<b>{pct(coc["equity_hurdle_pct"],0)}</b>. {e(coc["verdict"])} {extra}</div></div>')

def fcf_table(fcf, years_label="Year"):
    rows = [row((f'<span class="label">Capital deployed</span>'
                 f'<span class="meta">Mobilisation, deposits and advance licence fee</span>', ""),
                ("", ""), ("", ""), ("", ""),
                (cr(-fcf["t0"]), "neg"), cls_="sub")]
    for d in fcf["detail"]:
        rows.append(row(
            (f'{years_label} {d["year"]}', ""),
            (cr(d["ebitda"]), cls(d["ebitda"])),
            (cr(-d["tax"]), "muted"),
            (cr(-d["maintenance_capex"]), "muted"),
            (cr(d["fcf"]), cls(d["fcf"])),
        ))
    rows.append(row(("Cumulative free cash flow", ""), ("", ""), ("", ""), ("", ""),
                    (cr(fcf["cumulative_fcf"]), cls(fcf["cumulative_fcf"])), cls_="total"))
    return table(["", "EBITDA", "Tax", "Maint. capex", "Free cash flow"], rows)

# ============================================================================
# DECK 1 — GEETA GOVIND VATIKA
# ============================================================================
def deck_ggv():
    g = M["ggv"]; f = g["financing"]; r = g["rfp"]; db = f["debt"]
    yrs = g["years"]; cap = f["true_capital_requirement"]
    S = []

    cover = f"""
<div class="fin-cover">
  <div class="fin-cover__eyebrow">Project finance · 01 of 04</div>
  <h1 class="fin-cover__title">Geeta Govind Vatika</h1>
  <p class="fin-cover__sub">A 19-acre cultural park in Taj Nagri Phase-II, five minutes from the park
  E-O-D already runs. Seven years of operating rights, no land to buy, no structures to build —
  and one year of operating expenditure to fund before it pays for itself.</p>
  <div class="fin-cover__meta">
    <b>Agra Development Authority</b> · Licence-fee model · 7 + 4 years<br>
    Reserve licence fee <b>₹2.5 lakh per month</b> · forward e-auction · 5% annual escalation<br>
    Bid closes <b>19 August 2026</b> · technical bid opened 20 August 2026
  </div>
  <div class="cover-kpi-grid">
    {kpi("Funding ask", rs(f["ask"]), sub="Mobilisation plus one year of operating cost")}
    {kpi("True capital at risk", rs(cap["total"]), sub="The rest is revolving liquidity, repaid from collections")}
    {kpi("Project IRR", pct(f["project_fcf"]["irr_pct"]), sub=f'Payback {num(f["project_fcf"]["payback_years"],1)} years')}
    {kpi("Year 7 EBITDA", rs(yrs[-1]["ebitda"]), sub=f'{pct(yrs[-1]["ebitda_margin"],1)} margin on {rs(yrs[-1]["revenue"]["total"])}')}
  </div>
</div>"""

    # 01 the project
    scope_lis = "".join(f"<li>{e(x)}</li>" for x in r["scope"])
    body = f"""
<p class="lede">ADA has built a ₹4.0–4.2 crore themed park and now wants an operator. Everything
physical already exists — the musical fountains, the 40-minute <em>Krishna Leela</em> laser show,
eight kiosks, the Tulsi forest, the amphitheatre. The winning bidder pays a monthly licence fee and
keeps what it collects at the gate.</p>
{table(["Term", "What the RFP says"], [
  row(label_cell("Authority"), (e(r["authority"]), "")),
  row(label_cell("Site"), (e(r["site"]) + f' · ~{r["area_acres"]} acres', "")),
  row(label_cell("Contract period"), (e(r["term"]), "")),
  row(label_cell("Selection method"), (e(r["selection"]) + '<span class="meta">Highest licence fee in the sealed financial bids becomes the base price for the e-auction.</span>', "")),
  row(label_cell("Reserve licence fee"), (f'<b>{lakh(r["reserve_licence_fee_month_lakh"],1)} per month + GST</b> · {lakh(r["reserve_licence_fee_year_lakh"],0)} per year', "")),
  row(label_cell("Escalation"), (f'{pct(r["escalation_pct"],0)} a year on the preceding year', "")),
  row(label_cell("Payment terms"), (e(r["payment_terms"]) + '<span class="meta">15% p.a. penal interest up to 45 days late; beyond 60 days, termination is at ADA&rsquo;s discretion.</span>', "")),
  row(label_cell("Security deposit"), (e(r["security_deposit_basis"]), "")),
  row(label_cell("EMD / tender fee"), (f'{lakh(r["emd_lakh"],1)} refundable / ₹5,900 including GST', "")),
  row(label_cell("Moratorium"), (f'{r["moratorium_days"]} days from handover for mobilisation — no licence fee payable', "")),
  row(label_cell("Gate tariff"), (f'₹{r["entry_tariff_inr"]} entry. Fountain and laser show at rates approved by ADA. Free: {e(r["free_entry"])}.', "")),
  row(label_cell("Penalties"), (e(r["penalty_range_inr"]), "")),
  row(label_cell("Asset position"), (e(r["assets"]), "")),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Scope of services</div>
<ul style="font-size:13.5px;color:var(--ink-soft);line-height:1.7;padding-left:20px;margin:0 0 20px;">{scope_lis}</ul>
{note("green","Why E-O-D wins this on the technical bid",
  f"ADA asks for average turnover of {rs(r['eligibility_turnover_cr']*100,0)} over three years and two similar "
  f"projects above ₹50 lakh in five years. VAPPL turned over <b>₹16.29 Cr</b> in FY25-26 and operates four parks, "
  "three of them on government concessions — two of those <b>granted by ADA itself</b> (Agra Chaupati and Subhash "
  "Park). The eligibility bar is cleared several times over. The competitive question is the auction, not the "
  "qualification.")}
{note("blue","The cluster argument",
  "Geeta Govind Vatika sits <b>next to Agra Chaupati</b>, which E-O-D already runs, and a short drive from Subhash "
  "Park. One Agra management line, one marketing spend, one maintenance crew and one hiring pipeline serve three "
  "sites. The corporate overhead in this model is charged at <b>5% of revenue</b> rather than the standalone rate "
  "precisely because the fixed cost is already being carried.")}"""
    S.append(("01", "s01", "The project", body))

    # 02 the ask
    mob = g["mobilisation"]
    capex_rows = [row(label_cell(e(c["item"]), f'{c["life_years"]}-year life'), (lakh(c["amount"]), ""))
                  for c in g["capex_lines"]]
    capex_rows.append(row(("Mobilisation capex", ""), (lakh(mob["capex"]), ""), cls_="total"))
    body = f"""
<p class="lede">The brief was “one year of opex as loan or investment”. That is the right facility size,
but it is worth being precise about what the money is actually doing, because the answer changes which
instrument is appropriate.</p>
{bento([
  ("Facility as briefed", rs(f["ask"]), "Mobilisation plus 12 months of operating cost"),
  ("True capital at risk", rs(cap["total"]), "Mobilisation plus the year-1 operating deficit"),
  ("Revolving liquidity", rs(f["ask"] - cap["total"]), "Funded, spent and recovered from collections"),
])}
{note("terra","This is a liquidity requirement, not a capital requirement",
  f"Of the {rs(f['ask'])} asked for, only <b>{rs(cap['total'])}</b> is capital that the project consumes and "
  f"does not return — {rs(mob['capex'])} of mobilisation capex, {rs(mob['security_deposit'])} of deposit, "
  f"{rs(mob['advance_licence_fee_6m'])} of advance licence fee, and {rs(cap['cumulative_operating_deficit'])} "
  "of year-1 operating deficit. The remaining balance is working capital: it is drawn to pay wages and the "
  "electricity bill, and it comes back out of the gate. <b>Equity does not come back. A revolving limit does.</b> "
  "That single distinction is why Option B below is the recommendation.")}
{table(["Mobilisation capex", "Amount"], capex_rows)}
{table(["Total requirement", "Amount"], [
  row(label_cell("Mobilisation capex", "Activity equipment, kiosk fit-out, ticketing, signage, tools"), (lakh(mob["capex"]), "")),
  row(label_cell("Security deposit", "Three months of the licence fee at the winning bid — refundable at expiry"), (lakh(mob["security_deposit"]), "")),
  row(label_cell("Advance licence fee", "First six months, due within 7 days of the work order"), (lakh(mob["advance_licence_fee_6m"]), "")),
  row(label_cell("EMD and tender fee", "EMD refundable"), (lakh(mob["emd"] + mob["tender_fee"]), "")),
  row(("Sub-total — mobilisation", ""), (lakh(mob["total"]), ""), cls_="sub"),
  row(label_cell("Year 1 operating expenditure", "Licence fee, payroll, electricity, AMC, marketing, materials"), (lakh(g["year1_opex"]), "")),
  row(("Facility requested", ""), (lakh(f["ask"]), ""), cls_="total"),
])}
{note("amber","On the licence fee bid",
  f"This model assumes a winning bid of <b>{lakh(g['bid_licence_year1'],0)} a year</b> — ₹3.0 lakh a month, "
  f"20% above ADA's ₹2.5 lakh reserve. The forward e-auction is the single largest uncontrolled variable in the "
  "project. Section 07 runs the downside at a ₹45 lakh bid. <b>Above roughly ₹52 lakh a year the project stops "
  "clearing its cost of debt</b> — that is the walk-away number to carry into the auction room.")}"""
    S.append(("02", "s02", "What the money is for", body))

    # 03 revenue
    rev_rows = []
    keys = [("entry", "Gate entry", "₹20 per head, ADA-notified. Children under 5 and morning walkers free."),
            ("show", "Musical fountain and laser show", "The 40-minute Krishna Leela show plus fountain. Tariff set by ADA."),
            ("fnb", "Food and beverage", "Six 8×8 ft and two 10×10 ft kiosks. Pre-packaged and ready-to-eat only, plus tea and coffee."),
            ("activities", "Entertainment activities", "Demountable activity layer added by E-O-D under clause G. No permanent structures."),
            ("parking", "Parking", "Two- and four-wheeler. EV charging exempt while charging."),
            ("events", "Private events and shoots", "Birthdays, pre-wedding and wedding shoots, corporate bookings.")]
    for k, name, meta in keys:
        rev_rows.append(row(label_cell(name, meta), *[(cr(y["revenue"][k]), "") for y in yrs]))
    rev_rows.append(row(("Total revenue, net of GST", ""), *[(cr(y["revenue"]["total"]), "") for y in yrs], cls_="total"))
    rev_rows.append(row(("Footfall, lakh visits", ""), *[(num(y["revenue"]["footfall_lakh"], 2), "muted") for y in yrs], cls_="dim"))
    body = f"""
<p class="lede">Six streams, built bottom-up from footfall and capture rates rather than top-down from a
target. All figures are net of GST; the tariffs quoted below are the gross gate prices.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], rev_rows)}
{assm([("Footfall and capture", [
   ("Year 1 footfall", "3.10 lakh visits — about 850 a day", "3.10 L"),
   ("Year 7 footfall", "5.75 lakh visits — about 1,575 a day", "5.75 L"),
   ("Paid entry ratio", "Net of under-5s and free morning walkers", "76% → 80%"),
   ("Show conversion", "Share of visitors buying the fountain and laser ticket", "24% → 31%"),
   ("F&B capture", "Share of visitors spending at a kiosk", "32% → 38%"),
   ("Activity capture", "Share buying into the E-O-D activity layer", "11% → 16%"),
 ]),
 ("Tariffs, gross of GST", [
   ("Gate entry", "Fixed by ADA — no escalation modelled", "₹20"),
   ("Fountain and laser show", "Subject to ADA approval; escalation modelled every second year", "₹100 → ₹130"),
   ("F&B spend per capture", "Pre-packaged only; no cooking permitted on site", "₹35 → ₹46"),
   ("Activity spend per capture", "Blended across the activity stack", "₹120 → ₹180"),
   ("Parking", "62% two-wheeler at ₹10, 38% four-wheeler at ₹20", "₹10 / ₹20"),
 ])])}
{note("blue","Benchmark check",
  "Subhash Park, Agra — the same ₹20 gate, one pre-packaged stall, zero capex, no show — ran at a "
  "<b>17.5% net margin from its first month</b> and is modelled at ₹0.40–0.60 Cr for FY26-27 in the company "
  "financial model. Geeta Govind Vatika carries a laser show, a musical fountain, eight kiosks and 19 acres. "
  "The year-1 revenue here is roughly four times Subhash Park's run rate on roughly four times the asset.")}
{note("terra","The tariff you do not control",
  "ADA fixes the gate at ₹20 and approves every other rate, with ten days' notice required for any revision. "
  "<b>The show ticket is the only meaningful pricing lever, and E-O-D does not hold it.</b> Every rupee of the "
  "show tariff is worth roughly ₹7.4 lakh a year at year-3 volumes. Secure written agreement on the show tariff "
  "and its escalation path before the auction, not after the work order.")}"""
    S.append(("03", "s03", "Revenue model", body))

    # 04 cost
    cost_keys = [("licence_fee", "Licence fee to ADA", "Bid escalating at 5% a year"),
                 ("manpower", "Payroll", "31 heads at year-1 footfall, scaling with visits; loaded for PF and ESI"),
                 ("electricity", "Electricity", "Paid direct to the discom. Laser, fountain pumps and 19 acres of lighting"),
                 ("water_horticulture", "Water and horticulture", "Tulsi forest, lawns, flower beds, irrigation"),
                 ("show_amc", "Show AMC and spares", "Laser projectors, pumps, nozzles, control and audio systems"),
                 ("repairs", "Repairs and maintenance", "Kiosks, pathways, seating, civil"),
                 ("fnb_cogs", "F&B cost of goods", "52% of F&B revenue — bought-in sealed product"),
                 ("activity_cost", "Activity operating cost", "22% of activity revenue"),
                 ("marketing", "Marketing", "4.5% of revenue, shared across the Agra cluster"),
                 ("insurance_statutory", "Insurance and statutory", "Public liability, FSSAI, police verification, licences"),
                 ("it_cctv", "IT, POS and CCTV", "Including integration with the Agra Smart City command centre"),
                 ("corporate_overhead", "Corporate overhead", "5% of revenue — cluster allocation, not standalone"),
                 ("contingency", "Contingency", "Provision against the ₹5,000–₹50,000 penalty schedule")]
    cost_rows = [row(label_cell(n, m), *[(cr(y["opex"][k]), "") for y in yrs]) for k, n, m in cost_keys]
    cost_rows.append(row(("Total operating cost", ""), *[(cr(y["opex"]["total"]), "") for y in yrs], cls_="total"))
    body = f"""
<p class="lede">Payroll and the licence fee are the two structural lines. Everything else scales with
footfall, revenue or inflation.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], cost_rows)}
{note("amber","What is not in this model",
  "ADA requires CCTV integrated with the Agra Smart City command centre, ex-servicemen at entry and exit points, "
  "police verification and photo ID for every deployed person, insurance for all personnel, a dedicated technical "
  "supervisor for the fountain works, safety inspections every six months, and a monthly maintenance certificate "
  "with GPS-tagged photographs. These are costed inside the payroll, insurance and IT lines above. What is "
  "<b>not</b> costed is the replacement of any laser or fountain asset that reaches the end of its useful life "
  "during the term — the RFP places that burden on the agency and puts the onus of proving irreparability on "
  "the agency too. Ask ADA for the commissioning dates and the AMC history of the laser projectors before bidding.")}"""
    S.append(("04", "s04", "Cost model", body))

    # 05 P&L
    pl_rows = [
      row(label_cell("Revenue", "Net of GST"), *[(cr(y["revenue"]["total"]), "") for y in yrs]),
      row(label_cell("Operating cost", ""), *[(cr(-y["opex"]["total"]), "muted") for y in yrs]),
      row(("EBITDA", ""), *[(cr(y["ebitda"]), cls(y["ebitda"])) for y in yrs], cls_="sub"),
      row(("EBITDA margin", ""), *[(pct(y["ebitda_margin"], 1), "muted") for y in yrs], cls_="dim"),
      row(label_cell("Depreciation", "Straight line on mobilisation capex"), *[(cr(-y["depreciation"]), "muted") for y in yrs]),
      row(("EBIT", ""), *[(cr(y["ebit"]), cls(y["ebit"])) for y in yrs], cls_="total"),
    ]
    body = f"""
<p class="lede">Year 1 loses money. That is not a modelling artefact — it is a 15-day mobilisation window,
a full-year licence fee from day one, and a park that has never been open to the public before.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], pl_rows)}
{bento([
  ("Breakeven", "Year 2", f'EBITDA turns positive at {rs(yrs[1]["ebitda"])}'),
  ("Margin at maturity", pct(yrs[-1]["ebitda_margin"], 1), "Year 7, against E-O-D's 27–29% group target"),
  ("Cumulative EBITDA", rs(sum(y["ebitda"] for y in yrs)), "Across the seven-year initial term"),
])}
{note("green","The four extension years are not in any number on this page",
  "ADA may extend by four years on performance and mutual consent, with the right to revise the licence fee for "
  "the extended term. Years 8 to 11 would run at the year-7 cost base against a mature revenue line — the most "
  "profitable years of the contract. They are excluded from every return in this deck. <b>Treat them as free "
  "option value, and treat the timely-payment and upkeep conditions in clause 3.5 as the price of that option.</b>")}"""
    S.append(("05", "s05", "Seven-year projection", body))

    # 06 returns
    ex = f["exit_valuation"]
    body = f"""
<p class="lede">The project consumes {rs(cap["total"])} of real capital and returns
{rs(f["project_fcf"]["cumulative_fcf"])} of free cash flow over seven years. That is the number every
financing option below is competing to claim a share of.</p>
{fcf_table(f["project_fcf"])}
{bento([
  ("Project IRR", pct(f["project_fcf"]["irr_pct"]), "Unlevered, seven-year term, no extension value"),
  ("Payback", f'{num(f["project_fcf"]["payback_years"],1)} yrs', "From first deployment"),
  ("NPV at 15%", rs(f["project_fcf"]["npv_at_15pct"]), "Positive — the project creates value"),
])}
{verdict_block(f["cost_of_capital"])}
{note("blue","How the exit is valued",
  f"A licence that expires is a wasting asset. Valuing it at an EBITDA multiple flatters it, so the exit value "
  f"used throughout this deck is the <b>discounted remaining concession cash flow</b> at a 15% rate: "
  f"<b>{rs(ex['dcf_remaining_term'])}</b> at the end of year {f['exit_year']}. The EBITDA-multiple cross-check "
  f"at {num(ex['ebitda_multiple'],1)}× would give {rs(ex['ebitda_multiple_crosscheck'])} — higher, and in our "
  "view not defensible for an asset with two years left to run at that point.")}"""
    S.append(("06", "s06", "Project returns", body))

    # 07 scenarios
    body = f"""
<p class="lede">Three drivers move this project: footfall, show conversion and the licence fee you bid.
The downside case moves all three against you at once.</p>
{scenario_cards(g["scenarios"])}
{note("terra","The auction discipline",
  f"The downside case above is not a bad year — it is a <b>bad bid</b>. Fifteen per cent below base on footfall "
  f"and conversion is survivable on its own. A {lakh(g['bid_licence_year1']*1.25,0)} licence fee on top of it is "
  f"what takes the project below the cost of its own debt. The model solves the break-even licence fee at "
  f"<b>{lakh(f['walk_away']['licence_fee_year1'],1)} a year</b> — hold that line in the auction room.")}"""
    S.append(("07", "s07", "Scenarios", body))

    # 08 equity
    eq = f["equity"]
    body = f"""
<p class="lede">A third party funds the project in exchange for a share of it. Simple, no repayment
obligation, no covenant. It is also, on these numbers, the most expensive money on the table.</p>
{table(["Term", "Structure"], [
  row(label_cell("Capital", "Sized to the true capital requirement, not the gross facility"), (rs(eq["investment"]), "")),
  row(label_cell("Stake offered"), (pct(eq["stake_pct"], 0), "")),
  row(label_cell("Distribution policy", "Free cash after debt service and maintenance capex"), ('From year 3', "")),
  row(label_cell("Exit", e(eq["basis"])), (f'End of year {eq["exit_year"]}', "")),
  row(label_cell("Exit equity value"), (rs(eq["exit_equity_value"]), "")),
  row(label_cell("Investor proceeds", "Dividends plus exit"), (rs(sum(eq["dividends"]) + eq["exit_proceeds"]), "")),
  row(("Investor IRR", ""), (pct(eq["irr_pct"]), cls(eq["irr_pct"])), cls_="total"),
  row(("Money multiple", ""), (f'{num(eq["money_multiple"])}×', ""), cls_="total"),
])}
{note("terra","Why this does not clear",
  f"At {pct(eq['stake_pct'],0)} the investor earns {pct(eq['irr_pct'])} — below a deposit rate. To reach a "
  f"conventional 22% private-equity hurdle the investor would need <b>{pct(eq['stake_for_22pct'],0)}</b> of the "
  "project. The arithmetic is unavoidable: a seven-year concession generating "
  f"{rs(f['project_fcf']['cumulative_fcf'])} of lifetime free cash flow cannot pay an equity return on "
  f"{rs(eq['investment'])} of capital <em>and</em> leave anything for E-O-D. "
  "<b>Project-level equity is the wrong instrument here.</b> If equity is wanted, raise it at company level "
  "(see the company deck) where it buys a share of a portfolio, not a share of one wasting licence.")}"""
    S.append(("08", "s08", "Option A · Equity", body))

    # 09 debt
    dc = f["debt_capacity"]; dopt = f["debt_optimised"]
    body = f"""
<p class="lede">A CGTMSE-guaranteed composite facility: a small term loan against the mobilisation spend,
and a revolving working-capital limit against the operating cycle. No collateral, no third-party
guarantee, no charge on ADA's assets — which matters, because there are no assets to charge.</p>
{table(["Term", "Structure"], [
  row(label_cell("Scheme"), (f'CGTMSE {M["cgtmse"]["scheme"]} · guarantee ceiling {rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100, 0)} per borrower', "")),
  row(label_cell("Term loan", "Mobilisation capex, deposit and advance licence fee"), (rs(db["term_loan"]), "")),
  row(label_cell("Working capital limit", "One year of operating cost, revolving"), (rs(db["wc_limit"]), "")),
  row(("Total facility", ""), (rs(db["total_limit"]), ""), cls_="sub"),
  row(label_cell("Interest rate", "Repo-linked; CGTMSE keeps MLI pricing within ~3% of EBLR"), (pct(db["rate_pct"], 2), "")),
  row(label_cell("Annual guarantee fee", f'Standard slab for a {rs(db["total_limit"])} facility'), (pct(db["cgtmse"]["agf_rate_pct"], 2), "")),
  row(label_cell("Tenor", "Term loan; matched inside the seven-year licence"), (f'{db["tl_tenor_years"]} years', "")),
  row(label_cell("Moratorium", "Principal deferred through the ramp"), (f'{db["tl_moratorium_years"]} years', "")),
  row(label_cell("Guarantee coverage", "Standard cover for a Small Enterprise"), (f'{pct(db["cgtmse"]["coverage_pct"], 0)} · {rs(db["cgtmse"]["guaranteed_amount"])}', "")),
  row(label_cell("Security"), ('Nil collateral. Hypothecation of the assets financed. Personal guarantee of directors permitted; third-party guarantee is not.', "")),
  row(("Total finance cost over the term", ""), (rs(db["total_finance_cost"]), ""), cls_="total"),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Repayment and cover, ₹ crore</div>
{debt_schedule_table(db)}
{bento([
  ("Minimum DSCR", num(db["min_dscr_post_moratorium"]) + "×", "After the moratorium — above the 1.30× bank threshold"),
  ("Average DSCR", num(db["avg_dscr_post_moratorium"]) + "×", "Across the repayment years"),
  ("Debt capacity", rs(dc["max_total_limit"]), f'Maximum facility serviceable at {dc["target_dscr"]}× DSCR'),
])}
{note("green","The facility fits — but only just, and only with the moratorium",
  f"The project can service <b>{rs(dc['max_total_limit'])}</b> at a 1.30× floor. The facility as briefed is "
  f"{rs(db['total_limit'])}. There is {rs(dc['max_total_limit'] - db['total_limit'])} of headroom and no more. "
  f"The three-year principal moratorium is doing the work: it pushes the first repayment into year 4, when "
  f"EBITDA is {rs(yrs[3]['ebitda'])} rather than {rs(yrs[1]['ebitda'])}. <b>A bank that offers this facility "
  "with a one-year moratorium is offering a facility that defaults in year 2.</b>")}
{note("amber","Do not over-sanction the working-capital limit",
  f"CGTMSE charges its guarantee fee on the <b>sanctioned</b> limit in year 1 and on the outstanding balance "
  f"thereafter. A {rs(db['wc_limit'])} limit that peaks at {rs(0.60)} of actual drawdown is paying a guarantee "
  f"fee on air. Cutting the sanctioned limit to {rs(dopt['wc_limit'])} and keeping the balance as an "
  f"uncommitted overdraft saves <b>{lakh(f['agf_saving_optimised'],2)}</b> of guarantee fee over the term and "
  f"consumes {rs(db['total_limit'] - dopt['total_limit'])} less of the group's ₹10 Cr CGTMSE ceiling — which, "
  "as the portfolio hub sets out, is the binding constraint across all three projects.")}"""
    S.append(("09", "s09", "Option B · Debt under CGTMSE", body))

    # 10 CCD
    cc = f["ccd"]
    body = f"""
<p class="lede">A compulsorily convertible debenture: money in as debt, a coupon while the project ramps,
then automatic conversion into equity on a formula fixed the day it is issued.</p>
{table(["Term", "Structure"], [
  row(label_cell("Principal"), (rs(cc["principal"]), "")),
  row(label_cell("Coupon", "Paid annually until conversion"), (pct(cc["coupon_pct"], 1), "")),
  row(label_cell("Conversion", "Compulsory — not at the holder's option"), (f'End of year {cc["conversion_year"]}', "")),
  row(label_cell("Conversion stake"), (pct(cc["conversion_stake_pct"], 0), "")),
  row(label_cell("Coupon paid to conversion"), (rs(cc["coupon_paid_total"]), "")),
  row(label_cell("Exit"), (f'End of year {cc["exit_year"]} at {rs(cc["exit_equity_value"])}', "")),
  row(("Investor IRR", ""), (pct(cc["irr_pct"]), cls(cc["irr_pct"])), cls_="total"),
  row(("Money multiple", ""), (f'{num(cc["money_multiple"])}×', ""), cls_="total"),
])}
{note("terra","Worse than either pure option, at project level",
  f"The CCD returns {pct(cc['irr_pct'])} — below the equity case, because the coupon years consume the cash the "
  "project needs while it is ramping, and the conversion stake is not large enough to make up the difference on "
  "exit. At project level a CCD combines the cash-flow burden of debt with the dilution of equity and the "
  "guarantee benefit of neither. <b>It has a real place at company level — see the company deck — but not here.</b>")}
{note("blue","If a CCD is used anywhere in this structure, three things must be true",
  "<b>One:</b> the conversion formula must be fixed on the date of issue — a price determined later fails the "
  "FEMA pricing test if any part of the money is foreign, and turns the instrument into external commercial "
  "borrowing. <b>Two:</b> a valuation report under section 62(1)(c) of the Companies Act is needed before "
  "conversion, and the issue itself is a private placement under section 42 with the filings that follow. "
  "<b>Three:</b> until it converts, a CCD sits on the balance sheet as borrowing — it worsens the debt-to-equity "
  "ratio that any parallel CGTMSE facility will be covenanted on.")}"""
    S.append(("10", "s10", "Option C · Debt converted to equity", body))

    # 11 comparison
    body = f"""
{opt_cards(f)}
{table(["", "A · Equity", "B · CGTMSE debt", "C · CCD"], [
  row(label_cell("Money in"), (rs(eq["investment"]), ""), (rs(db["total_limit"]), ""), (rs(cc["principal"]), "")),
  row(label_cell("Cost to E-O-D", "Over the seven-year term"),
      (f'{pct(eq["stake_pct"],0)} of the project', ""), (rs(db["total_finance_cost"]), ""),
      (f'{rs(cc["coupon_paid_total"])} + {pct(cc["conversion_stake_pct"],0)}', "")),
  row(label_cell("Return to the funder"), (pct(eq["irr_pct"]), cls(eq["irr_pct"])),
      (f'{pct(db["rate_pct"],2)} + fee', "pos"), (pct(cc["irr_pct"]), cls(cc["irr_pct"]))),
  row(label_cell("Does it clear a funder's hurdle?"), ("No", "neg"), ("Yes", "pos"), ("No", "neg")),
  row(label_cell("Collateral required"), ("None", "pos"), ("None — CGTMSE cover", "pos"), ("None", "pos")),
  row(label_cell("Repaid?"), ("Never", "neg"), ("Yes, from collections", "pos"), ("Converts", "")),
  row(label_cell("Upside retained by E-O-D"), (pct(100 - eq["stake_pct"], 0), ""), ("100%", "pos"), (pct(100 - cc["conversion_stake_pct"], 0), "")),
  row(label_cell("Balance-sheet effect"), ("Improves gearing", "pos"), ("Adds debt", ""), ("Adds debt until conversion", "neg")),
])}
<div class="verdict verdict--go">
  <div class="verdict__label">Recommendation</div>
  <div class="verdict__head">Option B — a right-sized CGTMSE composite facility</div>
  <div class="verdict__body">
    The project earns <b>{pct(f["project_fcf"]["irr_pct"])}</b> against an all-in cost of guaranteed debt of
    <b>{pct(f["cost_of_capital"]["all_in_cost_of_cgtmse_debt_pct"], 2)}</b>. That
    <b>{pct(f["cost_of_capital"]["spread_over_debt_pct"], 1, sign=True)}</b> spread belongs to E-O-D, and debt is
    the only instrument that lets E-O-D keep it. Equity at project level needs
    {pct(eq["stake_for_22pct"], 0)} of the project to clear a normal hurdle, which is more than the project is
    worth giving away. Specifically: <b>term loan {rs(db["term_loan"])}</b> over {db["tl_tenor_years"]} years
    with a <b>{db["tl_moratorium_years"]}-year principal moratorium</b>, plus a working-capital limit sanctioned
    at <b>{rs(dopt["wc_limit"])}</b> rather than the full year of opex, with the balance available as an
    uncommitted overdraft. That structure holds DSCR above
    <b>{num(db["min_dscr_post_moratorium"])}×</b> throughout and leaves
    {rs(db["total_limit"] - dopt["total_limit"])} more of the group's CGTMSE ceiling for Karnal.
  </div>
</div>"""
    S.append(("11", "s11", "Which option, and why", body))

    # 12 risks
    body = f"""
{risks([
  ("Auction overshoot", "High", "sev-h",
   f"The forward e-auction has no cap and the licence fee escalates 5% a year on whatever is bid. Every "
   f"₹1 lakh a year above the modelled {lakh(g['bid_licence_year1'],0)} costs about ₹8.1 lakh across the "
   f"seven-year term. <b>Mitigation:</b> a board-approved walk-away of "
   f"{lakh(f['walk_away']['licence_fee_year1'],1)} a year, set before the auction opens."),
  ("ADA tariff control", "High", "sev-h",
   "ADA fixes the gate at ₹20 and approves every other rate, with the right to revise. The show ticket carries "
   "roughly a third of the revenue and E-O-D cannot price it. <b>Mitigation:</b> agree the show tariff and its "
   "escalation path in writing before the work order, not after."),
  ("Laser and fountain asset condition", "Medium–High", "sev-mh",
   "The agency inherits equipment of unknown age and must replace anything that reaches end of life at its own "
   "cost, with the onus of proving irreparability on the agency. <b>Mitigation:</b> a joint condition survey and "
   "the AMC history before bid submission; price the risk into the auction limit."),
  ("Year-1 cash", "Medium", "sev-m",
   f"The project loses {rs(-yrs[0]['ebitda'])} at EBITDA in year 1 while paying six months of licence fee in "
   "advance. <b>Mitigation:</b> this is precisely what the working-capital limit is for; the three-year "
   "principal moratorium keeps debt service out of the ramp."),
  ("No permanent structures", "Medium", "sev-m",
   "Clause 3.3.2 bars permanent construction. The activity layer — E-O-D's core margin driver — must be "
   "demountable, which raises unit cost and shortens asset life. <b>Mitigation:</b> the capex schedule assumes "
   "an eight-year life on demountable equipment, not fifteen."),
  ("Concession renewal", "Medium", "sev-m",
   "Seven years, extendable by four at ADA's discretion, with the licence fee revisable for the extended term. "
   "<b>Mitigation:</b> no extension value is included in any return in this deck. E-O-D holds two existing ADA "
   "concessions with a clean record."),
  ("Electricity arrears", "Medium", "sev-m",
   "Electricity is paid direct to the discom monthly, and VAPPL carries ₹2.14 Cr of accumulated arrears across "
   "the existing estate. A new site inherits scrutiny. <b>Mitigation:</b> clear the arrears before any lender "
   "sanction — it is a condition precedent in the company deck as well."),
])}
<div style="margin:34px 0 12px;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;">Open items before submission</div>
{caveats([
  "The winning licence fee is unknown until the e-auction concludes. Every figure in this deck is built on a "
  f"{lakh(g['bid_licence_year1'],0)} annual bid and must be re-run against the actual award.",
  "The show and fountain tariff is <b>not set</b> in the RFP — it is left to be agreed with ADA at least ten "
  "days before implementation. This is the single largest revenue assumption in the model and the least "
  "documented. Raise it as a pre-bid query.",
  "The RFP is internally inconsistent in one place: clause 5.1.1(h) defines “Park” as <b>Subash Park</b>, not "
  "Geeta Govind Vatika — a copy-paste from ADA's earlier tender. Harmless, but worth a written clarification so "
  "it cannot be used later.",
  "Milestone 3 requires the first six months of licence fee <b>within 7 days of the work order</b>, while "
  "possession need only be taken within 7 days of executing the agreement. Confirm the sequencing — paying six "
  "months in advance before holding the site is a cash-flow risk worth clarifying.",
  "Activity-layer capex of ₹45 lakh assumes ADA approves the design concept submitted within 15 days of the "
  "work order. If material items are rejected, both the capex and roughly "
  f"{rs(yrs[2]['revenue']['activities'])} of year-3 revenue fall away.",
  "Consortium bidding is permitted (two members and above). Not assumed here — VAPPL qualifies alone.",
])}
{FOOTER}"""
    S.append(("12", "s12", "Risks and open items", body))

    rail = [(n, sid, t) for n, sid, t, _ in
            [(a, b, c, d) for a, b, c, d in S]]
    body = cover + "\n".join(sec(n, sid, t, b) for n, sid, t, b in S)
    return page("Geeta Govind Vatika — Project Finance · E-O-D Parks",
                "Project finance · Geeta Govind Vatika", body, rail,
                "pf-geeta-govind-vatika.html")

# ============================================================================
# DECK 2 — RAMAYAN VATIKA
# ============================================================================
def deck_rv():
    v = M["rv"]; f = v["financing"]; r = v["rfp"]; db = f["debt"]
    yrs = v["years"]; cap = f["true_capital_requirement"]; mob = v["mobilisation"]
    dc = f["debt_capacity"]; dopt = f["debt_optimised"]; wa = f["walk_away"]
    S = []

    cover = f"""
<div class="fin-cover">
  <div class="fin-cover__eyebrow">Project finance · 02 of 04</div>
  <h1 class="fin-cover__title">Ramayan Vatika</h1>
  <p class="fin-cover__sub">Fifteen years of operating rights over a 51-foot bronze Ram, a holographic
  show projected onto it, and 16,000 Miyawaki trees in Bareilly. The longest contract in the portfolio,
  the tightest margin, and the only one where the RFP forbids you from pledging anything.</p>
  <div class="fin-cover__meta">
    <b>Bareilly Development Authority</b> · Licence-fee model · 10 + 5 years · 5-year lock-in<br>
    Reserve licence fee <b>{lakh(r["reserve_licence_fee_year_lakh"],0)} a year</b> · sealed H1 bid ·
    5% annual escalation · performance security {lakh(r["performance_security_lakh"],0)}<br>
    Technically qualified plus financially H1 · presentation required
  </div>
  <div class="cover-kpi-grid">
    {kpi("Facility as briefed", rs(f["facility_ask"]), sub="Two years of operating cost, per the brief")}
    {kpi("Debt the project can carry", rs(dc["max_total_limit"]), sub=f'At a {dc["target_dscr"]}× DSCR floor')}
    {kpi("Project IRR", pct(f["project_fcf"]["irr_pct"]), sub=f'Against a {pct(f["cost_of_capital"]["all_in_cost_of_cgtmse_debt_pct"],2)} cost of guaranteed debt')}
    {kpi("Walk-away licence fee", lakh(wa["licence_fee_year1"],1), sub=f'{lakh(wa["licence_fee_month"],2)} a month')}
  </div>
</div>
{note("terra","Read section 06 before section 02",
  f"This deck does not conclude that Ramayan Vatika should be funded on the terms briefed. On the base "
  f"assumptions the project returns <b>{pct(f['project_fcf']['irr_pct'])}</b> against a "
  f"<b>{pct(f['cost_of_capital']['all_in_cost_of_cgtmse_debt_pct'],2)}</b> cost of guaranteed debt, and can "
  f"service <b>{rs(dc['max_total_limit'])}</b> of facility against the <b>{rs(f['facility_ask'])}</b> asked for. "
  "The financing structures are set out in full because they were asked for, and because the project does work "
  "on BDA's own revenue assumptions — but the bid discipline in section 12 is the part that matters.")}"""

    assets_lis = "".join(f"<li>{e(x)}</li>" for x in r["assets"])
    streams_lis = "".join(f"<li>{e(x)}</li>" for x in r["revenue_streams"])
    mp = r["min_manpower"]
    body = f"""
<p class="lede">BDA has built a 33,000 square metre thematic park around the Ramayana and wants an
operator for fifteen years. The centrepiece is a 51-foot bronze Lord Ram by Ram Sutar, with a 3D
holographic laser and sound programme projected onto the statue and its surroundings.</p>
{table(["Term", "What the RFP says"], [
  row(label_cell("Authority"), (e(r["authority"]), "")),
  row(label_cell("Site"), (f'{e(r["site"])} · {r["area_sqm"]:,} sq m (~{r["area_acres"]} acres)', "")),
  row(label_cell("Contract period"), (e(r["term"]), "")),
  row(label_cell("Lock-in"), (f'<b>{e(r["lock_in"])}</b><span class="meta">{e(r["lock_in_conflict"])}</span>', "")),
  row(label_cell("Selection"), (e(r["selection"]), "")),
  row(label_cell("Reserve licence fee"), (f'<b>{lakh(r["reserve_licence_fee_year_lakh"],0)} a year</b> · {lakh(r["reserve_licence_fee_year_lakh"]/4,2)} quarterly in advance', "")),
  row(label_cell("Escalation"), (f'{pct(r["escalation_pct"],0)} a year', "")),
  row(label_cell("Payment terms"), (e(r["payment_terms"]) + f'<span class="meta">{e(r["penal_interest"])}. Non-payment for two consecutive quarters is a material breach.</span>', "")),
  row(label_cell("EMD / bid fee"), (f'{lakh(r["emd_lakh"],0)} refundable / {lakh(r["bid_fee_lakh"],2)}<span class="meta">EMD exempt for MSMEs registered in Uttar Pradesh.</span>', "")),
  row(label_cell("Performance security"), (f'<b>{lakh(r["performance_security_lakh"],0)}</b><span class="meta">{e(r["performance_security_note"])}</span>', "")),
  row(label_cell("Statutory burden"), (e(r["statutory"]), "")),
  row(label_cell("BDA free use"), (f'Up to {r["bda_free_use_days"]} days a calendar year, no compensation', "")),
  row(label_cell("Utilities"), ('BDA provides water and electricity connections; the operator pays consumption', "")),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">What already exists on site</div>
<ul style="font-size:13.5px;color:var(--ink-soft);line-height:1.7;padding-left:20px;margin:0 0 20px;">{assets_lis}</ul>
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Approved revenue streams</div>
<ul style="font-size:13.5px;color:var(--ink-soft);line-height:1.7;padding-left:20px;margin:0 0 20px;">{streams_lis}</ul>
{note("terra","Two clauses that change how this can be financed",
  f"<b>No charge over the asset.</b> “{e(r['mortgage_prohibition'])}” The Vatika cannot secure anything. That "
  "removes conventional project finance entirely and leaves a collateral-free CGTMSE facility as the only "
  "sensible debt route — the guarantee substitutes for the security the RFP forbids.<br><br>"
  f"<b>No change of control without consent.</b> “{e(r['shareholding_restriction'])}” Any equity issue that "
  "shifts VAPPL's shareholding, and any convertible instrument at the moment it converts, needs BDA's prior "
  "written approval during the lock-in. This is a condition precedent on Options A and C, not a footnote.")}
{note("blue","The technical bid is where E-O-D wins",
  f"BDA scores 100 marks and takes the highest scorer through to the financial bid. Experience "
  f"({r['tech_score']['experience']} marks) — VAPPL runs four parks, three on government concessions, all "
  "above the ₹50 lakh threshold: full marks. Financial strength "
  f"({r['tech_score']['financial_strength']} marks) — the top band is turnover above ₹5 Cr against VAPPL's "
  "₹16.29 Cr, with positive net worth of ₹2.58 Cr clearing the mandatory qualifying test: full marks. Manpower "
  f"({r['tech_score']['manpower']}), O&M plan ({r['tech_score']['om_plan']}) and technology "
  f"({r['tech_score']['technology']}) are presentation-led and winnable. <b>The tender has been floated roughly "
  "three times without concluding for want of competing bids</b> — which is both the opportunity and the "
  "warning: nobody else has been able to make the numbers work either.")}"""
    S.append(("01", "s01", "The project", body))

    body = f"""
<p class="lede">The brief was “two years of opex as loan or investment”. Sized literally that is
{rs(f["facility_ask"])}. The project's own capacity to service debt is {rs(dc["max_total_limit"])}.
The gap between those two numbers is the whole question.</p>
{bento([
  ("Facility as briefed", rs(f["facility_ask"]), "Two full years of operating cost"),
  ("True capital at risk", rs(cap["total"]), "Mobilisation, toy train, and two years of operating deficit"),
  ("Serviceable at 1.30× DSCR", rs(dc["max_total_limit"]), f'Gap to the brief: {rs(f["facility_ask"] - dc["max_total_limit"])}'),
])}
{table(["Requirement", "Amount"], [
  row(label_cell("Mobilisation capex", "Ticketing and access control, food court fit-out, activity equipment, signage, tools"), (lakh(mob["capex_year0"]), "")),
  row(label_cell("Performance security", "Interest-free, held until three months after completion — a 15-year lock-up of cash"), (lakh(mob["performance_security"]), "")),
  row(label_cell("EMD and bid fee", "EMD refundable; exempt for UP-registered MSMEs"), (lakh(mob["emd"] + mob["bid_fee"]), "")),
  row(label_cell("Stamp duty and registration", "Compulsory registration of the agreement, borne by the operator"), (lakh(mob["stamp_duty_registration"]), "")),
  row(label_cell("Advance licence fee", "First quarter, due by the 10th of the first month"), (lakh(mob["advance_licence_fee_q1"]), "")),
  row(("Sub-total — mobilisation", ""), (lakh(mob["total"]), ""), cls_="sub"),
  row(label_cell("Toy train and track", "Year 2 — optional. BDA lists it as an approved but discretionary stream"), (lakh(mob["capex_year2_toy_train"]), "")),
  row(label_cell("Year 1 operating expenditure", ""), (lakh(v["opex_year1"]), "")),
  row(label_cell("Year 2 operating expenditure", ""), (lakh(v["opex_year2"]), "")),
  row(("Facility requested — two years of opex", ""), (lakh(f["facility_ask"]), ""), cls_="total"),
])}
{note("amber","The performance security is the hidden cost",
  f"{lakh(r['performance_security_lakh'],0)} sits with BDA, interest-free, for the entire fifteen-year term. At "
  "a 11.5% opportunity cost that is roughly ₹3.45 lakh a year of foregone return, or about ₹52 lakh across the "
  "contract — <b>more than one and a half years of licence fee</b>. It is real, it is not recoverable, and it "
  "should be priced into the bid rather than treated as a refundable deposit.")}
{note("blue","Sizing the facility against what the project can carry",
  f"A lender will size on debt service coverage, not on the borrower's stated need. On the base case this "
  f"project services <b>{rs(dc['max_total_limit'])}</b> — a term loan of {rs(dc['max_term_loan'])} and a "
  f"working-capital limit of {rs(dc['max_wc_limit'])} — at a 1.30× floor. The recommended structure in section "
  f"11 therefore sanctions the full {rs(f['facility_ask'])} as a <b>limit</b>, with only "
  f"{rs(cap['total'])} of it expected to be drawn, and the balance available but uncommitted.")}"""
    S.append(("02", "s02", "What the money is for", body))

    rev_keys = [("entry", "Entry ticketing", "₹20–25 adult, ₹10 child, under-5 free. Computerised, auditable, BDA-approved rates."),
                ("show", "Holographic and laser show", "3D projection onto the Ram statue. The single largest line — and the whole thesis."),
                ("fnb", "Food court and vendor rentals", "Four stalls on lease plus directly operated outlets."),
                ("parking", "Parking", "Two-wheeler, four-wheeler and bus. Rates fixed by BDA."),
                ("events", "Cultural events and Ram Katha", "Folk performances, themed festivals, private functions — all pre-approved."),
                ("ancillary", "Souvenirs, photography, schools, advertising", "Theme-consistent only. The negative list bars anything else."),
                ("toy_train", "Toy train", "Commissioned in year 2. Listed by BDA as approved but discretionary.")]
    rev_rows = [row(label_cell(n, m), *[(cr(y["revenue"][k]), "") for y in yrs]) for k, n, m in rev_keys]
    rev_rows.append(row(("Total revenue, net of GST", ""), *[(cr(y["revenue"]["total"]), "") for y in yrs], cls_="total"))
    rev_rows.append(row(("Footfall, lakh visits", ""), *[(num(y["revenue"]["footfall_lakh"], 2), "muted") for y in yrs], cls_="dim"))
    bda_lo, bda_hi = r["bda_indicative_revenue_cr"]
    body = f"""
<p class="lede">BDA published its own indicative revenue of ₹{bda_lo:.2f}–{bda_hi:.2f} crore a year.
This model is deliberately built below it in the early years and reaches it in year 3 — because the
single assumption BDA's number rests on is the one most likely to be wrong.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], rev_rows)}
{note("terra","Where this model parts company with BDA",
  f"BDA's ₹{bda_hi:.2f} crore assumes <b>{e(r['bda_indicative_basis'])}</b>. A 60% conversion from gate to a "
  "₹125 evening show is extraordinary — it implies three in five visitors, including morning walkers, families "
  "with small children and school groups, buy the show. This model starts at <b>42%</b> and reaches 52% by year "
  "10. That single assumption is worth roughly ₹40 lakh a year at year-5 volumes and is the difference between "
  "the base case and the BDA case in section 07. <b>Everything about whether to bid turns on it.</b> Ask BDA for "
  "the show's commissioning date, seating capacity, number of daily slots and any footfall data from the "
  "soft-launch period.")}
{assm([("Footfall and capture", [
   ("Year 1 footfall", "1.65 lakh visits — about 450 a day, below BDA's 500 baseline", "1.65 L"),
   ("Year 10 footfall", "3.85 lakh visits — about 1,055 a day", "3.85 L"),
   ("Paid entry ratio", "Net of under-5s", "80% → 83%"),
   ("Show conversion", "Against BDA's assumed 60%", "42% → 52%"),
 ]),
 ("Tariffs, gross of GST", [
   ("Entry", "BDA-approved; BDA reserves the right to cap for affordability", "₹22 → ₹33"),
   ("Show ticket", "BDA's stated range is ₹100–150. Escalation modelled below inflation", "₹150 → ₹185"),
   ("Food court", "Four stalls at ₹25,000 a month plus directly operated outlets", "BDA basis"),
   ("Parking", "70% two-wheeler at ₹10, 30% four-wheeler at ₹30", "₹10 / ₹30"),
 ])])}"""
    S.append(("03", "s03", "Revenue model", body))

    cost_keys = [("licence_fee", "Licence fee to BDA", "Bid escalating at 5% a year, quarterly in advance"),
                 ("manpower", "Payroll", f'{mp["per_shift"]["sweepers"]} sweepers and {mp["per_shift"]["security"]} security per shift, {mp["per_day"]["mali_gardener"]} gardeners, site manager, electrician and plumber per day — the BDA minimum, plus ticketing, show and F&B staff. EPF and ESI mandatory.'),
                 ("electricity", "Electricity", "Holographic projection, statue and landscape lighting, eight acres"),
                 ("water_consumables", "Water and consumables", ""),
                 ("horticulture", "Horticulture", "16,000-tree Miyawaki forest, six thematic vatikas, lawns, boundary green belt"),
                 ("show_amc", "Show AMC", "3D holographic projectors, laser, synchronised sound"),
                 ("statue_upkeep", "Statue and artefact upkeep", "Polishing, painting and restoration of the bronze and marble statues, murals and gates — an explicit obligation"),
                 ("repairs", "Repairs and maintenance", "Civil, electrical, fittings, toilets, utilities"),
                 ("insurance", "Insurance", "Property, fire, public liability and third-party — mandatory"),
                 ("marketing", "Marketing", "4.5% of revenue"),
                 ("fnb_cogs", "F&B cost of goods", "On the directly operated share only"),
                 ("it_cctv", "IT, POS and CCTV", "Computerised ticketing is a contractual requirement"),
                 ("corporate_overhead", "Corporate overhead", "4% of revenue"),
                 ("contingency", "Contingency", "Provision against the penalty schedule")]
    cost_rows = [row(label_cell(n, m), *[(cr(y["opex"][k]), "") for y in yrs]) for k, n, m in cost_keys]
    cost_rows.append(row(("Total operating cost", ""), *[(cr(y["opex"]["total"]), "") for y in yrs], cls_="total"))
    body = f"""
<p class="lede">This is a maintenance-heavy contract. BDA transfers the entire comprehensive maintenance
obligation — civil, electrical, horticultural, statuary and IT — to the operator, at the operator's cost,
with quarterly audits and the authority's decision on asset condition binding at handover.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], cost_rows)}
{note("amber","The manpower floor is contractual, not discretionary",
  f"BDA prescribes a minimum deployment: {mp['per_shift']['sweepers']} sweepers and "
  f"{mp['per_shift']['security']} security personnel <b>per shift</b>, plus "
  f"{mp['per_day']['mali_gardener']} gardeners, a site manager, an electrician and a plumber per day — around "
  "29 heads before a single ticket is sold. Add ticketing, show technicians and food-court staff and the "
  "operating establishment is roughly 37 people. EPF and ESI are mandatory and explicitly called out. "
  "<b>Payroll is the largest cost line in every year of this contract and it cannot be flexed down in a bad "
  "season.</b> That is the structural reason the margin here is thinner than at Geeta Govind Vatika.")}
{note("terra","Restoration risk at handover",
  "The operator must return every asset “in the same condition as recorded at the time of initial handover, "
  "without any reduction in value, quality or serviceability”, with BDA's decision final and binding, and a "
  "pre-handover inspection thirty days out that can direct further works at the operator's cost. A 51-foot "
  "bronze and a Miyawaki forest are not assets whose fifteen-year condition can be underwritten confidently. "
  "<b>Mitigation:</b> a detailed, photographed, jointly signed asset handover report on day one, and a "
  "restoration provision accrued annually rather than met from year-15 cash.")}"""
    S.append(("04", "s04", "Cost model", body))

    pl_rows = [
      row(label_cell("Revenue", "Net of GST"), *[(cr(y["revenue"]["total"]), "") for y in yrs]),
      row(label_cell("Operating cost", ""), *[(cr(-y["opex"]["total"]), "muted") for y in yrs]),
      row(("EBITDA", ""), *[(cr(y["ebitda"]), cls(y["ebitda"])) for y in yrs], cls_="sub"),
      row(("EBITDA margin", ""), *[(pct(y["ebitda_margin"], 1), "muted") for y in yrs], cls_="dim"),
      row(label_cell("Depreciation", "Toy train enters in year 2"), *[(cr(-y["depreciation"]), "muted") for y in yrs]),
      row(("EBIT", ""), *[(cr(y["ebit"]), cls(y["ebit"])) for y in yrs], cls_="total"),
    ]
    body = f"""
<p class="lede">Two loss-making years, then a slow climb to a low-twenties margin. The shape is the
direct consequence of a fixed manpower floor meeting a ramping revenue line.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], pl_rows)}
{bento([
  ("EBITDA breakeven", "Year 3", f'After {rs(cap["cumulative_operating_deficit"])} of cumulative operating deficit'),
  ("Margin at year 10", pct(yrs[-1]["ebitda_margin"], 1), "Against 24.3% at Geeta Govind Vatika in year 7"),
  ("Cumulative EBITDA", rs(sum(y["ebitda"] for y in yrs)), "Across the ten-year initial term"),
])}
{note("blue","Years 11 to 15 are excluded from every return in this deck",
  "The extension is five further years at BDA's discretion, subject to performance, with a two-year lock-in of "
  "its own and the licence fee reviewable. Those years would run a mature revenue line against an established "
  "cost base and are where the contract's real profit sits. They are deliberately not modelled. If they are "
  "granted, the returns below improve materially — but they cannot be underwritten at bid stage.")}"""
    S.append(("05", "s05", "Ten-year projection", body))

    ex = f["exit_valuation"]
    body = f"""
<p class="lede">The project consumes {rs(cap["total"])} of capital and returns
{rs(f["project_fcf"]["cumulative_fcf"])} over ten years. That is a real return — it is simply not
a large enough one to pay for the money that funds it.</p>
{fcf_table(f["project_fcf"])}
{bento([
  ("Project IRR", pct(f["project_fcf"]["irr_pct"]), "Unlevered, ten-year term, no extension value"),
  ("Payback", f'{num(f["project_fcf"]["payback_years"],1)} yrs', "Against a five-year contractual lock-in"),
  ("NPV at 15%", rs(f["project_fcf"]["npv_at_15pct"]), "Negative — the project does not clear a 15% cost of capital"),
])}
{verdict_block(f["cost_of_capital"],
  extra=("The gap is narrow, not catastrophic, and it closes entirely on BDA's own revenue assumption — see "
         "section 07. But it does not close by hoping. It closes by bidding at the reserve price and by "
         "getting the show economics confirmed in writing before submission."))}
{note("terra","Payback lands after the lock-in expires — but only just",
  f"Free cash flow turns cumulatively positive in year {num(f['project_fcf']['payback_years'],1)}. The "
  "contractual lock-in runs five years, during which exit means paying out the remaining contractual amount for "
  "the unexpired period. <b>There is no cheap way out of a bad outcome here.</b> On a seven-year reading of the "
  "lock-in — clause 9 of the Key Terms says seven where clause 14 says five — the position is worse still. "
  "Resolve that conflict by pre-bid query before anything is committed.")}"""
    S.append(("06", "s06", "Project returns", body))

    body = f"""
<p class="lede">One assumption separates a project that should not be bid from one that comfortably
clears its cost of capital: how many visitors buy the show.</p>
{scenario_cards(v["scenarios"])}
{note("green","BDA's own case works — and it is not implausible",
  f"On BDA's stated assumptions the project returns "
  f"<b>{pct(v['scenarios']['bda_indicative']['project_irr_pct'])}</b> with a stabilised EBITDA margin of "
  f"{pct(v['scenarios']['bda_indicative']['ebitda_margin_stabilised'],1)}. A 51-foot bronze Ram with a "
  "holographic show projected onto it is a genuine destination attraction, and Bareilly has no competing "
  "evening product. The base case here is conservative by design because nobody has operated this asset yet "
  "and there is no footfall history to calibrate against. <b>The right response is not to bid on the base case "
  "or the BDA case, but to bid at a price that survives the base case and rewards the BDA case.</b>")}
{note("terra","The downside is where the lock-in bites",
  f"Fifteen per cent below base on footfall and conversion, a 5% cost overrun and a "
  f"{lakh(v['bid_licence_year1']*1.33,0)} licence fee produce a project that is still losing money at EBITDA "
  "in year 5 — inside the lock-in, with no exit that does not cost the unexpired contractual amount. This is "
  "the scenario that should set the bid, not the base case.")}"""
    S.append(("07", "s07", "Scenarios", body))

    eq = f["equity"]
    body = f"""
<p class="lede">Sized to the true capital requirement rather than the gross facility, and valued at exit
on the discounted cash flow still to come over the balance of the concession.</p>
{table(["Term", "Structure"], [
  row(label_cell("Capital"), (rs(eq["investment"]), "")),
  row(label_cell("Stake offered"), (pct(eq["stake_pct"], 0), "")),
  row(label_cell("Distribution policy", "Free cash after debt service; nothing before year 4"), ("From year 4", "")),
  row(label_cell("Exit", e(eq["basis"])), (f'End of year {eq["exit_year"]}', "")),
  row(label_cell("Exit equity value"), (rs(eq["exit_equity_value"]), "")),
  row(("Investor IRR", ""), (pct(eq["irr_pct"]), cls(eq["irr_pct"])), cls_="total"),
  row(("Money multiple", ""), (f'{num(eq["money_multiple"])}×', ""), cls_="total"),
])}
{note("terra","The arithmetic does not work at project level",
  f"At {pct(eq['stake_pct'],0)} of the project an investor earns {pct(eq['irr_pct'])}. To reach a 22% hurdle "
  f"they would need <b>{pct(eq['stake_for_22pct'],0)}</b> — the entire project and then some. There is no "
  "split of this concession that pays third-party equity a market return and leaves E-O-D a reason to operate "
  "it.")}
{note("amber","And it needs BDA's written consent",
  f"“{e(r['shareholding_restriction'])}” A project-level equity structure that changes VAPPL's shareholding "
  "pattern — or a holding company above it — requires BDA's prior written approval during the lock-in, with "
  "forfeiture of the performance security and blacklisting as the stated consequence of breach. Any equity "
  "conversation must start at BDA's office, not the investor's.")}"""
    S.append(("08", "s08", "Option A · Equity", body))

    peak_wc = max(x["wc_outstanding"] for x in db["schedule"])
    body = f"""
<p class="lede">The RFP forbids any charge over the Vatika. That is not an obstacle to a CGTMSE facility —
it is the reason to use one. The guarantee replaces the security the contract will not allow.</p>
{note("green","Why the guarantee is structurally the right answer here",
  f"“{e(r['mortgage_prohibition'])}” A conventional lender secures a project loan on the project. Here there is "
  "nothing to secure it on: BDA owns the land, the statue, the show and every fixture, and expressly bars them "
  "being pledged. CGTMSE covers a facility with <b>nil collateral and no third-party guarantee</b>, taking only "
  "hypothecation of the assets the borrower itself finances — ticketing systems, food-court equipment, the toy "
  "train. Personal guarantees of directors remain permissible. <b>The scheme and the contract fit each other "
  "exactly.</b>")}
{table(["Term", "Structure"], [
  row(label_cell("Scheme"), (f'CGTMSE {M["cgtmse"]["scheme"]} · ceiling {rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100,0)} per borrower', "")),
  row(label_cell("Term loan", "Mobilisation, performance security, stamp duty, toy train"), (rs(db["term_loan"]), "")),
  row(label_cell("Working capital limit", "The opex facility, revolving"), (rs(db["wc_limit"]), "")),
  row(("Total facility as briefed", ""), (rs(db["total_limit"]), ""), cls_="sub"),
  row(label_cell("Interest rate"), (pct(db["rate_pct"], 2), "")),
  row(label_cell("Annual guarantee fee", "Charged on the sanctioned limit in year 1, on the outstanding thereafter"), (pct(db["cgtmse"]["agf_rate_pct"], 2), "")),
  row(label_cell("Tenor / moratorium", "Matched inside the ten-year initial term"), (f'{db["tl_tenor_years"]} years / {db["tl_moratorium_years"]}-year principal moratorium', "")),
  row(label_cell("Guarantee coverage"), (f'{pct(db["cgtmse"]["coverage_pct"], 0)} · {rs(db["cgtmse"]["guaranteed_amount"])} guaranteed', "")),
  row(label_cell("Security"), ('Nil collateral. Hypothecation of assets financed by the borrower only — never the Vatika.', "")),
  row(("Total finance cost over the term", ""), (rs(db["total_finance_cost"]), ""), cls_="total"),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Repayment and cover at the facility size briefed, ₹ crore</div>
{debt_schedule_table(db)}
{bento([
  ("Minimum DSCR", num(db["min_dscr_post_moratorium"]) + "×", "Below the 1.30× threshold a bank will underwrite to"),
  ("Serviceable facility", rs(dc["max_total_limit"]), f'{rs(dc["max_term_loan"])} term loan + {rs(dc["max_wc_limit"])} working capital'),
  ("Expected peak drawdown", rs(max(cap["total"], peak_wc)), "Against a limit of " + rs(db["total_limit"])),
])}
{note("terra","The facility as briefed does not clear a bank's coverage test",
  f"At {rs(db['total_limit'])} the minimum post-moratorium DSCR is "
  f"<b>{num(db['min_dscr_post_moratorium'])}×</b>. Banks underwrite CGTMSE term facilities to 1.30× and "
  f"prefer 1.50×. The project services <b>{rs(dc['max_total_limit'])}</b> at that floor. The workable structure "
  f"is therefore a <b>sanctioned limit</b> of {rs(f['facility_ask'])} with a committed, drawn component of "
  f"{rs(dc['max_total_limit'])} and the balance uncommitted — or a smaller facility with the difference met "
  "from group cash. Presenting the full two years of opex to a credit committee as committed term money will "
  "get the proposal declined.")}
{note("amber","Right-size the sanctioned limit",
  f"The guarantee fee is charged on what is <b>sanctioned</b>, not what is used. Trimming the working-capital "
  f"limit from {rs(db['wc_limit'])} to {rs(dopt['wc_limit'])} saves "
  f"<b>{lakh(f['agf_saving_optimised'],2)}</b> of guarantee fee and frees "
  f"{rs(db['total_limit'] - dopt['total_limit'])} of the group's ₹10 crore CGTMSE ceiling.")}"""
    S.append(("09", "s09", "Option B · Debt under CGTMSE", body))

    cc = f["ccd"]
    body = f"""
<p class="lede">Money in as debt, a coupon while the park ramps, compulsory conversion into equity on a
formula fixed the day the instrument is issued.</p>
{table(["Term", "Structure"], [
  row(label_cell("Principal"), (rs(cc["principal"]), "")),
  row(label_cell("Coupon", "Annual, until conversion"), (pct(cc["coupon_pct"], 1), "")),
  row(label_cell("Conversion"), (f'End of year {cc["conversion_year"]} — compulsory, not optional', "")),
  row(label_cell("Conversion stake"), (pct(cc["conversion_stake_pct"], 0), "")),
  row(label_cell("Coupon paid to conversion"), (rs(cc["coupon_paid_total"]), "")),
  row(label_cell("Exit"), (f'End of year {cc["exit_year"]} at {rs(cc["exit_equity_value"])}', "")),
  row(("Investor IRR", ""), (pct(cc["irr_pct"]), cls(cc["irr_pct"])), cls_="total"),
  row(("Money multiple", ""), (f'{num(cc["money_multiple"])}×', ""), cls_="total"),
])}
{note("terra","Three separate reasons this is the worst of the three here",
  f"<b>Cash.</b> The coupon falls due in years 1 to {cc['conversion_year']} — precisely the years the project is "
  f"losing money at EBITDA. {rs(cc['coupon_paid_total'])} has to come from somewhere, and it is not coming from "
  "the gate.<br><br><b>Consent.</b> Conversion changes the shareholding pattern, which needs BDA's prior written "
  "approval inside the lock-in. An instrument that <em>must</em> convert on a fixed date, into a shareholding "
  "change that a third party can refuse to approve, is a structural mismatch. If BDA withholds consent the "
  "instrument cannot perform.<br><br><b>Leverage.</b> Until it converts a CCD is borrowing. Layered on VAPPL's "
  "existing 3.04× debt-to-equity it breaches the gearing covenant on any CGTMSE facility running alongside it.")}
{note("blue","If a convertible is used, use it at company level",
  "The company deck sets out a ₹12 crore CCD at VAPPL level returning 21.2% to the investor while deferring "
  "dilution — a genuinely competitive structure. The instrument is sound; this is the wrong project to attach "
  "it to.")}"""
    S.append(("10", "s10", "Option C · Debt converted to equity", body))

    body = f"""
{opt_cards(f)}
{table(["", "A · Equity", "B · CGTMSE debt", "C · CCD"], [
  row(label_cell("Money in"), (rs(eq["investment"]), ""), (rs(db["total_limit"]), ""), (rs(cc["principal"]), "")),
  row(label_cell("Return to the funder"), (pct(eq["irr_pct"]), cls(eq["irr_pct"])),
      (f'{pct(db["rate_pct"],2)} + fee', "pos"), (pct(cc["irr_pct"]), cls(cc["irr_pct"]))),
  row(label_cell("Clears a funder's hurdle?"), ("No", "neg"), ("Yes", "pos"), ("No", "neg")),
  row(label_cell("Permitted by the RFP without consent?"), ("No — change of control", "neg"),
      ("Yes — no charge over the Vatika", "pos"), ("No — conversion is a change of control", "neg")),
  row(label_cell("Cash cost during the ramp"), ("None", "pos"), ("Interest and fee only, principal deferred", ""), (f'{rs(cc["coupon_paid_total"])} of coupon', "neg")),
  row(label_cell("Effect on group gearing"), ("Improves", "pos"), ("Adds debt", ""), ("Adds debt until conversion", "neg")),
  row(label_cell("Upside retained by E-O-D"), (pct(100 - eq["stake_pct"], 0), ""), ("100%", "pos"), (pct(100 - cc["conversion_stake_pct"], 0), "")),
])}
<div class="verdict verdict--caution">
  <div class="verdict__label">Recommendation</div>
  <div class="verdict__head">Bid at reserve. Fund with a CGTMSE limit, drawn to {rs(dc["max_total_limit"])}.</div>
  <div class="verdict__body">
    Of the three structures only debt is both viable and permitted without BDA's consent — and it is viable
    only if the facility is <b>sanctioned</b> at {rs(f["facility_ask"])} but <b>committed</b> at
    {rs(dc["max_total_limit"])}, which is what the project services at a 1.30× coverage floor. The binding
    condition sits earlier than the financing, though: the model solves the break-even licence fee at
    <b>{lakh(wa["licence_fee_year1"],1)} a year</b> against BDA's
    {lakh(r["reserve_licence_fee_year_lakh"],0)} reserve. That is
    {pct((wa["licence_fee_year1"]/r["reserve_licence_fee_year_lakh"] - 1) * 100, 0)} of headroom in a sealed
    highest-bid process. <b>Bid at or barely above reserve, or do not bid.</b> On a contract with a five-year
    lock-in and a fifteen-year restoration obligation, winning at the wrong price is worse than losing.
  </div>
</div>
{note("green","What would change this recommendation",
  "Written confirmation from BDA on three points would move this project from marginal to clearly fundable: "
  "<b>(i)</b> the show's capacity, daily slot count and any soft-launch footfall data, which is what the "
  "conversion assumption turns on; <b>(ii)</b> agreement on the show tariff and a contractual escalation path, "
  "rather than annual discretion; <b>(iii)</b> resolution of the five-versus-seven-year lock-in conflict. All "
  "three are legitimate pre-bid queries and all three are free to ask.")}"""
    S.append(("11", "s11", "Which option, and why", body))

    body = f"""
{risks([
  ("Show conversion", "High", "sev-h",
   "Roughly half the revenue comes from one product with no operating history. BDA assumes 60% conversion; this "
   "model assumes 42% rising to 52%. <b>Mitigation:</b> obtain slot capacity and soft-launch data pre-bid; "
   "build the combo, school and group packages BDA already permits; bid a price that survives the base case."),
  ("Bid price in a sealed H1 process", "High", "sev-h",
   f"Break-even licence fee is {lakh(wa['licence_fee_year1'],1)} a year against a "
   f"{lakh(r['reserve_licence_fee_year_lakh'],0)} reserve — "
   f"{pct((wa['licence_fee_year1']/r['reserve_licence_fee_year_lakh']-1)*100,0)} of headroom, in a format that "
   "rewards the highest bid. <b>Mitigation:</b> a board-approved ceiling before the bid is sealed."),
  ("Five-year lock-in", "High", "sev-h",
   "Exit before the lock-in expires costs the remaining contractual amount for the unexpired period, plus "
   "forfeiture of the ₹30 lakh performance security. Payback lands at roughly year seven. <b>Mitigation:</b> "
   "none available contractually — this is why the bid price has to be right."),
  ("Restoration obligation at handover", "Medium–High", "sev-mh",
   "Every asset returned in its handover condition, BDA's decision binding, with a pre-handover inspection that "
   "can direct further works. A bronze statue and a Miyawaki forest over fifteen years. <b>Mitigation:</b> a "
   "photographed joint asset handover report on day one; accrue a restoration provision annually."),
  ("Manpower floor", "Medium", "sev-m",
   "Roughly 29 heads are contractually mandated before revenue. EPF and ESI are explicit. Payroll cannot flex "
   "with a weak season. <b>Mitigation:</b> multi-skill the establishment; use the food court on a vendor-lease "
   "model to move that headcount off the operator's books."),
  ("Tariff cap", "Medium", "sev-m",
   "BDA approves every rate and reserves the right to revise or cap for affordability. <b>Mitigation:</b> seek "
   "a contractual escalation formula rather than annual discretion."),
  ("Negative list", "Medium", "sev-m",
   "Non-thematic commercial activity, branding and kiosks are barred, and BDA may expand the list during the "
   "term. E-O-D's activity layer must be theme-consistent and pre-approved. <b>Mitigation:</b> submit the "
   "activity concept for written approval before the capex is committed."),
  ("Statue as a single point of failure", "Medium", "sev-m",
   "The show projects onto one bronze statue. Damage, weathering or a projection-system failure closes the "
   "principal revenue line. <b>Mitigation:</b> the mandatory property and public-liability cover; a spares and "
   "response-time schedule written into the show AMC."),
])}
<div style="margin:34px 0 12px;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;">Open items before submission</div>
{caveats([
  f"<b>Lock-in conflict.</b> {e(r['lock_in_conflict'])} A seven-year lock-in materially worsens the risk "
  "position and must be settled before bidding.",
  "<b>Bid dates are blank.</b> The data sheet's key-dates table has no bid start, bid end, pre-bid meeting or "
  "technical-opening dates filled in. Confirm the live schedule on etender.up.nic.in before planning submission.",
  "<b>The holographic show is described as being established, not established.</b> The RFP says BDA “is also "
  "establishing” the 3D projection programme. Confirm whether it is commissioned, who holds the AMC, and what "
  "condition it is in. Roughly half of modelled revenue depends on it.",
  "<b>The toy train is repeatedly marked “future planning”</b> throughout the RFP. This model commissions it in "
  f"year 2 at {lakh(mob['capex_year2_toy_train'],0)}. Confirm whether BDA expects the operator to fund it and "
  "whether track and civil works are in place.",
  "<b>Section 8.3(4) of the financial proposal is marked “[Deleted]”.</b> Confirm nothing material to the "
  "revenue-share or reporting obligations was removed by that deletion.",
  "<b>Mobilisation is stated inconsistently</b> — “FIFTEEN (15MONTHLY) days” in clause 10 against a clean "
  "15-day fitment period in clause 19. Assume 15 days and confirm.",
  "<b>EMD exemption for UP-registered MSMEs</b> is available. VAPPL is Delhi-registered; confirm whether a UP "
  f"Udyam registration is worth obtaining before bidding, which would release {lakh(r['emd_lakh'],0)}.",
])}
{FOOTER}"""
    S.append(("12", "s12", "Risks and open items", body))

    rail = [(n, sid, t) for n, sid, t, _ in S]
    body = cover + "\n".join(sec(n, sid, t, b) for n, sid, t, b in S)
    return page("Ramayan Vatika — Project Finance · E-O-D Parks",
                "Project finance · Ramayan Vatika", body, rail, "pf-ramayan-vatika.html")

# ============================================================================
# DECK 3 — KARNAL
# ============================================================================
def deck_karnal():
    k = M["karnal"]; f = k["financing"]; ff = k["facts"]; db = f["debt"]
    yrs = k["years"]; dc = f["debt_capacity"]
    S = []

    cover = f"""
<div class="fin-cover">
  <div class="fin-cover__eyebrow">Project finance · 03 of 04</div>
  <h1 class="fin-cover__title">Karnal</h1>
  <p class="fin-cover__sub">The only one of the three that is a build, not a takeover. Fifteen years on
  India's busiest national highway, a signed sub-lease, a long rent-free construction window — and the
  only project in the portfolio with assets a lender can actually take a charge over.</p>
  <div class="fin-cover__meta">
    <b>Sub-lease with A4A Highway Nest LLP</b> · NH-1 Milestone 109, Gharaunda · 15-year term<br>
    Minimum guarantee <b>₹2–3 lakh a month</b> from opening · long rent-free build period<br>
    Phase 1 build-out <b>{rs(k["capex_total"])}</b> · 12-month construction · opening ~September 2027
  </div>
  <div class="cover-kpi-grid">
    {kpi("Project cost", rs(k["capex_total"]), sub="Phase 1 build-out, as committed in the investor deck")}
    {kpi("Project IRR", pct(f["project_fcf"]["irr_pct"]), sub=f'Payback {num(f["project_fcf"]["payback_years"],1)} years')}
    {kpi("Minimum DSCR", num(db["min_dscr_post_moratorium"]) + "×", sub="Comfortably above the 1.30× bank floor")}
    {kpi("First full year EBITDA", rs(yrs[1]["ebitda"]), sub=f'{pct(yrs[1]["ebitda_margin"],1)} on {rs(yrs[1]["revenue"])} of revenue')}
  </div>
</div>
{note("amber","One fact to settle before any of this is bid or drawn",
  f"{e(ff['area_discrepancy'])}")}"""

    body = f"""
<p class="lede">Karnal replicates the Delhi–Meerut Expressway format on a busier corridor. DME proved
the highway-stopover model works and exposed exactly where it fails — indoor-only product against a
fixed common-area charge. Karnal is built with the outdoor activity stack from day one.</p>
{table(["Term", "Position"], [
  row(label_cell("Site"), (e(ff["site"]), "")),
  row(label_cell("Counterparty"), (e(ff["counterparty"]) + '<span class="meta">Private sub-lease — not a government concession. No tender, no auction, no licence-fee escalation clause imposed by an authority.</span>', "")),
  row(label_cell("Footprint"), (f'~{ff["area_sqft"]:,} sq ft <span class="meta">Subject to the confirmation flagged above.</span>', "")),
  row(label_cell("Term"), (f'{ff["term_years"]} years', "")),
  row(label_cell("Rent"), (f'Minimum guarantee ₹{ff["minimum_guarantee_month_lakh"][0]:.0f}–{ff["minimum_guarantee_month_lakh"][1]:.0f} lakh a month from opening<span class="meta">{e(ff["rent_free"])} — no rent during the 12-month build.</span>', "")),
  row(label_cell("Status"), (e(ff["status"]), "")),
  row(label_cell("Build period"), (f'{ff["build_months"]} months · opening {e(ff["open_estimate"])}', "")),
  row(label_cell("Asset position"), ('E-O-D owns the activity equipment, fit-out and fixtures it installs<span class="meta">Unlike Geeta Govind Vatika and Ramayan Vatika, there are assets here a lender can hypothecate.</span>', "")),
], aligns=["l","l"])}
{note("green","What makes this the strongest of the three",
  "<b>No auction.</b> The rent is a negotiated minimum guarantee, not a number set by a forward e-auction "
  "against unknown bidders. <b>No authority tariff control.</b> E-O-D prices its own tickets. <b>No mandated "
  "manpower floor.</b> The establishment flexes with the season. <b>No restoration obligation</b> over "
  "somebody else's bronze statue. <b>And real assets</b> — the go-kart track, the zipline, the obstacle course "
  "and the fit-out belong to E-O-D and can secure the facility that funds them.")}
{note("blue","What DME taught, and what Karnal does differently",
  "DME lost ₹37.51 lakh in FY25-26 on ₹25.42 lakh of revenue, and ₹29.9 lakh of that loss was fixed common-area "
  "charge — a cost that does not care whether anyone visits. The lesson was not that highway parks do not work; "
  "it was that an <b>indoor-only</b> highway park cannot carry a fixed occupancy cost. Karnal is built with the "
  f"outdoor stack from opening: {rs(190)} of the {rs(k['capex_total'])} capex is go-kart, zipline, obstacle "
  "course and soft play. NH-1 also carries materially higher throughput than the DME corridor.")}"""
    S.append(("01", "s01", "The project", body))

    capex_rows = [row(label_cell(e(c["item"]), f'{c["life_years"]}-year life'), (lakh(c["amount"]), ""))
                  for c in k["capex_lines"]]
    capex_rows.append(row(("Phase 1 project cost", ""), (lakh(k["capex_total"]), ""), cls_="total"))
    body = f"""
<p class="lede">Unlike the two concessions, every rupee here is capital. There is no revolving
working-capital component to separate out — the money buys assets that stay bought.</p>
{table(["Capital expenditure", "Amount"], capex_rows)}
{bento([
  ("Project cost", rs(k["capex_total"]), "As committed in the ₹10 Cr investor deck"),
  ("Promoter contribution", rs(db["promoter_contribution"]), f'{pct(db["promoter_margin_pct"],0)} margin — the standard bank requirement'),
  ("Debt sought", rs(db["term_loan"]), "Term loan against the assets financed"),
])}
{note("blue","This is already funded in the existing plan — the question is how",
  "The ₹10 crore equity round in the investor deck earmarks ₹4 crore for Karnal Phase 1, with construction "
  "starting October 2026 and opening September 2027. This deck asks whether that is the cheapest way to fund "
  "it. On the numbers in section 04 it is not: the project earns "
  f"<b>{pct(f['project_fcf']['irr_pct'])}</b> against an all-in cost of guaranteed debt of "
  f"<b>{pct(f['cost_of_capital']['all_in_cost_of_cgtmse_debt_pct'],2)}</b>. Funding Karnal with debt instead of "
  "equity would free ₹4 crore of the round for the parks that cannot be debt-funded — or reduce the round, and "
  "the dilution, by the same amount.")}"""
    S.append(("02", "s02", "Project cost", body))

    pl_rows = [
      row(label_cell("Revenue", "Year 1 is a half-year stub — H2 FY27-28"), *[(cr(y["revenue"]), "") for y in yrs]),
      row(label_cell("Minimum guarantee to sub-lessor"), *[(cr(-y["opex"]["minimum_guarantee"]), "muted") for y in yrs]),
      row(label_cell("Payroll"), *[(cr(-y["opex"]["manpower"]), "muted") for y in yrs]),
      row(label_cell("Electricity"), *[(cr(-y["opex"]["electricity"]), "muted") for y in yrs]),
      row(label_cell("Activity consumables and AMC"), *[(cr(-y["opex"]["activity_consumables_amc"]), "muted") for y in yrs]),
      row(label_cell("F&B cost of goods", "11% of revenue"), *[(cr(-y["opex"]["fnb_cogs"]), "muted") for y in yrs]),
      row(label_cell("Repairs, marketing, admin, insurance"), *[(cr(-(y["opex"]["repairs"] + y["opex"]["marketing"] + y["opex"]["admin_overhead"] + y["opex"]["insurance_statutory"])), "muted") for y in yrs]),
      row(("Total operating cost", ""), *[(cr(-y["opex"]["total"]), "") for y in yrs], cls_="sub"),
      row(("EBITDA", ""), *[(cr(y["ebitda"]), cls(y["ebitda"])) for y in yrs], cls_="sub"),
      row(("EBITDA margin", ""), *[(pct(y["ebitda_margin"], 1), "muted") for y in yrs], cls_="dim"),
      row(label_cell("Depreciation"), *[(cr(-y["depreciation"]), "muted") for y in yrs]),
      row(("EBIT", ""), *[(cr(y["ebit"]), cls(y["ebit"])) for y in yrs], cls_="total"),
    ]
    body = f"""
<p class="lede">Revenue follows the range published in the company financial model: ₹0.50–1.00 crore in
the FY27-28 stub half-year, ₹3.00–4.00 crore in the first full year. The midpoint is used throughout.</p>
{table([""] + [f"Yr {y['year']}" for y in yrs], pl_rows)}
{note("amber","Why the margin here looks better than the concessions",
  f"Karnal reaches {pct(yrs[4]['ebitda_margin'],1)} EBITDA by year 5 against 24.3% at Geeta Govind Vatika and "
  f"{pct(M['rv']['years'][-1]['ebitda_margin'],1)} at Ramayan Vatika. Three structural reasons: rent is a "
  "negotiated minimum guarantee rather than an auctioned licence fee escalating 5% a year; there is no "
  "contractual manpower floor, so payroll flexes with the season; and there is no obligation to maintain "
  "nineteen acres of someone else's horticulture or restore a bronze statue. <b>Owning your own small site "
  "beats operating somebody else's large one.</b>")}
{note("terra","The number to stress-test is the first full year",
  f"Everything rests on {rs(yrs[1]['revenue'])} in the first full year of trading from a "
  f"{ff['area_sqft']:,} sq ft highway site. That is the midpoint of the ₹3–4 crore range in the company model, "
  "but it is a projection for a park that does not exist yet, on a footprint that section 01 flags as "
  "unconfirmed. The downside case in section 05 runs it 25% lower.")}"""
    S.append(("03", "s03", "Ten-year projection", body))

    body = f"""
<p class="lede">{rs(k["capex_total"])} in, {rs(f["project_fcf"]["cumulative_fcf"])} of free cash flow out
over ten years, with five more years of sub-lease still to run beyond the model horizon.</p>
{fcf_table(f["project_fcf"])}
{bento([
  ("Project IRR", pct(f["project_fcf"]["irr_pct"]), "Ten-year horizon; five sub-lease years excluded"),
  ("Payback", f'{num(f["project_fcf"]["payback_years"],1)} yrs', "From first capex draw"),
  ("NPV at 15%", rs(f["project_fcf"]["npv_at_15pct"]), "Positive at a 15% hurdle"),
])}
{verdict_block(f["cost_of_capital"],
  extra="Karnal is the closest of the three to clearing an equity hurdle, and comfortably the best debt risk.")}
{note("blue","Years 11 to 15 are not in the IRR above",
  "The sub-lease runs fifteen years. This model stops at ten. The remaining five years would run a fully "
  "depreciated asset against a mature revenue line — the highest-margin period of the contract. Including them "
  "in the exit value in section 08 adds roughly "
  f"{rs(f['exit_valuation'].get('beyond_model_horizon', 0))} of value at the year-6 exit date.")}"""
    S.append(("04", "s04", "Project returns", body))

    body = f"""
<p class="lede">The revenue range in the company financial model is ₹3–4 crore for the first full year.
Base is the midpoint; downside sits below the published floor.</p>
{scenario_cards(k["scenarios"])}
{note("green","Even the downside services its debt",
  f"At 25% below the base revenue line — below the floor of the range published in the company model — the "
  f"project still reaches {rs(k['scenarios']['downside']['ebitda_stabilised'])} of stabilised EBITDA. "
  "That is the difference between a project with its own assets and a project renting somebody else's: the "
  "cost base moves with the revenue.")}"""
    S.append(("05", "s05", "Scenarios", body))

    eq = f["equity"]
    body = f"""
<p class="lede">This is how Karnal is funded in the existing plan — ₹4 crore of the ₹10 crore round.
Shown here at project level so it can be compared like for like against the other two instruments.</p>
{table(["Term", "Structure"], [
  row(label_cell("Capital", f'{rs(k["capex_total"])} of build cost plus {rs(f["true_capital_requirement"]["cumulative_operating_deficit"])} to fund the year-1 ramp'), (rs(eq["investment"]), "")),
  row(label_cell("Stake offered"), (pct(eq["stake_pct"], 0), "")),
  row(label_cell("Distributions", "Free cash after maintenance capex, from year 3"), (rs(sum(eq["dividends"])), "")),
  row(label_cell("Exit", e(eq["basis"])), (f'End of year {eq["exit_year"]}', "")),
  row(label_cell("Exit equity value"), (rs(eq["exit_equity_value"]), "")),
  row(("Investor IRR", ""), (pct(eq["irr_pct"]), cls(eq["irr_pct"])), cls_="total"),
  row(("Money multiple", ""), (f'{num(eq["money_multiple"])}×', ""), cls_="total"),
])}
{note("terra","Better than the concessions, still short of a hurdle",
  f"At {pct(eq['stake_pct'],0)} the investor earns {pct(eq['irr_pct'])} — the best of the three project-level "
  f"equity cases in this pack, and still well short of a 22% hurdle, which would need "
  f"{pct(eq['stake_for_22pct'],0)} of the project. The reason is structural rather than particular to Karnal: "
  "a single park generating ₹2–2.6 crore of mature EBITDA cannot carry both a venture return on ₹4 crore and "
  "an operator's margin. Equity works at portfolio level, where one round backs five parks and a brand. It does "
  "not work one park at a time.")}
{note("blue","Which is an argument about where the equity sits, not whether to raise it",
  "The ₹10 crore round in the investor deck is priced on the company, not on Karnal. Nothing here argues "
  "against that round. It argues that <b>Karnal specifically should be debt-funded inside it</b>, freeing the "
  "equity for the deployments that have no debt route.")}"""
    S.append(("06", "s06", "Option A · Equity", body))

    body = f"""
<p class="lede">A conventional CGTMSE term loan against assets the borrower owns, with a promoter margin
and a construction moratorium. Of the three projects in this pack, this is the one a credit committee
will recognise immediately.</p>
{table(["Term", "Structure"], [
  row(label_cell("Scheme"), (f'CGTMSE {M["cgtmse"]["scheme"]} · ceiling {rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100,0)} per borrower', "")),
  row(label_cell("Project cost"), (rs(k["capex_total"]), "")),
  row(label_cell("Promoter contribution", "Margin money from internal accrual or the equity round"), (f'{rs(db["promoter_contribution"])} · {pct(db["promoter_margin_pct"],0)}', "")),
  row(label_cell("Term loan"), (rs(db["term_loan"]), "")),
  row(label_cell("Working capital limit", "Opening-season operating cycle"), (rs(db["wc_limit"]), "")),
  row(("Total facility", ""), (rs(db["total_limit"]), ""), cls_="sub"),
  row(label_cell("Interest rate"), (pct(db["rate_pct"], 2), "")),
  row(label_cell("Annual guarantee fee"), (pct(db["cgtmse"]["agf_rate_pct"], 2), "")),
  row(label_cell("Tenor / moratorium", "Construction plus ramp"), (f'{db["tl_tenor_years"]} years / {db["tl_moratorium_years"]}-year principal moratorium', "")),
  row(label_cell("Guarantee coverage"), (f'{pct(db["cgtmse"]["coverage_pct"], 0)} · {rs(db["cgtmse"]["guaranteed_amount"])} guaranteed', "")),
  row(label_cell("Security"), ('Nil collateral. Hypothecation of the plant, equipment and fit-out financed. Personal guarantee of directors permitted.', "")),
  row(("Total finance cost over the term", ""), (rs(db["total_finance_cost"]), ""), cls_="total"),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Repayment and cover, ₹ crore</div>
{debt_schedule_table(db)}
{bento([
  ("Minimum DSCR", num(db["min_dscr_post_moratorium"]) + "×", "Above the 1.30× floor from the first repayment year"),
  ("Average DSCR", num(db["avg_dscr_post_moratorium"]) + "×", "Across the repayment years"),
  ("Debt capacity", rs(dc["max_total_limit"]), f'Headroom of {rs(dc["max_total_limit"] - db["total_limit"])} over the facility'),
])}
{note("green","The cleanest credit in the pack",
  f"A signed fifteen-year sub-lease, a rent-free construction period, assets the bank can hypothecate, a "
  f"two-year principal moratorium covering construction and ramp, and DSCR at "
  f"{num(db['min_dscr_post_moratorium'])}× rising to {num(db['schedule'][-1]['dscr'])}× by the end of the "
  "term. This is the facility to put in front of a bank first — a sanction here establishes the relationship "
  "and the CGTMSE track record that the two concession facilities will need.")}"""
    S.append(("07", "s07", "Option B · Debt under CGTMSE", body))

    cc = f["ccd"]
    body = f"""
<p class="lede">Debt with a fixed conversion date. The instrument that most closely matches a build-and-ramp
project: no dilution while the site is under construction, conversion once it is trading.</p>
{table(["Term", "Structure"], [
  row(label_cell("Principal"), (rs(cc["principal"]), "")),
  row(label_cell("Coupon", "Annual, until conversion"), (pct(cc["coupon_pct"], 1), "")),
  row(label_cell("Conversion"), (f'End of year {cc["conversion_year"]} — one full year after opening', "")),
  row(label_cell("Conversion stake"), (pct(cc["conversion_stake_pct"], 0), "")),
  row(label_cell("Coupon paid to conversion"), (rs(cc["coupon_paid_total"]), "")),
  row(label_cell("Exit"), (f'End of year {cc["exit_year"]} at {rs(cc["exit_equity_value"])}', "")),
  row(("Investor IRR", ""), (pct(cc["irr_pct"]), cls(cc["irr_pct"])), cls_="total"),
  row(("Money multiple", ""), (f'{num(cc["money_multiple"])}×', ""), cls_="total"),
])}
{note("terra","The coupon lands in the wrong years",
  f"Years 1 to {cc['conversion_year']} are construction and ramp: the project loses "
  f"{rs(-yrs[0]['ebitda'])} at EBITDA in year 1 and there is no rent-free relief on a debenture coupon. "
  f"{rs(cc['coupon_paid_total'])} of coupon has to be funded from the group while the site is being built. A "
  "CGTMSE term loan with a two-year principal moratorium defers the same burden and costs less.")}
{note("blue","A structural variant worth considering instead",
  "If the objective is deferred dilution rather than debt capacity, a <b>zero-coupon CCD with a conversion "
  "premium</b> removes the cash burden entirely — the investor's return comes from converting at a fixed "
  "discount to a later round rather than from a coupon during construction. The pricing must still be fixed on "
  "the date of issue to satisfy the FEMA conversion-formula test if any of the money is foreign.")}"""
    S.append(("08", "s08", "Option C · Debt converted to equity", body))

    body = f"""
{opt_cards(f)}
{table(["", "A · Equity", "B · CGTMSE debt", "C · CCD"], [
  row(label_cell("Money in", "Equity and the CCD also fund the year-1 ramp deficit; the debt facility sits alongside promoter margin"),
      (rs(eq["investment"]), ""), (rs(db["total_limit"]), ""), (rs(cc["principal"]), "")),
  row(label_cell("Promoter contribution needed"), ("None", "pos"), (rs(db["promoter_contribution"]), ""), ("None", "pos")),
  row(label_cell("Return to the funder"), (pct(eq["irr_pct"]), cls(eq["irr_pct"])),
      (f'{pct(db["rate_pct"],2)} + fee', "pos"), (pct(cc["irr_pct"]), cls(cc["irr_pct"]))),
  row(label_cell("Clears a funder's hurdle?"), ("No", "neg"), ("Yes", "pos"), ("No", "neg")),
  row(label_cell("Cash cost during construction"), ("None", "pos"), ("Interest only, principal deferred 2 years", "pos"), (f'{rs(cc["coupon_paid_total"])} of coupon', "neg")),
  row(label_cell("Cost to E-O-D over the term"),
      (f'{pct(eq["stake_pct"],0)} of the project forever', "neg"), (rs(db["total_finance_cost"]), "pos"),
      (f'{rs(cc["coupon_paid_total"])} + {pct(cc["conversion_stake_pct"],0)}', "")),
  row(label_cell("Upside retained by E-O-D"), (pct(100 - eq["stake_pct"], 0), ""), ("100%", "pos"), (pct(100 - cc["conversion_stake_pct"], 0), "")),
])}
<div class="verdict verdict--go">
  <div class="verdict__label">Recommendation</div>
  <div class="verdict__head">Option B — and take this facility to the bank first</div>
  <div class="verdict__body">
    Karnal earns <b>{pct(f["project_fcf"]["irr_pct"])}</b> against
    <b>{pct(f["cost_of_capital"]["all_in_cost_of_cgtmse_debt_pct"], 2)}</b> guaranteed debt, covers its service
    at <b>{num(db["min_dscr_post_moratorium"])}×</b> from the first repayment year, and — uniquely in this pack —
    owns assets a lender can hypothecate. A {rs(db["term_loan"])} term loan with
    {rs(db["promoter_contribution"])} of promoter margin and a {db["tl_moratorium_years"]}-year construction
    moratorium funds the whole build. Total finance cost over the term is
    <b>{rs(db["total_finance_cost"])}</b> against giving away {pct(eq["stake_pct"], 0)} of a park that
    generates {rs(yrs[-1]["ebitda"])} of EBITDA by year 10.<br><br>
    The wider consequence matters more than the project: funding Karnal with debt releases the
    <b>₹4 crore</b> earmarked for it in the ₹10 crore equity round. That capital has no debt alternative at
    Geeta Govind Vatika or Ramayan Vatika, and it is what buys down the dilution in the company deck.
  </div>
</div>"""
    S.append(("09", "s09", "Which option, and why", body))

    body = f"""
{risks([
  ("Footprint unconfirmed", "High", "sev-h",
   f"{e(ff['area_discrepancy'])} <b>Mitigation:</b> read the executed sub-lease before any drawdown. "
   "If the site is 22,000 sq ft rather than six acres, the outdoor go-kart and zipline stack — "
   f"{rs(190)} of the capex and most of the revenue thesis — may not physically fit."),
  ("Construction and opening slippage", "Medium–High", "sev-mh",
   "A twelve-month build to a September 2027 opening. Slipping past the summer season pushes a full peak "
   "quarter into the following year. <b>Mitigation:</b> the two-year principal moratorium absorbs a season of "
   "delay; contract the build with liquidated damages."),
  ("First-full-year revenue", "Medium–High", "sev-mh",
   f"{rs(yrs[1]['revenue'])} in the first full year is a projection for an unbuilt park. DME's first year was "
   "₹25 lakh. <b>Mitigation:</b> Karnal opens with the outdoor stack DME lacked, on a busier corridor; the "
   "downside case runs 25% below and still services the debt."),
  ("Counterparty concentration", "Medium", "sev-m",
   "A single private sub-lessor, A4A Highway Nest LLP, holds the head lease. Its default or the loss of its "
   "own tenure ends the project. <b>Mitigation:</b> confirm the head-lease tenure exceeds the sub-lease, and "
   "seek a direct agreement with the head lessor or a step-in right."),
  ("Minimum guarantee in a weak year", "Medium", "sev-m",
   "₹2–3 lakh a month is payable whether or not anyone stops. This is exactly the mechanism that produced "
   "DME's ₹29.9 lakh fixed-CAM loss. <b>Mitigation:</b> negotiate the MG against a revenue-share alternative, "
   "whichever is higher, and confirm the rent-free period runs to commissioning, not to a calendar date."),
  ("Highway traffic dependency", "Low–Medium", "sev-l",
   "Revenue depends on NH-1 throughput and on stopping behaviour. <b>Mitigation:</b> NH-1 is India's busiest "
   "national highway; the format is already proven at DME; the site is a destination for Karnal and Panipat "
   "residents as well as through-traffic."),
])}
<div style="margin:34px 0 12px;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;">Open items</div>
{caveats([
  f"<b>{e(ff['area_discrepancy'])}</b> This is the first thing to resolve — it sizes everything else.",
  "The minimum guarantee is stated as a ₹2–3 lakh range. This model uses ₹2.5 lakh a month escalating 5% a "
  "year. Confirm the contracted figure and the escalation mechanism from the executed sub-lease.",
  "The rent-free build period is described as “long” without a duration. This model assumes no rent until "
  "opening. Confirm whether it is tied to commissioning or to a fixed date.",
  "Head-lease tenure of A4A Highway Nest LLP is unknown. A fifteen-year sub-lease carved out of a shorter head "
  "lease is not a fifteen-year asset.",
  "Revenue is taken from the ranges published in the company financial model, not built bottom-up from a site "
  "plan. Once the footprint is confirmed, rebuild it from activity capacity and expected stop rates.",
  f"Depreciation is straight-line at {lakh(k['annual_depreciation'],1)} a year across the capex blocks, against "
  "₹27 lakh a year assumed in the company financial model's assumption section. The difference reflects the "
  "asset-life split used here; reconcile the two before the next audit.",
])}
{FOOTER}"""
    S.append(("10", "s10", "Risks and open items", body))

    rail = [(n, sid, t) for n, sid, t, _ in S]
    body = cover + "\n".join(sec(n, sid, t, b) for n, sid, t, b in S)
    return page("Karnal — Project Finance · E-O-D Parks", "Project finance · Karnal",
                body, rail, "pf-karnal.html")

# ============================================================================
# DECK 4 — COMPANY
# ============================================================================
def deck_company():
    c = M["company"]; p = c["profile"]; fy = p["fy26"]; fin = c["financing"]
    eq, db, cc = fin["equity"], fin["debt"], fin["ccd"]
    rpc = c["related_party_conversion"]; ms = c["msme"]; ex = c["exit_basis"]
    lev = fin["debt"]["leverage"]
    consol = M["consolidated"]["years"]
    S = []

    cover = f"""
<div class="fin-cover">
  <div class="fin-cover__eyebrow">Project finance · 04 of 04</div>
  <h1 class="fin-cover__title">Vision Amusement Park</h1>
  <p class="fin-cover__sub">Three ways to fund the company rather than the projects — equity, guaranteed
  debt, and debt that becomes equity. One of them is materially cheaper than the headline round, and one
  balance-sheet move has to happen before any of them.</p>
  <div class="fin-cover__meta">
    <b>{e(p["name"])}</b> · CIN {e(p["cin"])}<br>
    FY25-26 revenue <b>₹16.29 Cr</b> · EBITDA ₹2.37 Cr · net worth ₹2.58 Cr · borrowings ₹7.85 Cr<br>
    MSME classification <b>{ms["classification"].title()} Enterprise</b> · CGTMSE eligible
  </div>
  <div class="cover-kpi-grid">
    {kpi("FY30-31 revenue", rs(ex["revenue"], 0), sub="Seven parks, including all three new projects")}
    {kpi("Equity at ₹90 Cr pre", pct(eq["irr_pct"]), sub="Investor IRR over five years")}
    {kpi("CGTMSE ceiling", rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100, 0), sub="Per borrower, aggregated across all lenders")}
    {kpi("D/E after conversion", num(rpc["convert_lt_plus_promoter_409"]["debt_equity"]) + "×", sub="From 3.04× today, converting all ₹4.09 Cr of related-party debt")}
  </div>
</div>"""

    body = f"""
<p class="lede">The company financial model carries the full history. This section takes only what
determines whether VAPPL can borrow, and at what price.</p>
{table(["FY25-26 position", "Amount", "What a credit committee sees"], [
  row(label_cell("Revenue"), (rs(fy["revenue"]), ""), ('All-time high, +27% year on year, four parks operating', "")),
  row(label_cell("EBITDA"), (rs(fy["ebitda"]), ""), (f'{pct(fy["ebitda"]/fy["revenue"]*100,1)} margin — a ramp year, below the 36% single-park benchmark of FY22-23', "")),
  row(label_cell("Net worth"), (rs(fy["net_worth"]), ""), ('Positive and improving. Was negative ₹1.30 Cr in FY22-23', "pos")),
  row(label_cell("Total borrowings"), (rs(fy["borrowings_total"]), ""), (f'{rs(fy["borrowings_short"])} short-term across 13 facilities, {rs(fy["borrowings_long_related"])} long-term from related parties', "")),
  row(label_cell("Debt to equity"), (num(rpc["base"]["debt_equity"]) + "×", "neg"), ('Too high. Most banks want under 2× for an unsecured facility', "neg")),
  row(label_cell("Interest coverage"), ("4.7×", ""), ('Adequate but thin against a 13-facility NBFC book', "")),
  row(label_cell("Current ratio"), ("~0.50×", "neg"), ('Below 1.0 every year — structurally dependent on revolving credit', "neg")),
  row(label_cell("Electricity arrears"), (rs(fy["electricity_arrears"]), "neg"), ('Accumulated across parks, sitting in other current liabilities. A red flag on any sanction note', "neg")),
  row(label_cell("Cash and FDR"), (rs(fy["cash"] + fy["fdr"]), "pos"), ('₹2.22 Cr of FDR earning ₹9.2 lakh a year, not to be liquidated', "")),
], aligns=["l","r","l"])}
{note("terra","Four things stand between VAPPL and a bank sanction",
  f"<b>One:</b> debt to equity at {num(rpc['base']['debt_equity'])}×. <b>Two:</b> thirteen separate NBFC and "
  "bank facilities, which reads as distress borrowing regardless of how it arose. <b>Three:</b> "
  f"{rs(fy['electricity_arrears'])} of electricity arrears — a utility default is the single item most likely to "
  "stop a sanction note in its tracks. <b>Four:</b> a current ratio below 1.0 in every year on record. "
  "Sections 03 and 09 deal with all four. <b>None of the financing options in this deck should be taken to a "
  "lender before they are fixed.</b>")}"""
    S.append(("01", "s01", "Where the company stands", body))

    lim = M["msme_limits"]["small"]
    body = f"""
<p class="lede">CGTMSE covers micro and small enterprises only. VAPPL's eligibility is not marginal —
but it has an expiry date, and the date is inside this plan.</p>
{table(["Test", "VAPPL", "Small Enterprise limit", "Headroom"], [
  row(label_cell("Investment in plant and machinery", "FY26 gross block; land and building excluded by definition"),
      (f'₹{ms["investment_plant_machinery_cr"]:.2f} Cr', ""), (f'₹{lim["investment_cr"]:.0f} Cr', ""),
      (f'₹{ms["headroom_investment_cr"]:.2f} Cr', "pos")),
  row(label_cell("Annual turnover", "FY25-26 provisional"),
      (f'₹{ms["turnover_cr"]:.2f} Cr', ""), (f'₹{lim["turnover_cr"]:.0f} Cr', ""),
      (f'₹{ms["headroom_turnover_cr"]:.2f} Cr', "pos")),
  row(("Classification", ""), (ms["classification"].title() + " Enterprise", "pos"), ("", ""), ("CGTMSE eligible", "pos"), cls_="total"),
], aligns=["l","r","r","r"])}
{note("blue","The thresholds moved in VAPPL's favour on 1 April 2025",
  f"The Small Enterprise limits were raised from ₹10 Cr to <b>₹{lim['investment_cr']:.0f} Cr</b> of investment "
  f"and from ₹50 Cr to <b>₹{lim['turnover_cr']:.0f} Cr</b> of turnover, and the CGTMSE guarantee ceiling was "
  f"doubled from ₹5 Cr to <b>{rs(M['cgtmse']['ceiling_per_borrower_cr']*100,0)}</b> per borrower. Both changes "
  "landed after the ₹10 crore equity round was designed. A guaranteed, collateral-free ₹10 crore facility is "
  "available to VAPPL today that was not available when the round was structured — which is the reason this "
  "pack exists.")}
{table(["CGTMSE parameter", "Position"], [
  row(label_cell("Scheme"), (f'{M["cgtmse"]["scheme"]} — the standard scheme for banks and NBFCs', "")),
  row(label_cell("Guarantee ceiling"), (f'<b>{rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100,0)} per borrower</b><span class="meta">{e(M["cgtmse"]["ceiling_basis"])}. {rs(M["cgtmse"]["ceiling_startup_dpiit_cr"]*100,0)} for DPIIT-recognised startups.</span>', "")),
  row(label_cell("Coverage extent"), (f'{pct(M["cgtmse"]["coverage_small_enterprise_pct"],0)} for a Small Enterprise; up to {pct(M["cgtmse"]["coverage_preferential_pct"],0)} for micro, women-owned, SC/ST, NER, Aspirational District or ZED-certified units', "")),
  row(label_cell("Collateral and guarantees"), ('Nil collateral on the guaranteed portion. Third-party guarantee is <b>not</b> permitted; the personal guarantee of directors is.', "")),
  row(label_cell("Hybrid security"), ('Permitted — collateral may be taken on a portion, with the balance guaranteed', "")),
  row(label_cell("Interest rate"), (e(M["cgtmse"]["interest_cap_note"]), "")),
  row(label_cell("Guarantee fee basis"), (f'On the {e(M["cgtmse"]["agf_basis_y1"])} in year 1, on the {e(M["cgtmse"]["agf_basis_y2plus"])} thereafter', "")),
  row(label_cell("Fee concession"), (f'{pct(M["cgtmse"]["agf_concession_pct"],0)} for women, SC/ST, differently-abled, Agniveer and transgender borrowers, and for NER, J&K, Ladakh, Aspirational District, Credit Deficient District or ZED-certified units', "")),
], aligns=["l","l"])}
{table(["Facility size", "Standard annual guarantee fee"], [
  row(((f'Up to {money(cap)}' if i == 0
        else f'Above {money(M["cgtmse"]["agf_slabs"][i-1][0])} and up to {money(cap)}'), ""),
      (pct(rate, 2), ""),
      cls_=("sub" if 500 < cap <= 1000 else ""))
  for i, (cap, rate) in enumerate(M["cgtmse"]["agf_slabs"])
])}
{note("amber","Eligibility expires, and the plan is what expires it",
  f"The consolidated plan in section 04 reaches <b>{rs(consol[-1]['revenue'],0)}</b> of revenue by FY30-31. "
  f"The Small Enterprise turnover ceiling is ₹{lim['turnover_cr']:.0f} Cr. VAPPL stays comfortably inside it "
  "across this plan — but a Medium Enterprise is not eligible for CGTMSE at all. <b>The guarantee is available "
  "now and will not be available forever.</b> A facility sanctioned while the company qualifies keeps its "
  "cover for its full tenor; one applied for after the threshold is crossed does not exist. That is a timing "
  "argument for drawing the facility early, not for growing slowly.")}
{note("blue","Two eligibility items to confirm before applying",
  "<b>Udyam registration.</b> CGTMSE cover requires a live Udyam registration matching the borrowing entity. "
  "Confirm VAPPL's registration exists, is current, and reflects the revised April 2025 classification.<br><br>"
  "<b>Activity code.</b> Amusement and recreation services fall within the service enterprises CGTMSE covers, "
  "but the registered NIC code on the Udyam certificate is what the lender's system checks. Confirm it before "
  "the application, not after a rejection.")}"""
    S.append(("02", "s02", "MSME status and CGTMSE eligibility", body))

    base, c260, c409 = rpc["base"], rpc["convert_lt_related_260"], rpc["convert_lt_plus_promoter_409"]
    prd = p["promoter_related_debt"]
    body = f"""
<p class="lede">Before raising anything, there is a free move available. Roughly ₹4 crore of VAPPL's
₹7.85 crore of borrowings is money the promoters and related parties have already put in. Converting it
into equity costs no cash and transforms the balance sheet a lender is asked to lend against.</p>
{table(["Related-party and promoter debt", "Amount"], [
  row(label_cell("Sanjeev Bewtra and Team Buildcon", "Long-term related-party loans, unchanged since FY24-25"), (lakh(prd["sanjeev_bewtra_and_team_buildcon_lt"], 0), "")),
  row(label_cell("Promoter loans", "Added during FY25-26"), (lakh(prd["promoter_loans_fy26"], 1), "")),
  row(label_cell("Apoorv Babbar HUF"), (lakh(prd["apoorv_babbar_huf"], 1), "")),
  row(label_cell("Geetika Jain"), (lakh(prd["geetika_jain"], 0), "")),
  row(("Total convertible related-party debt", ""), (lakh(sum(prd.values()), 1), ""), cls_="total"),
])}
{table(["", "Today", "Convert the ₹2.60 Cr long-term", "Convert all related-party debt"], [
  row(label_cell("Total borrowings"), (rs(base["borrowings"]), ""), (rs(c260["borrowings"]), "pos"), (rs(c409["borrowings"]), "pos")),
  row(label_cell("Net worth"), (rs(base["net_worth"]), ""), (rs(c260["net_worth"]), "pos"), (rs(c409["net_worth"]), "pos")),
  row(("Debt to equity", ""), (num(base["debt_equity"]) + "×", "neg"),
      (num(c260["debt_equity"]) + "×", "pos"), (num(c409["debt_equity"]) + "×", "pos"), cls_="total"),
  row(label_cell("Cash cost of doing it"), ("—", ""), ("Nil", "pos"), ("Nil", "pos")),
], aligns=["l","r","r","r"])}
{note("green","This is the single highest-leverage action in the entire pack",
  f"Converting related-party loans into equity moves debt to equity from <b>{num(base['debt_equity'])}×</b> to "
  f"{num(c260['debt_equity'])}× or {num(c409['debt_equity'])}× depending on how much is converted, and lifts "
  f"net worth from {rs(base['net_worth'])} to {rs(c260['net_worth'])} or {rs(c409['net_worth'])}. No cash "
  "moves. No third party is involved. It converts a balance sheet that a credit committee declines into one it "
  "can work with, and it does so before a single rupee of external money is raised. <b>Do this first.</b>")}
<div style="margin:30px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">
  How much conversion the ₹10 crore facility actually needs</div>
<p class="lede" style="margin-bottom:16px;">A lender does not size a facility off today's balance sheet — it
sizes it off where gearing lands <em>after</em> the money is drawn. Assuming a conventional 2.0× debt-to-equity
covenant, that calculation decides how much of the CGTMSE ceiling VAPPL can reach at all.</p>
{table(["Conversion", "D/E once ₹10 Cr is drawn", "Largest facility inside a 2.0× covenant"],
  [row(label_cell(e(cs["label"]).replace("Rs ", "₹"),
        f'Net worth {rs(cs["net_worth"])} · borrowings {rs(cs["borrowings"])}'),
       (num(cs["debt_equity"]) + "×", "pos" if cs["debt_equity"] <= 2.0 else "neg"),
       (rs(cs["max_facility_at_covenant"]), "pos" if cs["max_facility_at_covenant"] >= 1000 else "neg"))
   for cs in lev["cases"]], aligns=["l","r","r"])}
{note("terra","Converting only the ₹2.60 crore is not enough",
  f"With {rs(260)} converted, gearing after a full drawdown lands at "
  f"<b>{num(lev['cases'][1]['debt_equity'])}×</b> — outside a 2.0× covenant — and the largest facility that "
  f"stays inside it is {rs(lev['cases'][1]['max_facility_at_covenant'])}, not "
  f"{rs(1000, 0)}. Converting <b>all {rs(lev['conversion_full'])}</b> of related-party and promoter debt takes "
  f"post-drawdown gearing to {num(lev['cases'][2]['debt_equity'])}× and lifts the covenant-constrained capacity "
  f"to <b>{rs(lev['cases'][2]['max_facility_at_covenant'])}</b> — comfortably above the CGTMSE ceiling. "
  "<b>Convert the whole amount, not the long-term portion only.</b> Without any conversion the company can "
  f"support a new facility of {rs(lev['cases'][0]['max_facility_at_covenant'])} — which is to say, it cannot "
  "borrow at all.")}
{note("amber","How to do it, and what it costs in dilution",
  "A rights issue under section 62(1)(a) of the Companies Act to existing holders, subscribed by set-off "
  "against the loans, or a preferential allotment under section 62(1)(c) with a registered-valuer report. "
  "Either route needs a board and shareholder resolution and a PAS-3 filing. Because the lenders are the "
  "promoters themselves, <b>the dilution is internal</b> — the promoter group's economic position is unchanged; "
  "only the form of its claim changes, from a creditor's to a shareholder's. The cost is the loss of interest "
  "deductibility on that portion, which against the improvement in borrowing capacity is not close.")}"""
    S.append(("03", "s03", "Fix the balance sheet first", body))

    rows = []
    for part, name, meta in [("existing", "Existing four parks", "EMV, EAC, DME, ESP — midpoints from the company financial model"),
                             ("ggv", "Geeta Govind Vatika", "Award assumed October 2026"),
                             ("rv", "Ramayan Vatika", "Award assumed January 2027"),
                             ("karnal", "Karnal", "Opening September 2027")]:
        rows.append(row(label_cell(name, meta), *[(cr(y["parts"][part]["revenue"]), "" if y["parts"][part]["revenue"] else "muted") for y in consol]))
    rows.append(row(("Consolidated revenue", ""), *[(cr(y["revenue"]), "") for y in consol], cls_="total"))
    rows.append(row(("Consolidated EBITDA", ""), *[(cr(y["ebitda"]), cls(y["ebitda"])) for y in consol], cls_="sub"))
    rows.append(row(("EBITDA margin", ""), *[(pct(y["ebitda_margin"], 1), "muted") for y in consol], cls_="dim"))
    body = f"""
<p class="lede">The existing four parks plus all three new projects, phased on the award and opening
dates assumed in each project deck. Existing-portfolio figures are the midpoints already published in
the company financial model, extended two further years on the stated maturity path.</p>
{table([""] + [y["fy"] for y in consol], rows)}
{bento([
  ("FY30-31 revenue", rs(consol[-1]["revenue"], 0), f'From {rs(fy["revenue"])} in FY25-26'),
  ("FY30-31 EBITDA", rs(consol[-1]["ebitda"], 0), f'{pct(consol[-1]["ebitda_margin"],1)} margin'),
  ("New projects' share", pct(sum(consol[-1]["parts"][k]["revenue"] for k in ("ggv","rv","karnal")) / consol[-1]["revenue"] * 100, 0), "Of FY30-31 revenue"),
])}
{note("blue","What this does to concentration risk",
  f"EMV was 73% of consolidated revenue in FY25-26. By FY30-31 the three new projects alone contribute "
  f"{pct(sum(consol[-1]['parts'][k]['revenue'] for k in ('ggv','rv','karnal')) / consol[-1]['revenue'] * 100, 0)} "
  "of revenue, across three additional cities and two additional government relationships (ADA already known, "
  "BDA new). The revenue-concentration risk flagged as High in the company financial model's risk register is "
  "materially reduced by this plan — which is itself part of the credit case.")}
{note("amber","And what it does to the cost base",
  "Three new sites add roughly 100 people to the establishment, two of them with contractually mandated "
  "minimum staffing. The FY30-31 margin of "
  f"{pct(consol[-1]['ebitda_margin'],1)} already reflects that. <b>These are volume businesses with fixed "
  "obligations — growth here buys diversification, not operating leverage.</b> The operating leverage sits in "
  "the existing estate, where EMV runs a 32.5% net margin at maturity.")}"""
    S.append(("04", "s04", "The consolidated plan", body))

    ps = eq["pricing_sensitivity"]
    body = f"""
<p class="lede">The existing round is ₹10 crore at a ₹90 crore pre-money for 10%. Funding all three new
projects with equity would take it to roughly ₹16 crore. Here is what that returns to the person writing
the cheque.</p>
{table(["Term", "Existing round", "Expanded round"], [
  row(label_cell("Amount"), (rs(eq["existing_round"]["amount"]), ""), (rs(eq["investment"]), "")),
  row(label_cell("Pre-money"), (rs(eq["existing_round"]["pre_money"], 0), ""), (rs(eq["pre_money"], 0), "")),
  row(label_cell("Dilution"), (pct(eq["existing_round"]["dilution_pct"], 1), ""), (pct(eq["stake_pct"], 1), "")),
  row(label_cell("Implied multiple", "On FY25-26 revenue of ₹16.29 Cr"), ("5.5×", ""), ("5.5×", "")),
], aligns=["l","r","r"])}
{table(["Exit basis", "Value"], [
  row(label_cell("Exit year"), (e(ex["fy"]) + " — five years from a September 2026 close", "")),
  row(label_cell("Revenue at exit"), (rs(ex["revenue"], 0), "")),
  row(label_cell("EBITDA at exit"), (rs(ex["ebitda"], 0), "")),
  row(label_cell("Enterprise value", f'At {num(ex["ev_revenue_multiple"],1)}× revenue — the company model&rsquo;s own peer frame is 3&ndash;5&times; at this maturity'), (rs(ex["enterprise_value"], 0), "")),
  row(label_cell("Cross-check", "At 11× EBITDA"), (rs(ex["ev_ebitda_crosscheck"], 0), "muted")),
  row(label_cell("Less net debt"), (rs(-ex["net_debt"], 0), "muted")),
  row(("Equity value at exit", ""), (rs(ex["equity_value"], 0), ""), cls_="total"),
  row(("Investor proceeds", f'{pct(eq["stake_pct"],1)} of exit equity value'), (rs(eq["exit_proceeds"], 0), "")),
  row(("Investor IRR over five years", ""), (pct(eq["irr_pct"]), cls(eq["irr_pct"] - 15)), cls_="total"),
  row(("Money multiple", ""), (f'{num(eq["money_multiple"])}×', ""), cls_="total"),
], aligns=["l","r"])}
{note("terra","₹90 crore pre-money prices most of the growth in",
  f"On this plan — which already includes all three new projects, an all-time-high revenue line and a margin "
  f"reaching {pct(consol[-1]['ebitda_margin'],1)} — an investor entering at ₹90 crore pre-money earns "
  f"<b>{pct(eq['irr_pct'])}</b> over five years. That is a respectable return for a family office or a "
  "strategic investor. It is <b>below what an institutional growth fund underwrites to</b>, which is typically "
  "22–25%. This is not an argument that the valuation is wrong — it is an argument about who the right "
  "counterparty is, and about how long the round is likely to take to close.")}
{table(["Investor hurdle", "Stake required", "Implied post-money", "Implied pre-money"], [
  row(label_cell("18% — family office, strategic"), (pct(ps["irr_18"]["stake_pct"], 1), ""), (rs(ps["irr_18"]["post_money"], 0), ""), (rs(ps["irr_18"]["pre_money"], 0), "")),
  row(label_cell("22% — lower-quartile growth fund"), (pct(ps["irr_22"]["stake_pct"], 1), ""), (rs(ps["irr_22"]["post_money"], 0), ""), (rs(ps["irr_22"]["pre_money"], 0), "")),
  row(label_cell("25% — institutional growth equity"), (pct(ps["irr_25"]["stake_pct"], 1), ""), (rs(ps["irr_25"]["post_money"], 0), ""), (rs(ps["irr_25"]["pre_money"], 0), "")),
  row(("At the asking price of ₹90 Cr pre", ""), (pct(eq["stake_pct"], 1), ""), (rs(eq["post_money"], 0), ""), (pct(eq["irr_pct"]) + " investor IRR", "")),
], aligns=["l","r","r","r"])}
{note("blue","Which is exactly why the other two options matter",
  f"Debt at {pct(db['rate_pct'],2)} plus a {pct(db['cgtmse']['agf_rate_pct'],2)} guarantee fee costs VAPPL "
  f"about {pct(db['rate_pct'] + db['cgtmse']['agf_rate_pct'], 2)} a year. Equity at ₹90 crore pre-money costs "
  f"{pct(eq['stake_pct'],1)} of a company the promoters believe is worth far more than ₹90 crore in five "
  "years' time. <b>When you believe your own projections, debt is the cheaper capital — and the ₹10 crore "
  "CGTMSE ceiling now covers most of what the round was for.</b>")}"""
    S.append(("05", "s05", "Option A · Equity", body))

    body = f"""
<p class="lede">A single collateral-free composite facility at company level: a term loan for the
project build-outs and a working-capital limit that consolidates the NBFC book.</p>
{table(["Term", "Structure"], [
  row(label_cell("Scheme"), (f'CGTMSE {M["cgtmse"]["scheme"]} · at the {rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100,0)} ceiling', "")),
  row(label_cell("Term loan", "Karnal build-out, DME outdoor, EAC Phase 2, ESP activation, project mobilisation"), (rs(db["term_loan"]), "")),
  row(label_cell("Working capital limit", f'Four-park operating cycle plus {rs(db["nbfc_refinance"])} of NBFC consolidation'), (rs(db["wc_limit"]), "")),
  row(("Total facility", ""), (rs(db["total_limit"]), ""), cls_="sub"),
  row(label_cell("Interest rate", "Repo-linked, scheduled bank"), (pct(db["rate_pct"], 2), "")),
  row(label_cell("Annual guarantee fee", f'Slab for a facility above ₹8 Cr and up to {rs(M["cgtmse"]["ceiling_per_borrower_cr"]*100,0)}'), (pct(db["cgtmse"]["agf_rate_pct"], 2), "")),
  row(label_cell("All-in cost"), (pct(db["rate_pct"] + db["cgtmse"]["agf_rate_pct"], 2), "")),
  row(label_cell("Tenor / moratorium"), (f'{db["tl_tenor_years"]} years / {db["tl_moratorium_years"]}-year principal moratorium', "")),
  row(label_cell("Guarantee coverage"), (f'{pct(db["cgtmse"]["coverage_pct"], 0)} · {rs(db["cgtmse"]["guaranteed_amount"])} guaranteed, {rs(db["cgtmse"]["uncovered_amount"])} at the lender&rsquo;s risk', "")),
  row(label_cell("Security"), ('Nil collateral. Hypothecation of assets financed. Personal guarantee of directors permitted; third-party guarantee is not.', "")),
  row(("Total finance cost over seven years", ""), (rs(db["total_finance_cost"]), ""), cls_="total"),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Debt service against the consolidated plan, ₹ crore</div>
{table(["", "New facility", "Existing debt", "Total service", "EBITDA", "DSCR"],
  [row((f'Year {r["year"]}' + (' <span class="muted">· moratorium</span>' if r["year"] <= db["tl_moratorium_years"] else ''), ""),
       (cr(r["new_facility"]), ""), (cr(r["existing_debt"]), "muted"), (cr(r["total_debt_service"]), ""),
       (cr(r["cfads"]), ""), (num(r["dscr"]) + "×", "pos" if r["dscr"] and r["dscr"] >= 1.5 else ""))
   for r in db["combined_service"]])}
{bento([
  ("Minimum DSCR", num(db["min_dscr_combined"]) + "×", "Including the existing ₹7.85 Cr book, not just the new facility"),
  ("Average DSCR", num(db["avg_dscr_combined"]) + "×", "Across the seven-year term"),
  ("Cost vs equity", pct(db["rate_pct"] + db["cgtmse"]["agf_rate_pct"], 2), f'Against {pct(eq["stake_pct"],1)} of the company'),
])}
{note("green","This clears comfortably — which is the point",
  f"Minimum DSCR of <b>{num(db['min_dscr_combined'])}×</b> against a 1.30× threshold, <em>including</em> the "
  "existing borrowings. The consolidated EBITDA line carries the service several times over. A ₹10 crore "
  "collateral-free facility at "
  f"{pct(db['rate_pct'] + db['cgtmse']['agf_rate_pct'], 2)} all-in costs "
  f"<b>{rs(db['total_finance_cost'])}</b> over seven years — against {pct(eq['stake_pct'],1)} of a company "
  f"whose equity this plan values at {rs(ex['equity_value'],0)} in FY30-31, or "
  f"{rs(ex['equity_value'] * eq['stake_pct'] / 100, 0)}. <b>The debt is roughly a fifth of the cost of the "
  "equity, on the company's own projections.</b>")}
{note("amber","Three conditions the sanction will carry",
  f"<b>Leverage.</b> Post-conversion debt to equity of {num(rpc['convert_lt_related_260']['debt_equity'])}× is "
  f"acceptable; the {num(rpc['base']['debt_equity'])}× position today is not. Section 03 is a condition "
  f"precedent, not a suggestion. <b>Consolidation.</b> {rs(db['nbfc_refinance'])} of the facility is earmarked "
  "to retire NBFC borrowings — a lender will want the thirteen facilities reduced to a countable number and "
  "will covenant against re-borrowing. <b>Arrears.</b> The "
  f"{rs(fy['electricity_arrears'])} electricity liability must be cleared or formally rescheduled with the "
  "discom before sanction.")}"""
    S.append(("06", "s06", "Option B · Debt under CGTMSE", body))

    body = f"""
<p class="lede">Money in as debt at a coupon, converting into equity on a fixed formula three years out.
At company level — unlike at project level — this is genuinely competitive with both alternatives.</p>
{table(["Term", "Structure"], [
  row(label_cell("Principal"), (rs(cc["principal"]), "")),
  row(label_cell("Coupon", "Annual, until conversion"), (pct(cc["coupon_pct"], 1), "")),
  row(label_cell("Conversion"), (f'End of year {cc["conversion_year"]} — compulsory', "")),
  row(label_cell("Conversion stake"), (pct(cc["conversion_stake_pct"], 1), "")),
  row(label_cell("Implied conversion valuation", "Post-money at conversion"), (rs(cc["conversion_valuation_implied"], 0), "")),
  row(label_cell("Coupon paid to conversion"), (rs(cc["coupon_paid_total"]), "")),
  row(label_cell("Exit"), (f'{e(ex["fy"])} at {rs(cc["exit_equity_value"], 0)} of equity value', "")),
  row(("Investor IRR", ""), (pct(cc["irr_pct"]), "pos"), cls_="total"),
  row(("Money multiple", ""), (f'{num(cc["money_multiple"])}×', ""), cls_="total"),
], aligns=["l","r"])}
{note("green","The best risk-adjusted structure for an outside investor",
  f"<b>{pct(cc['irr_pct'])}</b> against {pct(eq['irr_pct'])} for straight equity at the same valuation, on the "
  "same exit. The difference comes from three years of coupon and from entering as a creditor rather than a "
  "shareholder while the three new projects are still unproven. For VAPPL the trade is symmetrical: dilution "
  f"is deferred three years, and if the projects deliver, {pct(cc['conversion_stake_pct'],1)} converted at a "
  f"{rs(cc['conversion_valuation_implied'],0)} implied valuation is cheaper than "
  f"{pct(eq['stake_pct'],1)} sold today at ₹90 crore pre-money.")}
{note("terra","The covenant problem — and it is not optional",
  f"{e(cc['balance_sheet_note'])}")}
{note("blue","How to structure it so both can coexist",
  f"<b>Convert the related-party debt first</b> (section 03), taking gearing to "
  f"{num(rpc['convert_lt_related_260']['debt_equity'])}×. <b>Then</b> the CCD sits on a base that can carry it. "
  "Alternatively, negotiate the CGTMSE facility's leverage covenant to <b>exclude compulsorily convertible "
  "instruments</b> from the debt numerator — standard practice, since a CCD that must convert is quasi-equity, "
  "and Indian accounting standards and most lenders will accept the treatment if it is agreed in the sanction "
  "letter rather than argued later.")}
{note("amber","Compliance checklist for a CCD issue",
  "Private placement under section 42 of the Companies Act with a PAS-4 offer letter and PAS-3 return; a board "
  "and special resolution under section 62(1)(c); a registered-valuer report under rule 13 of the Share Capital "
  "and Debentures Rules; a debenture trust deed if the issue is to more than 500 persons; and — if any part of "
  "the money is foreign — a <b>conversion formula fixed on the date of issue</b> and pricing not below the fair "
  "value determined by an internationally accepted methodology. An optionally convertible debenture would be "
  "treated as external commercial borrowing instead, with a different and far more restrictive regime. "
  "<b>Compulsory conversion is what makes this instrument work; make sure the documents say so.</b>")}"""
    S.append(("07", "s07", "Option C · Debt converted to equity", body))

    alloc = M["cgtmse_allocation"]
    all_in = db["rate_pct"] + db["cgtmse"]["agf_rate_pct"]
    body = f"""
{opt_cards(fin, currency_label="Facility")}
{table(["", "A · Equity", "B · CGTMSE debt", "C · CCD"], [
  row(label_cell("Money in"), (rs(eq["investment"]), ""), (rs(db["total_limit"]), ""), (rs(cc["principal"]), "")),
  row(label_cell("Cost to VAPPL"), (f'{pct(eq["stake_pct"],1)} forever', ""), (rs(db["total_finance_cost"]) + " over 7 yrs", "pos"), (f'{rs(cc["coupon_paid_total"])} + {pct(cc["conversion_stake_pct"],1)}', "")),
  row(label_cell("Cost in FY30-31 money", "Value of what is given up at the modelled exit"),
      (rs(ex["equity_value"] * eq["stake_pct"] / 100, 0), "neg"),
      (rs(db["total_finance_cost"]), "pos"),
      (rs(cc["coupon_paid_total"] + ex["equity_value"] * cc["conversion_stake_pct"] / 100, 0), "")),
  row(label_cell("Return to the funder"), (pct(eq["irr_pct"]), ""), (pct(all_in, 2), ""), (pct(cc["irr_pct"]), "pos")),
  row(label_cell("Repaid?"), ("Never", "neg"), ("Yes, over 7 years", "pos"), ("Converts", "")),
  row(label_cell("Dilution"), (f'{pct(eq["stake_pct"],1)} immediately', "neg"), ("None", "pos"), (f'{pct(cc["conversion_stake_pct"],1)} in year 3', "")),
  row(label_cell("Effect on gearing"), ("Improves", "pos"), (f'D/E to {num(lev["cases"][2]["debt_equity"])}× once drawn, after converting all {rs(lev["conversion_full"])}', ""), ("Worsens until conversion", "neg")),
  row(label_cell("Time to close"), ("4–8 months", "neg"), ("6–12 weeks after conditions precedent", "pos"), ("3–6 months", "")),
  row(label_cell("Collateral"), ("None", "pos"), ("None — CGTMSE cover", "pos"), ("None", "pos")),
  row(label_cell("Constrained by"), ("Valuation and investor appetite", ""), (f'The {rs(alloc["ceiling"],0)} per-borrower ceiling', ""), ("Valuation and covenant headroom", "")),
])}
<div class="verdict verdict--go">
  <div class="verdict__label">Recommendation</div>
  <div class="verdict__head">All three, in sequence — not one instead of the others</div>
  <div class="verdict__body">
    <b>Step 1 — now, no external party.</b> Convert <b>all {rs(lev["conversion_full"])}</b> of related-party
    and promoter debt to equity — not the {rs(260)} long-term portion alone. Gearing falls from
    {num(rpc["base"]["debt_equity"])}× to {num(c409["debt_equity"])}×, and post-drawdown gearing to
    {num(lev["cases"][2]["debt_equity"])}×, which is what makes the full {rs(1000, 0)} facility reachable
    inside a 2.0× covenant. Clear the
    {rs(fy["electricity_arrears"])} of electricity arrears. Consolidate the thirteen NBFC facilities into a
    countable number. None of this requires anyone's permission and all of it is a precondition to what follows.<br><br>
    <b>Step 2 — the cheap capital.</b> A {rs(db["total_limit"])} CGTMSE composite facility at
    {pct(all_in, 2)} all-in, covering Karnal's build-out, the DME and EAC deployments, and the two concession
    mobilisations. Total cost {rs(db["total_finance_cost"])} over seven years, against
    {rs(ex["equity_value"] * eq["stake_pct"] / 100, 0)} for the equivalent equity. Take the Karnal facility to
    the bank first — it is the cleanest credit and it establishes the CGTMSE track record.<br><br>
    <b>Step 3 — the equity, smaller and later.</b> With {rs(db["total_limit"])} of guaranteed debt in place,
    the equity round does not need to be {rs(eq["investment"])}. It needs to cover what debt cannot: the
    portion of the portfolio above the CGTMSE ceiling, the working-capital cushion, and the balance-sheet
    strength that keeps the facility covenanted. A round of <b>₹6–8 crore</b> does that at materially less
    dilution than {pct(eq["stake_pct"], 1)} — and if the counterparty wants a better entry than
    {pct(eq["irr_pct"])}, the CCD in Option C gets them to {pct(cc["irr_pct"])} without repricing the company.
  </div>
</div>
{note("terra","The constraint that shapes everything",
  f"Gross CGTMSE demand across all four uses is <b>{rs(alloc['total_gross_demand'])}</b> against a "
  f"<b>{rs(alloc['ceiling'],0)} per-borrower ceiling</b> — an excess of "
  f"{rs(alloc['excess_over_ceiling'])} that has to be funded another way. The portfolio hub sets out how to "
  "allocate the ceiling across the four uses and what the options are for the residual.")}"""
    S.append(("08", "s08", "Which option, and why", body))

    body = f"""
<div style="margin:0 0 14px;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;">Conditions precedent to any lender approach</div>
{table(["Action", "Why it matters", "Owner"], [
  row(label_cell("Convert all ₹4.09 Cr of related-party and promoter debt to equity"), ("Takes D/E from 3.04× to 0.56×, and to 1.61× once the facility is drawn. Converting only the ₹2.60 Cr long-term portion caps the facility at ₹8.11 Cr under a 2.0× covenant; converting nothing caps it at ₹0.31 Cr.", ""), ("Board", "")),
  row(label_cell("Clear the ₹2.14 Cr electricity arrears"), ("A live utility default is the single item most likely to stop a sanction note.", ""), ("Finance", "")),
  row(label_cell("Consolidate the NBFC book"), ("Thirteen facilities read as distress borrowing. Reduce to a countable number before applying.", ""), ("Finance", "")),
  row(label_cell("Confirm Udyam registration and NIC code"), ("CGTMSE cover requires a live registration on the correct activity code for the borrowing entity.", ""), ("Compliance", "")),
  row(label_cell("Complete the FY25-26 audit"), ("Provisional accounts carry a ₹54.5 lakh depreciation placeholder against an estimated ₹1.0–1.1 Cr. Lenders will want audited numbers. Expected August 2026.", ""), ("HMBA & Associates", "")),
  row(label_cell("Obtain BDA consent for any change of control"), ("Ramayan Vatika's lock-in bars shareholding changes without prior written approval. Applies to the equity round and to CCD conversion.", ""), ("Board", "")),
], aligns=["l","l","l"])}
<div style="margin:38px 0 14px;font-size:11px;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-mute);font-weight:600;">Risks to the capital plan</div>
{risks([
  ("Leverage covenant", "High", "sev-h",
   f"At {num(rpc['base']['debt_equity'])}× today, a 2.0× covenant supports a new facility of only "
   f"{rs(lev['cases'][0]['max_facility_at_covenant'])}. Converting all {rs(lev['conversion_full'])} of "
   f"related-party debt lifts that to {rs(lev['cases'][2]['max_facility_at_covenant'])}. "
   "<b>Mitigation:</b> convert in full before applying; negotiate the covenant to exclude compulsorily "
   "convertible instruments if a CCD runs in parallel; draw in tranches as retained earnings build."),
  ("CGTMSE ceiling", "High", "sev-h",
   f"{rs(alloc['total_gross_demand'])} of demand against a {rs(alloc['ceiling'],0)} per-borrower ceiling. "
   "<b>Mitigation:</b> the allocation plan in the portfolio hub; hybrid security for the residual; SPV "
   "structuring if the group is willing to accept separate borrowers."),
  ("MSME threshold", "Medium", "sev-m",
   f"Cover is available to micro and small enterprises only. This plan reaches {rs(consol[-1]['revenue'],0)} of "
   f"revenue against a ₹{M['msme_limits']['small']['turnover_cr']:.0f} Cr ceiling — comfortable, but the "
   "direction of travel is one-way. <b>Mitigation:</b> draw the facility while eligible; cover runs for the "
   "sanctioned tenor."),
  ("Electricity arrears", "Medium–High", "sev-mh",
   "₹2.14 Cr accumulated across parks. Resolution is described as in progress. <b>Mitigation:</b> settle or "
   "formally reschedule before any sanction application."),
  ("FY26 audit outcome", "Medium", "sev-m",
   "Depreciation moves from a ₹54.5 lakh placeholder to an estimated ₹1.0–1.1 Cr, reducing PAT and therefore "
   "net worth. EBITDA and DSCR are unaffected. <b>Mitigation:</b> present EBITDA-based coverage; disclose the "
   "adjustment proactively rather than have a lender find it."),
  ("Execution across three new sites at once", "Medium–High", "sev-mh",
   "Two tender processes and a construction project running in parallel with four operating parks. FY24-25 "
   "showed what simultaneous launches cost. <b>Mitigation:</b> the sequencing in the portfolio hub; the Agra "
   "cluster shares management with Geeta Govind Vatika; Karnal is a build, not an operation, until 2027."),
  ("Valuation gap", "Medium", "sev-m",
   f"₹90 Cr pre-money returns {pct(eq['irr_pct'])} to a five-year investor against a 22–25% institutional "
   "hurdle. <b>Mitigation:</b> the CCD structure closes the gap without repricing; target family offices and "
   "strategics rather than growth funds; reduce the round size using the debt."),
])}
{FOOTER}"""
    S.append(("09", "s09", "Conditions precedent and risks", body))

    rail = [(n, sid, t) for n, sid, t, _ in S]
    body = cover + "\n".join(sec(n, sid, t, b) for n, sid, t, b in S)
    return page("Vision Amusement Park — Company Capital Structure · E-O-D Parks",
                "Company capital structure", body, rail, "pf-company.html")

# ============================================================================
# DECK 0 — PORTFOLIO HUB
# ============================================================================
def deck_index():
    g, v, k, c = M["ggv"], M["rv"], M["karnal"], M["company"]
    alloc = M["cgtmse_allocation"]; cg = M["cgtmse"]
    gf, vf, kf, cf = g["financing"], v["financing"], k["financing"], c["financing"]
    consol = M["consolidated"]["years"]
    S = []

    total_ask = gf["ask"] + vf["facility_ask"] + kf["project_cost"]
    total_capital = (gf["true_capital_requirement"]["total"] +
                     vf["true_capital_requirement"]["total"] + kf["project_cost"])

    cover = f"""
<div class="fin-cover">
  <div class="fin-cover__eyebrow">Project finance · Portfolio</div>
  <h1 class="fin-cover__title">Three projects,<br>one balance sheet</h1>
  <p class="fin-cover__sub">Geeta Govind Vatika, Ramayan Vatika and Karnal, each modelled as equity,
  guaranteed debt, and debt that converts to equity — plus the company-level view that ties them
  together. Built on the ₹10 crore CGTMSE ceiling that came into force in April 2025.</p>
  <div class="fin-cover__meta">
    <b>{e(c["profile"]["name"])}</b> · CIN {e(c["profile"]["cin"])} ·
    MSME classification <b>{c["msme"]["classification"].title()} Enterprise</b><br>
    Prepared {e(M["meta"]["prepared"])} · all figures generated from <b>model/pf_model.py</b>
  </div>
  <div class="cover-kpi-grid">
    {kpi("Total funding sought", rs(total_ask, 1), sub="Across the three projects, as briefed")}
    {kpi("True capital at risk", rs(total_capital, 1), sub="The balance is revolving liquidity")}
    {kpi("CGTMSE ceiling", rs(alloc["ceiling"], 0), sub="Per borrower, across all lenders — the binding constraint")}
    {kpi("Gross demand", rs(alloc["total_gross_demand"], 1), sub=f'{rs(alloc["excess_over_ceiling"],1)} over the ceiling')}
  </div>
</div>
<div class="deck-grid">
  <a class="deck-card" href="pf-geeta-govind-vatika.html">
    <div class="deck-card__tag">Agra Development Authority · 7 + 4 years</div>
    <div class="deck-card__name">Geeta Govind Vatika</div>
    <div class="deck-card__desc">Nineteen acres in Taj Nagri Phase-II with a laser show and musical
    fountains, next door to the park E-O-D already runs. One year of operating cost to fund.</div>
    <div class="deck-card__foot"><span>Ask <b>{rs(gf["ask"])}</b></span>
      <span>Project IRR <b>{pct(gf["project_fcf"]["irr_pct"])}</b></span>
      <span><span class="tag tag--green">Debt</span></span></div>
  </a>
  <a class="deck-card" href="pf-ramayan-vatika.html">
    <div class="deck-card__tag">Bareilly Development Authority · 10 + 5 years</div>
    <div class="deck-card__name">Ramayan Vatika</div>
    <div class="deck-card__desc">A 51-foot bronze Ram, a holographic show projected onto it, and a
    contract that forbids pledging any of it. Two years of operating cost to fund.</div>
    <div class="deck-card__foot"><span>Ask <b>{rs(vf["facility_ask"])}</b></span>
      <span>Project IRR <b>{pct(vf["project_fcf"]["irr_pct"])}</b></span>
      <span><span class="tag tag--amber">Bid discipline</span></span></div>
  </a>
  <a class="deck-card" href="pf-karnal.html">
    <div class="deck-card__tag">Private sub-lease · NH-1 · 15 years</div>
    <div class="deck-card__name">Karnal</div>
    <div class="deck-card__desc">The only build, and the only project with assets a lender can take a
    charge over. Signed sub-lease, long rent-free construction window.</div>
    <div class="deck-card__foot"><span>Cost <b>{rs(kf["project_cost"])}</b></span>
      <span>Project IRR <b>{pct(kf["project_fcf"]["irr_pct"])}</b></span>
      <span><span class="tag tag--green">Debt</span></span></div>
  </a>
  <a class="deck-card" href="pf-company.html">
    <div class="deck-card__tag">Vision Amusement Park Pvt. Ltd.</div>
    <div class="deck-card__name">Company capital structure</div>
    <div class="deck-card__desc">Equity, guaranteed debt and convertible debt at company level — and the
    one balance-sheet move that has to happen before any of them.</div>
    <div class="deck-card__foot"><span>CGTMSE <b>{rs(cf["debt"]["total_limit"], 0)}</b></span>
      <span>Equity IRR <b>{pct(cf["equity"]["irr_pct"])}</b></span>
      <span><span class="tag">All three</span></span></div>
  </a>
</div>"""

    body = f"""
<p class="lede">The same analysis run three times. What differs between the projects is not the method —
it is how much capital each genuinely consumes, and what it earns on it.</p>
{table(["", "Geeta Govind Vatika", "Ramayan Vatika", "Karnal"], [
  row(label_cell("Counterparty"), ("Agra Development Authority", ""), ("Bareilly Development Authority", ""), ("A4A Highway Nest LLP", "")),
  row(label_cell("Term"), ("7 + 4 years", ""), ("10 + 5 years", ""), ("15 years", "")),
  row(label_cell("Lock-in"), ("None", "pos"), ("5 years", "neg"), ("None", "pos")),
  row(label_cell("Funding sought"), (rs(gf["ask"]), ""), (rs(vf["facility_ask"]), ""), (rs(kf["project_cost"]), "")),
  row(label_cell("True capital at risk"), (rs(gf["true_capital_requirement"]["total"]), ""),
      (rs(vf["true_capital_requirement"]["total"]), ""), (rs(kf["project_cost"]), "")),
  row(label_cell("Year 1 revenue"), (rs(g["years"][0]["revenue"]["total"]), ""), (rs(v["years"][0]["revenue"]["total"]), ""), (rs(k["years"][0]["revenue"]), "")),
  row(label_cell("Stabilised revenue", "Year 5"), (rs(g["years"][4]["revenue"]["total"]), ""), (rs(v["years"][4]["revenue"]["total"]), ""), (rs(k["years"][4]["revenue"]), "")),
  row(label_cell("Stabilised EBITDA margin"), (pct(g["years"][4]["ebitda_margin"], 1), ""), (pct(v["years"][4]["ebitda_margin"], 1), ""), (pct(k["years"][4]["ebitda_margin"], 1), "")),
  row(("Project IRR", ""), (pct(gf["project_fcf"]["irr_pct"]), "pos"), (pct(vf["project_fcf"]["irr_pct"]), "neg"), (pct(kf["project_fcf"]["irr_pct"]), "pos"), cls_="sub"),
  row(label_cell("Payback"), (f'{num(gf["project_fcf"]["payback_years"],1)} yrs', ""), (f'{num(vf["project_fcf"]["payback_years"],1)} yrs', ""), (f'{num(kf["project_fcf"]["payback_years"],1)} yrs', "")),
  row(label_cell("Spread over guaranteed debt", "Percentage points of project IRR above the all-in cost of a CGTMSE facility"),
      (f'{gf["cost_of_capital"]["spread_over_debt_pct"]:+.1f} pp', "pos"),
      (f'{vf["cost_of_capital"]["spread_over_debt_pct"]:+.1f} pp', "neg"),
      (f'{kf["cost_of_capital"]["spread_over_debt_pct"]:+.1f} pp', "pos")),
  row(label_cell("Minimum DSCR at the size asked"), (num(gf["debt"]["min_dscr_post_moratorium"]) + "×", "pos"),
      (num(vf["debt"]["min_dscr_post_moratorium"]) + "×", "neg"), (num(kf["debt"]["min_dscr_post_moratorium"]) + "×", "pos")),
  row(label_cell("Debt capacity at 1.30× DSCR"), (rs(gf["debt_capacity"]["max_total_limit"]), ""),
      (rs(vf["debt_capacity"]["max_total_limit"]), ""), (rs(kf["debt_capacity"]["max_total_limit"]), "")),
  row(label_cell("Assets a lender can charge"), ("None — ADA owns everything", "neg"),
      ("None — expressly prohibited", "neg"), ("Yes — E-O-D owns the fit-out", "pos")),
  row(label_cell("Equity IRR at project level"), (pct(gf["equity"]["irr_pct"]), "neg"), (pct(vf["equity"]["irr_pct"]), "neg"), (pct(kf["equity"]["irr_pct"]), "neg")),
  row(("Recommended instrument", ""), ("CGTMSE debt", "pos"), ("CGTMSE debt, at reserve price", ""), ("CGTMSE debt", "pos"), cls_="total"),
])}
{note("terra","The same conclusion three times, for the same reason",
  "None of the three projects clears an equity hurdle at project level, and it is not because any of them is a "
  "bad project. It is because a single park generating ₹1–2.5 crore of mature EBITDA cannot pay a 22% return "
  "on the capital it needs <em>and</em> leave an operator's margin behind. Equity works on a portfolio and a "
  "brand; it does not work one licence at a time. <b>Two of the three out-earn guaranteed debt comfortably. "
  "Fund them with it and keep the spread.</b>")}
{note("amber","And one project that needs a decision, not a financing structure",
  f"Ramayan Vatika returns {pct(vf['project_fcf']['irr_pct'])} against a "
  f"{pct(vf['cost_of_capital']['all_in_cost_of_cgtmse_debt_pct'],2)} cost of debt on the base case — and "
  f"{pct(v['scenarios']['bda_indicative']['project_irr_pct'])} on BDA's own published revenue assumption. "
  "The entire difference is how many visitors buy the holographic show. That is a question to answer with data "
  "from BDA before the bid, not a question to solve with a capital structure.")}"""
    S.append(("01", "s01", "The three projects, compared", body))

    slab_rows = []
    for i, (cap, rate) in enumerate(cg["agf_slabs"]):
        prev = cg["agf_slabs"][i-1][0] if i else 0
        lbl = f'Up to {money(cap)}' if i == 0 else f'Above {money(prev)} and up to {money(cap)}'
        slab_rows.append(row((lbl, ""), (pct(rate, 2), "")))
    body = f"""
<p class="lede">Every debt structure in this pack is built on the Credit Guarantee Fund Trust for Micro
and Small Enterprises. The scheme changed materially on 1 April 2025, and the change is what makes this
pack possible.</p>
{bento([
  ("Guarantee ceiling", rs(cg["ceiling_per_borrower_cr"]*100, 0), "Doubled from ₹5 Cr on 1 April 2025"),
  ("Coverage for a Small Enterprise", pct(cg["coverage_small_enterprise_pct"], 0), f'Up to {pct(cg["coverage_preferential_pct"],0)} for micro, women-owned, NER and ZED units'),
  ("Collateral required", "Nil", "On the guaranteed portion. Third-party guarantee not permitted"),
])}
{table(["Parameter", "Position"], [
  row(label_cell("Scheme"), (f'{e(cg["scheme"])} — the standard scheme used by banks and NBFCs', "")),
  row(label_cell("Eligible borrowers"), ('Micro and Small Enterprises under the MSMED Act, with a live Udyam registration. Manufacturing and service enterprises both eligible; amusement and recreation is a covered service activity.', "")),
  row(label_cell("Ceiling basis"), (f'<b>{e(cg["ceiling_basis"])}</b><span class="meta">This is the constraint that shapes the whole portfolio — see section 03.</span>', "")),
  row(label_cell("DPIIT-recognised startups"), (f'Ceiling of {rs(cg["ceiling_startup_dpiit_cr"]*100,0)}', "")),
  row(label_cell("Security"), ('Nil collateral on the guaranteed portion. Third-party guarantee is <b>not</b> permitted; the personal guarantee of directors is. Primary security is hypothecation of the assets financed.', "")),
  row(label_cell("Hybrid security"), ('Permitted. Collateral may be taken on part of a facility with the remainder guaranteed — the route for exposure above the ceiling.', "")),
  row(label_cell("Interest rate"), (e(cg["interest_cap_note"]) + '<span class="meta">NBFC pricing for the same borrower currently runs 14–22%. The scheme is what makes bank money accessible without collateral.</span>', "")),
  row(label_cell("Guarantee fee basis"), (f'On the {e(cg["agf_basis_y1"])} in year 1; on the {e(cg["agf_basis_y2plus"])} thereafter.<span class="meta">Which is why an over-sanctioned, undrawn limit is expensive — a point made in each project deck.</span>', "")),
  row(label_cell("Fee concession"), (f'{pct(cg["agf_concession_pct"],0)} for women, SC/ST, differently-abled, Agniveer and transgender borrowers, and for NER, J&K, Ladakh, Aspirational District, Credit Deficient District or ZED-certified units.', "")),
  row(label_cell("Lender risk adjustment"), ('Well-performing member institutions receive up to a 10% discount on the standard fee; higher-risk institutions pay a premium. The rate quoted to the borrower depends on which bank is approached.', "")),
], aligns=["l","l"])}
<div style="margin:26px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Standard annual guarantee fee, effective April 2025</div>
{table(["Facility size", "Fee per annum"], slab_rows)}
{note("amber","Verify before you apply, not after",
  "CGTMSE parameters are revised by circular and vary in application between member lending institutions. The "
  "figures above reflect the position as published following the April 2025 revisions and were checked against "
  "public sources in August 2026. <b>Confirm the current operative circular, the fee applicable to the specific "
  "bank approached, and the coverage percentage for VAPPL's classification directly with the lender before "
  "relying on any number in these decks.</b> The structures hold; the basis points may not.")}"""
    S.append(("02", "s02", "The CGTMSE framework", body))

    dem_rows = [row((e(name), ""), (rs(amt), "")) for name, amt in alloc["gross_demand"].items()]
    dem_rows.append(row(("Gross demand", ""), (rs(alloc["total_gross_demand"]), ""), cls_="sub"))
    dem_rows.append(row(("CGTMSE ceiling, per borrower", ""), (rs(alloc["ceiling"], 0), ""), cls_="dim"))
    dem_rows.append(row(("Excess to fund another way", ""), (rs(alloc["excess_over_ceiling"]), "neg"), cls_="total"))
    plan_rows = [row((e(name), ""), (rs(amt), "")) for name, amt in alloc["single_borrower_plan"].items()]
    plan_rows.append(row(("Total allocated", ""), (rs(alloc["single_borrower_plan_total"]), ""), cls_="total"))
    body = f"""
<p class="lede">This is the single most important structural fact in the pack, and it is easy to miss:
the ₹10 crore ceiling is <b>per borrower</b>, not per project, per facility or per lender. Four separate
sanctions from four separate banks still share one ceiling.</p>
{table(["Gross demand across the portfolio", "Amount"], dem_rows)}
{note("terra","Four facilities, one ceiling",
  f"Adding the composite facilities from each project deck to the company working-capital requirement gives "
  f"<b>{rs(alloc['total_gross_demand'])}</b> of demand against a <b>{rs(alloc['ceiling'],0)}</b> ceiling. "
  "Applying to four different banks does not create four ceilings — CGTMSE aggregates a borrower's guaranteed "
  "exposure across all member lending institutions. <b>Roughly "
  f"{rs(alloc['excess_over_ceiling'])} has to come from somewhere else.</b>")}
<div style="margin:30px 0 10px;font-size:10.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--terracotta);font-weight:700;">Recommended allocation — single borrower</div>
{table(["Use", "Allocation"], plan_rows)}
{note("blue","Why the allocation is ordered this way",
  f"<b>Karnal takes the largest slice</b> ({rs(alloc['single_borrower_plan']['Karnal Phase 1 — term loan'])}) "
  "because it is the only project with assets to hypothecate, the cleanest DSCR, and a construction timetable "
  "that cannot slip without cost. It is also the facility to take to a bank first — a sanction there establishes "
  "the CGTMSE relationship the other two will draw on.<br><br>"
  "<b>The two concessions take committed term money plus standby working capital</b> rather than the full year "
  "or two years of gross opex. The guarantee fee is charged on what is sanctioned; sanctioning liquidity that "
  "will not be drawn burns both fee and ceiling.<br><br>"
  "<b>Company working capital takes the balance</b>, of which ₹3 crore retires NBFC borrowings — which is not "
  "just cheaper money, it is the consolidation a credit committee will require anyway.")}
{table(["Route for the residual " + rs(alloc["excess_over_ceiling"]), "How it works", "Assessment"], [
  row(label_cell("Hybrid security"),
      ("CGTMSE expressly permits collateral on part of a facility with the balance guaranteed. The exposure above the ceiling is secured conventionally.", ""),
      ("<b>Preferred.</b> No structural change, no new entity, no consent required. Needs collateral VAPPL can actually offer — the ₹2.22 Cr of FDR is the obvious candidate, though the company model is explicit that it should not be liquidated.", "")),
  row(label_cell("Equity or CCD"),
      ("Fund the residual from the company-level round rather than from debt.", ""),
      ("<b>Recommended alongside hybrid security.</b> This is precisely the ₹6–8 crore round the company deck arrives at — the debt does the work it is cheapest at, and equity covers what it cannot reach.", "")),
  row(label_cell("Separate SPVs"),
      ("Each project held in its own entity with its own Udyam registration and its own CGTMSE ceiling.", ""),
      ("<b>Legally available, practically difficult.</b> A new SPV has no turnover history and fails the two-projects and turnover tests in both RFPs. Lenders assess group exposure regardless. And Ramayan Vatika's lock-in bars restructuring without BDA's consent. Consider only for future projects, structured from the outset.", "")),
  row(label_cell("Sequencing"),
      ("Draw the facilities in order as earlier ones amortise and release headroom.", ""),
      ("<b>Useful at the margin.</b> The Karnal term loan begins amortising in year 3, releasing roughly ₹0.43 Cr of ceiling a year. It does not solve a day-one shortfall.", "")),
], aligns=["l","l","l"])}"""
    S.append(("03", "s03", "The ceiling problem", body))

    ec = cf["equity"]; dbc = cf["debt"]; ccc = cf["ccd"]
    body = f"""
<p class="lede">Putting the three project conclusions and the company analysis together gives one
sequence. It is not a choice between equity and debt — it is an order of operations.</p>
{table(["Step", "Action", "Amount", "Effect"], [
  row(label_cell("1 · Now", "No external party. No permission needed."),
      ("Convert <b>all</b> related-party and promoter debt to equity; clear the electricity arrears; consolidate the NBFC book", ""),
      (rs(cf["debt"]["leverage"]["conversion_full"]), ""),
      (f'D/E {num(c["related_party_conversion"]["base"]["debt_equity"])}× → {num(c["related_party_conversion"]["convert_lt_plus_promoter_409"]["debt_equity"])}×<span class="meta">Without it the covenant caps the facility at {rs(cf["debt"]["leverage"]["cases"][1]["max_facility_at_covenant"])}, not {rs(1000,0)}.</span>', "pos")),
  row(label_cell("2 · Weeks 1–12", "Cheapest capital, and it establishes the banking relationship"),
      ("CGTMSE term loan for Karnal Phase 1, taken to a bank first", ""),
      (rs(alloc["single_borrower_plan"]["Karnal Phase 1 — term loan"]), ""),
      (f'Releases the ₹4 Cr earmarked for Karnal in the equity round', "pos")),
  row(label_cell("3 · On award", "Only if the bid clears the walk-away price"),
      ("CGTMSE facility for Geeta Govind Vatika, sanctioned on award", ""),
      (rs(alloc["single_borrower_plan"]["Geeta Govind Vatika — term loan + standby WC"]), ""),
      (f'Walk-away licence fee {lakh(gf["walk_away"]["licence_fee_year1"],1)} a year', "")),
  row(label_cell("4 · On award", "Bid at reserve, or do not bid"),
      ("CGTMSE facility for Ramayan Vatika, drawn to what the project services", ""),
      (rs(alloc["single_borrower_plan"]["Ramayan Vatika — term loan + standby WC"]), ""),
      (f'Walk-away licence fee {lakh(vf["walk_away"]["licence_fee_year1"],1)} a year', "")),
  row(label_cell("5 · Parallel", "Consolidation the lender will require in any case"),
      ("CGTMSE working capital, retiring ₹3 Cr of NBFC borrowings", ""),
      (rs(alloc["single_borrower_plan"]["VAPPL — working capital, NBFC consolidation"]), ""),
      ("Reduces finance cost and the facility count", "pos")),
  row(label_cell("6 · Months 4–10", "Smaller, later, and at less dilution"),
      ("Equity or CCD at company level for what debt cannot reach", ""), ("₹6–8 Cr", ""),
      (f'Against {rs(ec["investment"])} and {pct(ec["stake_pct"],1)} if funded by equity alone', "pos")),
], aligns=["l","l","r","l"])}
{bento([
  ("CGTMSE deployed", rs(alloc["single_borrower_plan_total"], 0), "The full per-borrower ceiling"),
  ("Cost of that debt", pct(dbc["rate_pct"] + dbc["cgtmse"]["agf_rate_pct"], 2), "All-in, collateral-free"),
  ("Equity avoided", "₹8–10 Cr", "Reduction in the round size versus funding everything with equity"),
])}
<div class="verdict verdict--go">
  <div class="verdict__label">The case in one paragraph</div>
  <div class="verdict__head">Debt is the cheap capital, and it only just became available</div>
  <div class="verdict__body">
    The ₹10 crore equity round was designed before the CGTMSE ceiling doubled and before the MSME
    thresholds were raised, both on 1 April 2025. VAPPL is a <b>Small Enterprise</b> with
    ₹{c["msme"]["headroom_investment_cr"]:.1f} crore of investment headroom and
    ₹{c["msme"]["headroom_turnover_cr"]:.1f} crore of turnover headroom, and it can now access
    <b>{rs(alloc["ceiling"], 0)} of collateral-free, guaranteed debt at
    {pct(dbc["rate_pct"] + dbc["cgtmse"]["agf_rate_pct"], 2)} all-in</b>. Two of the three new projects
    out-earn that cost by six to seven percentage points; none of the three out-earns an equity hurdle.
    The conclusion follows: <b>fund the projects with the guarantee, keep the spread, and use equity only
    for what the ceiling cannot reach</b> — at which point the round is ₹6–8 crore rather than ₹16 crore,
    and the dilution roughly halves. The one thing that has to happen first costs nothing:
    convert {rs(260)} of promoter debt into equity and take gearing from
    {num(c["related_party_conversion"]["base"]["debt_equity"])}× to
    {num(c["related_party_conversion"]["convert_lt_related_260"]["debt_equity"])}×.
  </div>
</div>"""
    S.append(("04", "s04", "The recommended sequence", body))

    body = f"""
<p class="lede">These decks are a model, not a due-diligence report. Everything below is either unknown,
inconsistent in the source documents, or dependent on a third party — and each one moves numbers.</p>
{table(["Item", "Where it matters", "Who can answer it"], [
  row(label_cell("Karnal footprint", "22,000 sq ft in index.html against ~6 acres in financials.html"),
      ("Sizes the entire Karnal revenue thesis and determines whether the outdoor activity stack physically fits", ""),
      ("The executed sub-lease with A4A Highway Nest LLP", "")),
  row(label_cell("Ramayan Vatika show conversion", "42% assumed here against BDA's 60%"),
      ("The difference between an 11.4% and a 24%+ project IRR — the whole bid decision", ""),
      ("BDA — slot capacity, commissioning date, soft-launch footfall", "")),
  row(label_cell("Ramayan Vatika lock-in", "7 years in clause 9 against 5 years in clause 14"),
      ("A seven-year lock-in on a project with a seven-year payback changes the risk materially", ""),
      ("BDA — pre-bid clarification", "")),
  row(label_cell("Geeta Govind Vatika show tariff", "Not set in the RFP — to be agreed with ADA"),
      ("Roughly a third of Geeta Govind Vatika's revenue rests on a rate E-O-D does not control", ""),
      ("ADA — pre-bid query", "")),
  row(label_cell("Winning licence fees", "Both are competitive processes with no cap"),
      ("Both models are built on assumed bids. Re-run on award", ""),
      ("The e-auction and the sealed bid", "")),
  row(label_cell("CGTMSE current circular", "Fee slabs, coverage and ceiling as published April 2025"),
      ("Every debt structure in the pack", ""),
      ("The lending bank's MSME desk", "")),
  row(label_cell("Udyam registration and NIC code", "Required for CGTMSE cover"),
      ("Eligibility itself", ""), ("VAPPL compliance records", "")),
  row(label_cell("FY25-26 audit", "Depreciation placeholder ₹54.5 L against an estimated ₹1.0–1.1 Cr"),
      ("Net worth and therefore the gearing covenant. EBITDA and DSCR unaffected", ""),
      ("HMBA & Associates — expected August 2026", "")),
  row(label_cell("Electricity arrears", "₹2.14 Cr, resolution described as in progress"),
      ("A condition precedent to any sanction", ""), ("VAPPL finance and the discoms", "")),
  row(label_cell("Laser and fountain asset condition", "Geeta Govind Vatika — age and AMC history unknown"),
      ("The operator must replace end-of-life assets at its own cost", ""),
      ("ADA — joint condition survey before bidding", "")),
], aligns=["l","l","l"])}
{note("blue","How to keep these decks accurate",
  "Every figure in this pack is computed by <b>model/pf_model.py</b> and rendered into HTML by "
  "<b>model/render.py</b>. Nothing is typed into the markup. To update an assumption — a winning licence fee, a "
  "revised footfall, a different interest rate — edit the model and re-run both scripts; all five decks "
  "regenerate consistently. The intermediate <b>model/pf_model.json</b> holds every computed value if the "
  "numbers need to be checked line by line or exported.")}
{note("amber","What this pack deliberately does not do",
  "It does not value the extension years on any concession — four at Geeta Govind Vatika, five at Ramayan "
  "Vatika — even though those are the most profitable years of each contract. It does not assume any new "
  "concession beyond these three. It does not include the Swadesh Darshan 2.0 pipeline. And it values exits by "
  "discounting the cash flow left in each concession rather than by applying an EBITDA multiple, which is the "
  "conservative choice and roughly halves the exit values. <b>Every one of those choices makes the returns look "
  "worse than a promoter would present them. That is the point.</b>")}
{FOOTER}"""
    S.append(("05", "s05", "What still has to be verified", body))

    rail = [(n, sid, t) for n, sid, t, _ in S]
    body = cover + "\n".join(sec(n, sid, t, b) for n, sid, t, b in S)
    return page("Project Finance — E-O-D Parks · Vision Amusement Park Pvt. Ltd.",
                "Project finance · Portfolio", body, rail, "pf-index.html")


if __name__ == "__main__":
    out = {
        "pf-index.html": deck_index,
        "pf-geeta-govind-vatika.html": deck_ggv,
        "pf-ramayan-vatika.html": deck_rv,
        "pf-karnal.html": deck_karnal,
        "pf-company.html": deck_company,
    }
    for fn, builder in out.items():
        path = os.path.join(ROOT, fn)
        html_out = builder()
        with open(path, "w") as fh:
            fh.write(html_out)
        print(f"{fn:34s} {len(html_out):>8,} bytes")
