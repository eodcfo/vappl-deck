# E-O-D Parks — Investor Brief + Financial Model

Investor materials for **Vision Amusement Park Pvt. Ltd.** (CIN U93000DL2011PTC212814), operator of the **E-O-D Adventure Parks** portfolio across Delhi-NCR and Agra.

Live at: **[eodcfo.github.io/vappl-deck](https://eodcfo.github.io/vappl-deck)**

| File | Purpose |
|---|---|
| `index.html` | 12-chapter investor deck · ~8 min read |
| `financials.html` | Detailed financial model · 11 sections · linked from the deck |
| `pf-index.html` | Project finance pack — portfolio hub, CGTMSE framework, capital plan |
| `pf-geeta-govind-vatika.html` | Geeta Govind Vatika, Agra (ADA) — 1 year of opex as loan/investment |
| `pf-ramayan-vatika.html` | Ramayan Vatika, Bareilly (BDA) — 2 years of opex as loan/investment |
| `pf-karnal.html` | Karnal, NH-1 — ₹4 Cr Phase 1 build-out |
| `pf-company.html` | VAPPL capital structure — equity, CGTMSE debt, debt-to-equity |
| `model/pf_model.py` | The financial model behind all five project-finance decks |
| `model/render.py` | Renders the decks from the model · **edit the model, not the HTML** |

---

## What this is

Self-contained HTML files — no build step, no dependencies, no framework. Pure HTML + embedded CSS + vanilla JS, designed to be read in a browser, shared as a link, or printed to PDF.

The deck makes the case for a ₹10 Cr equity raise at a ₹90 Cr pre-money valuation — the first institutional capital in the company's history. The financial model provides the full supporting detail: audited actuals (FY22–25), provisional FY25-26, three-year projections, balance sheet, cost structure, borrowings, assumptions, and risk register.

The **project finance pack** (`pf-*.html`) sits alongside them: three new projects, each modelled under equity, CGTMSE-guaranteed debt and convertible debt, plus the company-level capital structure. Unlike the two hand-edited files above, those five decks are **generated from a model** — see the section below.

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

## Project finance pack (`pf-*.html`)

Five decks covering the three new projects and the company-level capital structure. Each project is
modelled under all three financing structures the brief asked for — **equity**, **debt under CGTMSE**,
and **debt converted to equity (CCD)** — with the recommendation stated and the arithmetic shown.

| Deck | Ask | Project IRR | Recommendation |
|---|---|---|---|
| Geeta Govind Vatika · ADA · 7+4 yrs | ₹3.35 Cr (mobilisation + 1 yr opex) | 18.7% | CGTMSE composite facility |
| Ramayan Vatika · BDA · 10+5 yrs | ₹4.17 Cr (2 yrs opex) | 11.4% | Bid at reserve; facility drawn to ₹2.81 Cr |
| Karnal · private sub-lease · 15 yrs | ₹4.00 Cr (Phase 1 capex) | 19.5% | CGTMSE term loan — take to a bank first |
| VAPPL company | ₹10 Cr CGTMSE + ₹6–8 Cr equity | — | Convert all ₹4.09 Cr promoter debt, then debt, then equity |

### The four findings that shaped the pack

1. **The CGTMSE ceiling doubled to ₹10 Cr on 1 April 2025**, and the MSME Small Enterprise thresholds
   rose to ₹25 Cr investment / ₹100 Cr turnover on the same date. VAPPL qualifies as a **Small
   Enterprise** with wide headroom. Collateral-free guaranteed debt at ~12.5% all-in is now available
   at a scale that did not exist when the ₹10 Cr equity round was designed.
2. **The ceiling is per borrower, not per project.** Gross demand across the four uses is ₹14.5 Cr
   against a ₹10 Cr ceiling. The hub sets out the allocation and the routes for the ₹4.5 Cr residual.
3. **No project clears an equity hurdle at project level; two clear guaranteed debt comfortably.**
   A single park generating ₹1–2.5 Cr of mature EBITDA cannot pay a 22% return on its capital *and*
   leave an operator's margin. Equity belongs at company level; the projects should be debt-funded.
4. **At VAPPL's current gearing, the company cannot borrow at all.** At 3.04× debt-to-equity, a
   conventional 2.0× covenant supports a new facility of only **₹0.31 Cr**. Converting the ₹2.60 Cr of
   long-term related-party loans lifts that to ₹8.11 Cr; converting **all ₹4.09 Cr** of related-party
   and promoter debt lifts it to ₹12.58 Cr, which is what makes the full ₹10 Cr ceiling reachable. The
   conversion costs no cash and involves no third party. It is the first step in the plan.

Two contractual constraints materially shape the structures: Ramayan Vatika's RFP **prohibits any
mortgage or charge over the asset** (which is why CGTMSE fits) and **bars changes in shareholding
during the lock-in without BDA's written approval** (which gates both the equity and CCD routes).

### Regenerating the decks

Every figure in the five decks is computed, not typed. Nothing is hard-coded into the markup.

```bash
python3 model/pf_model.py    # writes model/pf_model.json + prints a summary
python3 model/render.py      # regenerates all five pf-*.html files
```

To change an assumption — a winning licence fee, footfall, an interest rate — edit `model/pf_model.py`
and re-run both. `model/pf_model.json` holds every computed value for line-by-line checking or export.

**Verify before relying on the CGTMSE numbers.** Scheme parameters are revised by circular and vary
between member lending institutions. The fee slabs, coverage percentages and ceiling reflect the
position published after the April 2025 revisions, checked against public sources in August 2026.
Confirm the current operative circular with the lender before use.

---

## Design system

All seven HTML files share the same design language:

- **Typography:** Clash Display (display numbers + titles) · DM Sans (body, UI, tables) · Fraunces italic (pull quotes only)
- **Palette:** White canvas `#FFFFFF` · blue `#2B66EA` · terracotta `#C8553D` · green `#10B981` · ink `#0A1426`
- **Layout:** Sticky left rail navigation · mobile-responsive · print-ready
- **`index.html` extras:** Scroll progress bar · chapter nav · bento grid · TAM funnel visual · competitive matrix
- **`financials.html` extras:** Colour-coded table rows (audited/provisional/projection) · risk severity badges · scenario cards · deployment timeline · intersection-observer rail highlighting

---

## Development

`index.html` and `financials.html` have no build process — edit them directly. The five `pf-*.html`
decks are **generated**; edit `model/pf_model.py` (assumptions and calculations) or `model/render.py`
(prose and layout) and re-run both scripts. Changes made directly to a `pf-*.html` file will be
overwritten on the next render.

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
