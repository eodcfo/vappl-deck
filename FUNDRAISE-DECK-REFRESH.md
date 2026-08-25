# Fundraise deck — Subhash Park re-basing

**Applied 25 August 2026.** `index.html` and `financials.html` had been frozen at the version submitted
to Almonds in May 2026. They were re-based at the CFO's instruction after Subhash Park's FY26-27
position overtook what the model carried. The May 2026 version is preserved in git at commit
`716443a` and can be recovered with `git show 716443a:financials.html`.

## What changed

Subhash Park booked **₹27 lakh in FY26-27 to date** — five months, 1 April to end August 2026, before
the season — against ₹0.40–0.60 Cr carried for the full year.

| ESP · Subhash Park (₹ Cr) | FY25-26 | FY26-27 | FY27-28 | FY28-29 |
|---|---|---|---|---|
| As published, May 2026 | 0.14 | ~0.50 | ~1.00 | ~1.50–2.00 |
| Re-based | 0.14 | **~1.00** | **~1.50–2.00** | **~2.00–2.50** |

The outer years are shifted a year left on the published curve's own shape, not scaled up — if FY26-27
lands where FY27-28 was, the whole curve moves rather than steepening.

| Consolidated (₹ Cr) | FY26-27 | FY27-28 | FY28-29 |
|---|---|---|---|
| As published | 23–25 | 31–35 | 41–46 |
| Re-based | **24–26** | **32–36** | **42–46** |

| At the unchanged ₹90 Cr pre-money | FY26-27 | FY27-28 | FY28-29 |
|---|---|---|---|
| As published | 3.8× | 2.7× | 2.1× |
| Re-based | **3.6×** | **2.6×** | **2.0×** |

Flowed through everywhere the figures appear: the cover KPI, the metrics dashboard, both revenue
tables, the 3-year projections, the deployment bridge, the comparables matrix, the timeline, the
scenario block, and the revenue chart — whose projection band, dashed line and label shift by one
crore on the y-mapping the SVG already documents.

## What was deliberately left alone

**EBITDA, EBITDA margin, PAT and the ₹90 Cr pre-money are unchanged.** Subhash Park is about 2% of
consolidated revenue. The uplift is worth ₹0.17–0.25 Cr of EBITDA at any plausible incremental margin,
which sits inside the published ₹5–6 Cr range for FY26-27. Restating profitability or valuation on one
small park would imply a precision the evidence does not carry, and a reader who checked would find
the extra EBITDA unsupported.

A dated revision note now sits at the head of the Data Sources section recording the previous figures,
so anyone holding the May 2026 version can reconcile the two.

## Still open

- **The YoY growth row** is now computed off the preceding year's mid-point. The published row could
  not be reproduced from any single consistent basis, so the method was made explicit rather than
  guessed at. Worth a glance before the deck goes out again.
- **The ₹27 lakh is management-reported**, not audited or reviewed. It is labelled as such in the
  source list.
- **Mobile layout**: `index.html` overflows horizontally by 219px at 390px width, in the comparables
  matrix. Pre-existing — measured identical on the May 2026 version — and not addressed here.
- **The other parks were not revisited.** EMV, EAC, DME and Karnal carry their May 2026 projections. If
  any of those are also running ahead, the same exercise applies and the group numbers would move
  further than this revision does.
