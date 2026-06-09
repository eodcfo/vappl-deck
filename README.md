# E-O-D Parks — Investor Brief + Financial Model

Investor materials for **Vision Amusement Park Pvt. Ltd.** (CIN U93000DL2011PTC212814), operator of the **E-O-D Adventure Parks** portfolio across Delhi-NCR and Agra.

Live at: **[eodcfo.github.io/vappl-deck](https://eodcfo.github.io/vappl-deck)**

| File | Purpose |
|---|---|
| `index.html` | 12-chapter investor deck · ~8 min read |
| `financials.html` | Detailed financial model · 11 sections · linked from the deck |

---

## What this is

Two self-contained HTML files — no build step, no dependencies, no framework. Pure HTML + embedded CSS + vanilla JS, designed to be read in a browser, shared as a link, or printed to PDF.

The deck makes the case for a ₹10 Cr equity raise at a ₹90 Cr pre-money valuation — the first institutional capital in the company's history. The financial model provides the full supporting detail: audited actuals (FY22–25), provisional FY25-26, three-year projections, balance sheet, cost structure, borrowings, assumptions, and risk register.

---

## The business

E-O-D (Every Other Day) operates neighbourhood adventure parks across North India — three on government-concession land (EMV, EAC, ESP) and one on a private highway sub-lease (DME). The thesis: India built destination parks for once-a-year occasions. E-O-D built the park you go to every other Saturday.

**Current portfolio — FY25-26:**

| Park | Location | Model | Status |
|---|---|---|---|
| EMV | Mayur Vihar, Delhi | Urban destination | Mature · ₹14.56 Cr revenue |
| EAC | Agra Chaupati, Agra | Urban destination | Phase 1 · profitable in first 6 months · ₹400 from May 22 |
| DME | Delhi–Meerut Expressway | Highway stopover | Year 1 · indoor-only · outdoor raise-funded |
| ESP | Subhash Park, Agra | Government-concession IP | Zero capex · profitable from day one |

**FY25-26 consolidated:** ₹16.29 Cr revenue · +27% YoY · all-time high.  
**EMV mature-year benchmark:** 32.5% net margin.  
**EAC first-season margin:** 30.7% at ₹200 combo in 6 months.

---

## What the raise funds

| Deployment | Amount | Timeline |
|---|---|---|
| Karnal · Phase 1 build-out (NH-1, signed) | ₹4 Cr | 12 months |
| DME · outdoor expansion (Go Kart, Zipline, Obstacle Course) | ₹1.5 Cr | 6 months |
| EAC · Phase 2 activities | ₹1.5 Cr | 9 months |
| ESP · IP activation (events, FOFO stores) | ₹0.5 Cr | 6 months |
| Working capital | ₹2.5 Cr | Immediate |

---

## Deck structure (`index.html`)

The brief is organised across 12 chapters, readable in approximately eight minutes:

1. **Cover** — Traction snapshot bento · hero image placeholder
2. **The Opportunity** — Gap in India's recreation market · competitive positioning matrix
3. **The Market** — TAM/SAM/SOM funnel (₹11,500 Cr → ₹2,100 Cr → ₹200 Cr)
4. **The Answer** — The ₹299 combo ticket pivot and near-zero CAC model
5. **The Journey** — Timeline from 2015 to FY26-27 target
6. **Who We Serve** — 3,134-response survey · two park archetypes · park image placeholders
7. **How We Make Money** — Unit economics bento · six revenue streams · FY26-27 EMV mix
8. **Three Years of Numbers** — Revenue, margins, balance sheet snapshot
9. **The Moat** — Five structural barriers · government concession risk mitigation box
10. **Growth Pipeline** — Horizon 1 (four parks) + Horizon 2 (Karnal, SD 2.0, pipeline)
11. **The Team** — Six people who were inside E-O-D through every crisis
12. **The Ask** — ₹10 Cr · 10% · ₹90 Cr pre-money · listed comps · 3-year model snippet · link to detailed financial model

---

## Financial model structure (`financials.html`)

A standalone 11-section model linked from Chapter 12 of the deck. All figures sourced from audited financials (FY22–25), provisional P&L from HMBA & Associates (11 May 2026), and management accounts. Edit this file directly to update numbers, assumptions, or projections.

| Section | Contents |
|---|---|
| 01 · Key Metrics Dashboard | Revenue, EBITDA, PAT, net worth, borrowings, parks — FY22-23 to FY28-29 |
| 02 · Historical P&L | Full consolidated income statement with year-on-year commentary |
| 03 · Park-by-Park | Revenue by park FY23–29 · FY25-26 park-level profit/loss actuals |
| 04 · 3-Year Projections | Revenue, EBITDA, PAT by park and consolidated · valuation reference |
| 05 · Balance Sheet | Equity, borrowings, assets, key ratios — FY22-23 to FY25-26 |
| 06 · Cost Structure | Every cost line with FY26 detail + FY26 capex additions breakdown |
| 07 · Borrowings Detail | All 13 NBFC/bank facilities + related-party LT loans |
| 08 · Fundraise Timeline | Deployment milestones with dates + use of funds table |
| 09 · Assumptions | Macro, per-park (EMV/EAC/DME/Karnal), capital structure, valuation |
| 10 · Risk & Sensitivity | 8 risks with severity + 3-scenario sensitivity (downside/base/upside) |
| 11 · Data Sources | Audit trail, source descriptions, 6 key caveats |

**Key caveats tracked in the model:**
- FY25-26 depreciation placeholder ₹54.5L → est. ₹1.0–1.1 Cr on audit (August 2026). EBITDA unaffected; PAT will change.
- All DME outdoor + Karnal projections are raise-dependent. EAC ₹400 is NOT — already live 22 May 2026.
- Note 5/6 label swap on FY26 provisional BS corrected throughout (ST = ₹5.26 Cr, LT = ₹2.60 Cr).

---

## Design system

Both files share the same design language:

- **Typography:** Clash Display (display numbers + titles) · DM Sans (body, UI, tables) · Fraunces italic (pull quotes only)
- **Palette:** White canvas `#FFFFFF` · blue `#2B66EA` · terracotta `#C8553D` · green `#10B981` · ink `#0A1426`
- **Layout:** Sticky left rail navigation · mobile-responsive · print-ready
- **`index.html` extras:** Scroll progress bar · chapter nav · bento grid · TAM funnel visual · competitive matrix
- **`financials.html` extras:** Colour-coded table rows (audited/provisional/projection) · risk severity badges · scenario cards · deployment timeline · intersection-observer rail highlighting

---

## Development

No build process. Edit either HTML file directly.

```bash
# View locally
open index.html
open financials.html

# Or serve over HTTP (recommended — preserves relative links between files)
python3 -m http.server 8080
# then visit http://localhost:8080
```

Deployed via GitHub Pages from the `main` branch. To update the live site, commit changes to `main` and push — Pages rebuilds automatically within ~2 minutes.

> **Workflow:** develop on a feature branch, open a PR into `main`, and merge to publish.
