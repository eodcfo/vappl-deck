# E-O-D Parks — Investor Brief

A single-file interactive investor deck for **Vision Amusement Park Pvt. Ltd.** (CIN U93000DL2011PTC212814), operator of the **E-O-D Adventure Parks** portfolio across Delhi-NCR and Agra.

Live at: **[eodcfo.github.io/vappl-deck](https://eodcfo.github.io/vappl-deck)**

---

## What this is

A self-contained HTML investor brief — no build step, no dependencies, no framework. One file (`index.html`) with embedded CSS and vanilla JS, designed to be read in a browser, shared as a link, or printed to PDF.

The deck makes the case for a ₹10 Cr equity raise at a ₹90 Cr pre-money valuation — the first institutional capital in the company's history.

---

## The business

E-O-D (Every Other Day) operates neighbourhood adventure parks on government-concession land across North India. The thesis: India built destination parks for once-a-year occasions. E-O-D built the park you go to every other Saturday.

**Current portfolio — FY25-26:**

| Park | Location | Model | Status |
|---|---|---|---|
| EMV | Mayur Vihar, Delhi | Urban destination | Mature · ₹14.56 Cr revenue |
| EAC | Agra Chaupati, Agra | Urban destination | Phase 1 · profitable in first 6 months |
| DME | Delhi–Meerut Expressway | Highway stopover | Year 1 · indoor-only |
| ESP | Subhash Park, Agra | Government-concession IP | Zero capex · profitable from day one |

**FY25-26 consolidated:** ₹16.29 Cr revenue · +27% YoY · all-time high.  
**EMV mature-year benchmark:** 32.5% net margin.  
**Long-term debt:** ₹0. Self-funded from operations.

---

## What the raise funds

| Deployment | Amount | Timeline |
|---|---|---|
| Karnal · Phase 1 build-out (NH-1, signed) | ₹4 Cr | 12 months |
| DME · outdoor expansion (Go Kart, Zipline, Obstacle Course) | ₹1.5 Cr | 6 months |
| EAC · Phase 2 activities (combo ₹200 → ₹400) | ₹1.5 Cr | 9 months |
| ESP · IP activation (events, FOFO stores) | ₹0.5 Cr | 6 months |
| Working capital | ₹2.5 Cr | Immediate |

---

## Deck structure

The brief is organised across 12 chapters, readable in approximately eight minutes:

1. **Cover** — Traction snapshot bento · hero image placeholder
2. **The Opportunity** — Gap in India's recreation market · competitive positioning matrix
3. **The Market** — TAM/SAM/SOM funnel (₹11,500 Cr → ₹2,100 Cr → ₹200 Cr)
4. **The Answer** — The ₹299 combo ticket pivot and near-zero CAC model
5. **The Journey** — Timeline from 2015 to FY26-27 target
6. **Who We Serve** — 3,134-response survey · two park archetypes · park image placeholders
7. **How We Make Money** — Unit economics bento · six revenue streams · FY26-27 EMV mix
8. **Three Years of Numbers** — Revenue, margins, balance sheet (zero long-term debt)
9. **The Moat** — Five structural barriers · government concession risk mitigation box
10. **Growth Pipeline** — Horizon 1 (four parks) + Horizon 2 (Karnal, SD 2.0, pipeline)
11. **The Team** — Six people who were inside E-O-D through every crisis
12. **The Ask** — ₹10 Cr · 10% · ₹90 Cr pre-money · listed comps · 3-year financial model

---

## Design system

- **Typography:** Clash Display (display numbers + chapter titles) · DM Sans (body, UI, section heads) · Fraunces italic (testimonials and closing lines only)
- **Palette:** White canvas `#FFFFFF` · electric green `#10B981` · terracotta `#C8553D` · true black `#0A0A0A` · blue `#2B66EA`
- **Layout:** Sticky left rail with chapter navigation · scroll progress bar · mobile-responsive · print-ready (A4)
- **Components:** Bento grid · TAM/SAM/SOM funnel visual · competitive positioning matrix · risk mitigation checklist · image placeholder system with upload specs

---

## Development

No build process. Edit `index.html` directly.

```bash
# View locally
open index.html

# Or serve over HTTP
python3 -m http.server 8080
```

Deployed via GitHub Pages from the `main` branch. To update the live deck, commit changes to `main` and push — Pages rebuilds automatically within ~2 minutes.
