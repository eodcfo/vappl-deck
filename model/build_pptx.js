/**
 * Builds the PowerPoint versions of the project finance pack.
 *
 *   node model/build_pptx.js        -> writes pptx/*.pptx
 *
 * Every figure is read from model/pf_model.json, the same source the HTML decks
 * render from. Edit model/pf_model.py and re-run both generators; never edit the
 * .pptx by hand.
 */
const pptxgen = require("pptxgenjs");
const fs = require("fs"), path = require("path");
const L = require("./pptx_lib.js");
const { C, cr, crN, lk, pc, pp, xx, money } = L;

const ROOT = path.dirname(__dirname);
const M = JSON.parse(fs.readFileSync(path.join(ROOT, "model", "pf_model.json"), "utf8"));
const OUT = path.join(ROOT, "pptx");
fs.mkdirSync(OUT, { recursive: true });

let DECK = "";
const newDeck = (title, subject) => {
  DECK = title; SLIDE = 0;
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE";
  p.author = "Vision Amusement Park Pvt. Ltd.";
  p.company = "E-O-D Parks";
  p.title = title;
  p.subject = subject;
  return p;
};
let SLIDE = 0;
const slide = p => { SLIDE += 1; L.mark(DECK, SLIDE); return p.addSlide(); };
const rev = y => typeof y.revenue === "object" ? y.revenue.total : y.revenue;

/* ============================ shared project sections ==================== */

function sectionProjection(p, f, yrs, name, note, num) {
  const s = slide(p);
  let y = L.head(s, num || "05", "Projection", note);
  L.chart(p ? s : s, p, y, "bar", [
    { name: "Revenue", labels: yrs.map(v => `Yr ${v.year}`), values: yrs.map(v => +crN(rev(v))) },
    { name: "EBITDA",  labels: yrs.map(v => `Yr ${v.year}`), values: yrs.map(v => +crN(v.ebitda)) },
  ], { h: 2.95, axisTitle: "₹ crore", colors: [C.blue, C.green] });
  const first = yrs.findIndex(v => v.ebitda > 0) + 1;
  L.stats(s, 5.42, [
    { label: "EBITDA breakeven", value: `Year ${first}`, small: true,
      sub: `After ${cr(yrs.slice(0, first - 1).reduce((a, v) => a - v.ebitda, 0))} of cumulative operating deficit` },
    { label: "Margin at maturity", value: pc(yrs[yrs.length - 1].ebitda_margin),
      sub: `Final year of the modelled term` },
    { label: "Cumulative EBITDA", value: cr(yrs.reduce((a, v) => a + v.ebitda, 0)),
      sub: "Across the modelled term" },
  ], { h: 1.24 });
  L.foot(s, name);
  return s;
}

function sectionReturns(p, f, name, extra, num) {
  const s = slide(p);
  const fc = f.project_fcf, coc = f.cost_of_capital;
  let y = L.head(s, num || "06", "Project returns",
    `Unlevered free cash flow to the project. Capital deployed is the true project cost — the revolving opex facility is financing, not project cost, so it is excluded here.`);
  const d = fc.detail;
  y = L.chart(s, p, y, "bar", [
    { name: "Free cash flow", labels: ["Capital", ...d.map(v => `Yr ${v.year}`)],
      values: [ -(+crN(fc.t0)), ...d.map(v => +crN(v.fcf)) ] },
  ], { h: 2.40, axisTitle: "₹ crore", colors: [C.blue], labelPos: "outEnd" });
  y = L.stats(s, y + 0.05, [
    { label: "Project IRR", value: pc(fc.irr_pct),
      color: coc.clears_debt ? C.green : C.terra,
      sub: "Unlevered, no extension value" },
    { label: "Payback", value: fc.payback_years ? `${fc.payback_years.toFixed(1)} yrs` : "Beyond term",
      sub: "From first deployment" },
    { label: "All-in cost of CGTMSE debt", value: pc(coc.all_in_cost_of_cgtmse_debt_pct, 2),
      sub: `Interest plus guarantee fee` },
    { label: "Spread over debt", value: pp(coc.spread_over_debt_pct),
      color: coc.clears_debt ? C.green : C.terra,
      sub: extra || "Percentage points of project IRR above the cost of guaranteed debt" },
  ], { h: 1.32 });
  L.foot(s, name);
  return s;
}

function sectionScenarios(p, scen, name, lede, noteKind, noteHead, noteBody, num) {
  const s = slide(p);
  const order = ["downside", "base", "upside", "bda_indicative"].filter(k => scen[k]);
  const nm = { downside: "Downside", base: "Base case", upside: "Upside",
               bda_indicative: "BDA's own case" };
  let y = L.head(s, num || "07", "Scenarios", lede);
  y = L.chart(s, p, y, "bar", [
    { name: "Project IRR", labels: order.map(k => nm[k]),
      values: order.map(k => scen[k].project_irr_pct == null ? 0
                             : +scen[k].project_irr_pct.toFixed(1)) },
  ], { h: 2.15, axisTitle: "Project IRR, %", fmt: '0.0"%"',
       colors: order.map(k => k === "base" ? C.blue
                             : (scen[k].project_irr_pct || 0) < 0 ? C.terra : C.green) });
  L.table(s, y + 0.05, ["", ...order.map(k => nm[k])], [
    { cells: ["Year 1 EBITDA", ...order.map(k => cr(scen[k].ebitda_year1))] },
    { cells: ["Stabilised revenue", ...order.map(k => cr(scen[k].revenue_stabilised))] },
    { cells: ["Stabilised EBITDA margin", ...order.map(k => pc(scen[k].ebitda_margin_stabilised))] },
    { cells: ["Payback", ...order.map(k => scen[k].payback_years
        ? `${scen[k].payback_years.toFixed(1)} yrs` : "Not within term")], emphasis: "total" },
  ], { colW: [3.6, ...Array(order.length).fill((L.W - 2 * L.M - 3.6) / order.length)], rowH: 0.32 });
  if (noteHead) L.verdict(s, y + 0.16, noteKind, noteHead, noteBody);
  L.foot(s, name);
  return s;
}

function sectionDebt(p, f, name, lede, notes, num) {
  const db = f.debt, dc = f.debt_capacity;
  const s = slide(p);
  let y = L.head(s, num || "09", "Option B · Debt under CGTMSE", lede);
  const sch = db.schedule;
  y = L.chart(s, p, y, "bar", [
    { name: "Debt service", labels: sch.map(r => `Yr ${r.year}`), values: sch.map(r => +crN(r.debt_service)) },
    { name: "Cash available (EBITDA)", labels: sch.map(r => `Yr ${r.year}`), values: sch.map(r => +crN(r.cfads)) },
  ], { h: 2.05, axisTitle: "₹ crore", colors: [C.terra, C.blue] });
  y = L.stats(s, y + 0.02, [
    { label: "Total facility", value: cr(db.total_limit),
      sub: `Term loan ${cr(db.term_loan)} + working capital ${cr(db.wc_limit)}` },
    { label: "All-in rate", value: `${pc(db.rate_pct, 2)} + ${pc(db.cgtmse.agf_rate_pct, 2)}`,
      small: true, sub: "Interest plus annual guarantee fee" },
    { label: "Minimum DSCR", value: xx(db.min_dscr_post_moratorium),
      color: db.bankable ? C.green : C.terra,
      sub: `After the ${db.tl_moratorium_years}-year moratorium. Banks underwrite to 1.30×` },
    { label: "Debt capacity", value: cr(dc.max_total_limit),
      sub: `Most the project services at a ${dc.target_dscr}× floor` },
  ], { h: 1.26 });
  if (notes) L.verdict(s, y + 0.06, notes.kind, notes.head, notes.body);
  L.foot(s, name);
  return s;
}

function sectionCompare(p, f, name, rows, rec) {
  const s = slide(p);
  const eq = f.equity, db = f.debt, cc = f.ccd;
  let y = L.head(s, rec.num, "Which option, and why");
  y = L.optionCards(s, y, [
    { tag: "Option A", name: "Equity", big: pc(eq.irr_pct), cap: "Investor IRR",
      bigColor: eq.irr_pct >= 18 ? C.green : C.terra, rows: [
        ["Capital in", cr(eq.investment)],
        ["Stake offered", pc(eq.stake_pct, 0)],
        ["Money multiple", `${eq.money_multiple.toFixed(2)}×`],
        ["Stake for a 22% IRR", pc(eq.stake_for_22pct, 0)],
      ] },
    { tag: "Option B", name: "Debt · CGTMSE", big: xx(db.min_dscr_post_moratorium),
      cap: "Minimum DSCR · this facility", pick: true,
      bigColor: db.bankable ? C.green : C.terra, rows: [
        ["Facility", cr(db.total_limit)],
        ["Term loan / WC", `${crN(db.term_loan)} / ${crN(db.wc_limit)}`],
        ["All-in rate", `${pc(db.rate_pct, 2)} + fee`],
        ["Total finance cost", cr(db.total_finance_cost)],
      ] },
    { tag: "Option C", name: "Debt → equity (CCD)", big: pc(cc.irr_pct), cap: "Investor IRR",
      bigColor: cc.irr_pct >= 18 ? C.green : C.terra, rows: [
        ["Principal", cr(cc.principal)],
        ["Coupon to conversion", `${pc(cc.coupon_pct, 1)} · yr ${cc.conversion_year}`],
        ["Stake on conversion", pc(cc.conversion_stake_pct, 0)],
        ["Money multiple", `${cc.money_multiple.toFixed(2)}×`],
      ] },
  ], 3.16);
  L.verdict(s, y, rec.kind, rec.head, rec.body, 1.72);
  L.foot(s, name);
  return s;
}

/* ================================ 1 · GGV =============================== */
function buildGGV() {
  const g = M.ggv, f = g.financing, r = g.rfp, db = f.debt, yrs = g.years;
  const cap = f.true_capital_requirement, mob = g.mobilisation, wa = f.walk_away;
  const p = newDeck("Geeta Govind Vatika — Project Finance",
                    "ADA licence-fee concession, 7+4 years");
  const NAME = "Geeta Govind Vatika · Agra Development Authority · Project finance";

  L.cover(slide(p), {
    eyebrow: "Project finance · 01 of 04", title: "Geeta Govind\nVatika",
    sub: "Nineteen acres in Taj Nagri Phase-II, next door to the park E-O-D already runs. Seven years of operating rights, no land to buy, no structures to build. One crore to open the doors — and from there it pays for itself at the gate.",
    meta: "Agra Development Authority · Licence-fee model · 7 + 4 years · 19 acres\nReserve licence fee ₹2.5 lakh per month · forward e-auction · 5% annual escalation",
    stats: [
      { label: "Funding ask", value: cr(f.ask), sub: "Mobilisation only — operating cost met from collections" },
      { label: "Year 1 EBITDA", value: cr(yrs[0].ebitda), sub: "Positive from the opening season" },
      { label: "Project IRR", value: pc(f.project_fcf.irr_pct), sub: `Payback ${f.project_fcf.payback_years.toFixed(1)} years` },
      { label: "Year 7 EBITDA", value: cr(yrs[6].ebitda), sub: `${pc(yrs[6].ebitda_margin)} margin` },
    ],
  });

  // 01 the project
  let s = slide(p);
  let y = L.head(s, "01", "The project",
    "Nineteen acres in Taj Nagri Phase-II, built and fitted out by ADA, now looking for an operator. The asset is already there — musical fountains, a 40-minute Krishna Leela laser show, an open-air amphitheatre, a waterbody, eight kiosks and a Tulsi forest. The operator pays a monthly licence fee and keeps what it collects at the gate.");
  y = L.table(s, y, ["Term", "What the RFP says"], [
    { cells: ["Authority", r.authority] },
    { cells: ["Contract period", r.term] },
    { cells: ["Selection", "Technical evaluation, then forward e-auction on the licence fee"] },
    { cells: ["Reserve licence fee", `${lk(r.reserve_licence_fee_month_lakh)} per month + GST · ${lk(r.reserve_licence_fee_year_lakh, 0)} a year`] },
    { cells: ["Escalation", `${pc(r.escalation_pct, 0)} a year on the preceding year`] },
    { cells: ["Payment terms", "First 6 months in advance within 7 days of the work order; then half-yearly in advance"] },
    { cells: ["Security deposit", r.security_deposit_basis] },
    { cells: ["Gate tariff", `₹${r.entry_tariff_inr} entry. Fountain and laser show at rates approved by ADA`] },
    { cells: ["Asset position", r.assets], emphasis: "total" },
  ], { colW: [3.0, L.W - 2 * L.M - 3.0], rowH: 0.36, fontSize: 11 });
  L.verdict(s, y, "note", "What the Agra cluster does to the commercials",
    "The site adjoins Agra Chaupati and is a short drive from Subhash Park, both already operating. Overhead is charged at 5% of revenue rather than a standalone rate; food and beverage is supplied from the Chaupati kitchens, so the site needs counters rather than a built kitchen and runs at 44% cost of goods instead of 52%; and marketing reaches an audience already visiting the cluster.", 1.16);
  L.foot(s, NAME);

  // 02 the ask
  s = slide(p);
  y = L.head(s, "02", "What the money is for",
    "The brief was one year of opex as loan or investment. That is the right facility size — but being precise about what the money does changes which instrument fits.");
  y = L.stats(s, y, [
    { label: "Facility as briefed", value: cr(f.ask), sub: "Mobilisation plus 12 months of operating cost" },
    { label: "True capital at risk", value: cr(cap.total), tint: "FBF1EE", line: C.terra,
      sub: "Mobilisation plus the year-1 operating deficit" },
    { label: "Revolving liquidity", value: cr(f.ask - cap.total),
      sub: "Drawn, spent, and recovered from collections" },
  ], { h: 1.26 });
  y = L.table(s, y, ["Total requirement", "Amount"], [
    { cells: ["Mobilisation capex — activity equipment, kiosk fit-out, ticketing, signage", lk(mob.capex)] },
    { cells: ["Security deposit (3 months, refundable), advance licence fee (6 months), EMD and tender fee",
              lk(mob.security_deposit + mob.advance_licence_fee_6m + mob.emd + mob.tender_fee)] },
    { cells: ["Sub-total — mobilisation", lk(mob.total)], emphasis: "sub" },
    { cells: ["Year 1 operating expenditure", lk(g.year1_opex)] },
    { cells: ["Facility requested", lk(f.ask)], emphasis: "total" },
  ], { colW: [10.0, L.W - 2 * L.M - 10.0], rowH: 0.34 });
  L.verdict(s, y, "stop", "A liquidity requirement, not a capital requirement",
    `Of the ${cr(f.ask)} asked for, only ${cr(cap.total)} is capital the project consumes and does not return. The rest is working capital — spent on wages and electricity, recovered at the gate. Equity does not come back; a revolving limit does.`);
  L.foot(s, NAME);

  // 03 revenue
  s = slide(p);
  y = L.head(s, "03", "Revenue model",
    "Six streams, built bottom-up from footfall and capture rates. All figures net of GST.");
  const K = [["entry", "Gate entry"], ["show", "Fountain & laser show"],
             ["fnb", "Food and beverage"], ["activities", "E-O-D activity layer"]];
  y = L.chart(s, p, y, "barStacked", [
    ...K.map(([k, n]) => ({ name: n, labels: yrs.map(v => `Yr ${v.year}`),
                            values: yrs.map(v => +crN(v.revenue[k])) })),
    { name: "Parking, events and shoots", labels: yrs.map(v => `Yr ${v.year}`),
      values: yrs.map(v => +crN(v.revenue.parking + v.revenue.events)) },
  ], { h: 3.05, axisTitle: "₹ crore", labelPos: "ctr",
       colors: [C.blue, C.terra, C.green, C.amber, "8A93A6"] });
  L.stats(s, y + 0.05, [
    { label: "Year 1 footfall", value: `${yrs[0].revenue.footfall_lakh.toFixed(2)} L`, sub: "About 850 visits a day" },
    { label: "Year 7 footfall", value: `${yrs[6].revenue.footfall_lakh.toFixed(2)} L`, sub: "About 1,575 visits a day" },
    { label: "Show conversion", value: "24% → 31%", small: true, sub: "Share buying the fountain and laser ticket" },
    { label: "Gate tariff", value: "₹20", sub: "Fixed by ADA — no escalation modelled" },
  ], { h: 1.20 });
  L.foot(s, NAME);

  // 04 cost
  s = slide(p);
  y = L.head(s, "04", "Cost model",
    "Payroll and the licence fee are the two structural lines. Everything else scales with footfall, revenue or inflation.");
  const CK = [["licence_fee", "Licence fee to ADA"], ["manpower", "Payroll"],
              ["electricity", "Electricity"], ["show_amc", "Show AMC and spares"],
              ["water_horticulture", "Water and horticulture"], ["fnb_cogs", "F&B cost of goods"],
              ["marketing", "Marketing"], ["corporate_overhead", "Corporate overhead"]];
  y = L.table(s, y, ["₹ crore", ...yrs.map(v => `Yr ${v.year}`)],
    [...CK.map(([k, n]) => ({ cells: [n, ...yrs.map(v => crN(v.opex[k]))] })),
     { cells: ["Other operating cost", ...yrs.map(v => crN(v.opex.total -
        CK.reduce((a, [k]) => a + v.opex[k], 0)))] },
     { cells: ["Total operating cost", ...yrs.map(v => crN(v.opex.total))], emphasis: "total" },
     { cells: ["Revenue / EBITDA margin", ...yrs.map(v => `${crN(rev(v))} · ${pc(v.ebitda_margin, 0)}`)], emphasis: "sub" }],
    { colW: [3.5, ...Array(7).fill((L.W - 2 * L.M - 3.5) / 7)], rowH: 0.29, fontSize: 10.5 });
  L.verdict(s, y, "caution", "What is not in this model",
    "The CCTV integration, ex-servicemen at entry, police verification and six-monthly audits are costed above. What is not costed is replacing a laser or fountain asset that reaches end of life mid-term — that burden sits with the agency. Get the AMC history before bidding.");
  L.foot(s, NAME);

  sectionProjection(p, f, yrs, NAME,
    "Year 1 loses money — a 15-day mobilisation window, a full-year licence fee from day one, and a park that has never opened to the public.");
  sectionReturns(p, f, NAME);
  sectionScenarios(p, g.scenarios, NAME,
    "Three drivers move this project: footfall, show conversion, and the licence fee you bid. The downside moves all three against you at once.",
    "stop", "The downside is a bad bid, not a bad year",
    `The model solves the break-even licence fee at ${lk(wa.licence_fee_year1)} a year — ${lk(wa.licence_fee_month, 2)} a month, about ${pc((wa.licence_fee_month / r.reserve_licence_fee_month_lakh - 1) * 100, 0)} above ADA's reserve. Hold that line in the auction room.`);

  // 08 equity
  s = slide(p);
  const eq = f.equity;
  y = L.head(s, "08", "Option A · Equity",
    "A third party funds the project for a share of it. No repayment obligation, no covenant — and on these numbers the most expensive money on the table.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: ["Capital", cr(eq.investment)] },
    { cells: ["Stake offered", pc(eq.stake_pct, 0)] },
    { cells: ["Exit", `End of year ${eq.exit_year}, valued as the discounted remaining concession cash flow`] },
    { cells: ["Exit equity value", cr(eq.exit_equity_value)] },
    { cells: ["Investor proceeds — dividends plus exit", cr(eq.dividends.reduce((a, b) => a + b, 0) + eq.exit_proceeds)] },
    { cells: ["Investor IRR", pc(eq.irr_pct)], emphasis: "total" },
    { cells: ["Stake needed to clear a 22% hurdle", pc(eq.stake_for_22pct, 0)], emphasis: "total" },
  ], { colW: [7.4, L.W - 2 * L.M - 7.4], rowH: 0.36 });
  L.verdict(s, y + 0.3, "stop", "Project-level equity is the wrong instrument here",
    `At ${pc(eq.stake_pct, 0)} the investor earns ${pc(eq.irr_pct)} — below a deposit rate. Clearing a conventional 22% hurdle would take ${pc(eq.stake_for_22pct, 0)} of the project. A seven-year concession generating ${cr(f.project_fcf.cumulative_fcf)} of lifetime free cash flow cannot pay an equity return on ${cr(eq.investment)} and still leave E-O-D a reason to operate it. If equity is wanted, raise it at company level.`, 1.6);
  L.foot(s, NAME);

  sectionDebt(p, f, NAME,
    "A CGTMSE-guaranteed composite facility: a small term loan against mobilisation, and a revolving working-capital limit against the operating cycle. No collateral, no charge on ADA's assets — which matters, because there are none to charge.",
    { kind: "go", head: "The facility fits — but the moratorium is doing the work",
      body: `The three-year principal moratorium pushes the first repayment into year 4, when EBITDA is ${cr(yrs[3].ebitda)} rather than ${cr(yrs[1].ebitda)}. A bank offering this with a one-year moratorium is offering a facility that defaults in year 2.` });

  // 10 CCD
  s = slide(p);
  const cc = f.ccd;
  y = L.head(s, "10", "Option C · Debt converted to equity",
    "Money in as debt, a coupon while the project ramps, then compulsory conversion into equity on a formula fixed the day it is issued.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: ["Principal", cr(cc.principal)] },
    { cells: ["Coupon, paid annually until conversion", pc(cc.coupon_pct, 1)] },
    { cells: ["Conversion — compulsory, not at the holder's option", `End of year ${cc.conversion_year}`] },
    { cells: ["Conversion stake", pc(cc.conversion_stake_pct, 0)] },
    { cells: ["Coupon paid to conversion", cr(cc.coupon_paid_total)] },
    { cells: ["Investor IRR", pc(cc.irr_pct)], emphasis: "total" },
  ], { colW: [8.4, L.W - 2 * L.M - 8.4], rowH: 0.36 });
  L.verdict(s, y + 0.2, "stop", "Worse than either pure option, at project level",
    `The CCD returns ${pc(cc.irr_pct)} — below the equity case, because the coupon years consume the cash the project needs while ramping. It combines the cash-flow burden of debt with the dilution of equity and the guarantee benefit of neither.\n\nIf a CCD is used anywhere: the conversion formula must be fixed on the date of issue, or it fails the FEMA pricing test and becomes external commercial borrowing. Until it converts it is borrowing on the balance sheet.`);
  L.foot(s, NAME);

  sectionCompare(p, f, NAME, null, {
    num: "11", kind: "go", head: "Option B — a right-sized CGTMSE composite facility",
    body: `The project earns ${pc(f.project_fcf.irr_pct)} against ${pc(f.cost_of_capital.all_in_cost_of_cgtmse_debt_pct, 2)} guaranteed debt. That ${pp(f.cost_of_capital.spread_over_debt_pct)} spread belongs to E-O-D, and debt is the only instrument that lets E-O-D keep it. Term loan ${cr(db.term_loan)} over ${db.tl_tenor_years} years with a ${db.tl_moratorium_years}-year principal moratorium, plus a working-capital limit sanctioned at ${cr(f.debt_optimised.wc_limit)} rather than the full year of opex — saving ${lk(f.agf_saving_optimised, 2)} of guarantee fee and leaving more of the group's ₹10 Cr CGTMSE ceiling for Karnal.`,
  });

  // 12 risks
  s = slide(p);
  y = L.head(s, "12", "Risks and open items");
  L.itemList(s, y, [
    { title: "Auction overshoot", color: C.terra,
      body: `No cap on the forward e-auction. Every ₹1 lakh a year above the modelled ${lk(g.bid_licence_year1, 0)} costs about ₹8.1 lakh over the term. Mitigation: a board-approved walk-away of ${lk(wa.licence_fee_year1)} a year.` },
    { title: "ADA tariff control", color: C.terra,
      body: "ADA fixes the gate at ₹20 and approves every other rate. The show ticket carries roughly a third of revenue and E-O-D cannot price it. Mitigation: agree the tariff and escalation path in writing before the work order." },
    { title: "Laser and fountain asset condition", color: C.amber,
      body: "The agency inherits equipment of unknown age and must replace end-of-life assets at its own cost. Mitigation: joint condition survey and AMC history before bidding." },
    { title: "Year-1 cash", color: C.amber,
      body: `The project loses ${cr(-yrs[0].ebitda)} at EBITDA in year 1 while paying six months of licence fee in advance. Mitigation: this is what the working-capital limit is for.` },
    { title: "No permanent structures", color: C.amber,
      body: "Clause 3.3.2 bars permanent construction, so the activity layer must be demountable — higher unit cost, shorter asset life. The capex schedule assumes an eight-year life." },
    { title: "Show tariff is not set in the RFP", color: C.blue,
      body: "Left to be agreed with ADA at least ten days before implementation. The largest revenue assumption in the model and the least documented. Raise it as a pre-bid query." },
  ], { cols: 2, rowH: 1.26 });
  L.foot(s, NAME);

  return p.writeFile({ fileName: path.join(OUT, "EOD-Geeta-Govind-Vatika-Project-Finance.pptx") });
}

/* ============================ 2 · RAMAYAN VATIKA ======================== */
function buildRV() {
  const v = M.rv, f = v.financing, r = v.rfp, db = f.debt, yrs = v.years;
  const cap = f.true_capital_requirement, mob = v.mobilisation, dc = f.debt_capacity, wa = f.walk_away;
  const p = newDeck("Ramayan Vatika — Project Finance", "BDA licence-fee concession, 10+5 years");
  const NAME = "Ramayan Vatika · Bareilly Development Authority · Project finance";

  L.cover(slide(p), {
    eyebrow: "Project finance · 02 of 04", title: "Ramayan\nVatika",
    sub: "Fifteen years of operating rights over a 51-foot bronze Ram, a holographic show projected onto it, and 16,000 Miyawaki trees in Bareilly. The longest contract in the portfolio, the tightest margin, and the only one where the RFP forbids pledging anything.",
    meta: "Bareilly Development Authority · 10 + 5 years · 5-year lock-in\nReserve licence fee ₹30 lakh a year · sealed H1 bid · performance security ₹30 lakh",
    stats: [
      { label: "Facility as briefed", value: cr(f.facility_ask), sub: "Two years of operating cost" },
      { label: "Debt the project carries", value: cr(dc.max_total_limit), sub: `At a ${dc.target_dscr}× DSCR floor` },
      { label: "Project IRR", value: pc(f.project_fcf.irr_pct), sub: `Against ${pc(f.cost_of_capital.all_in_cost_of_cgtmse_debt_pct, 2)} guaranteed debt` },
      { label: "Walk-away licence fee", value: lk(wa.licence_fee_year1), sub: `${lk(wa.licence_fee_month, 2)} a month` },
    ],
  });

  // 00 read this first
  let s = slide(p);
  s.background = { color: C.white };
  L.verdict(s, 0.5, "stop", "Read this before the rest of the deck",
    `This deck does not conclude that Ramayan Vatika should be funded on the terms briefed. On the base assumptions the project returns ${pc(f.project_fcf.irr_pct)} against a ${pc(f.cost_of_capital.all_in_cost_of_cgtmse_debt_pct, 2)} cost of guaranteed debt, and services ${cr(dc.max_total_limit)} of facility against the ${cr(f.facility_ask)} asked for.\n\nThe three financing structures are set out in full because they were asked for, and because the project does work on BDA's own revenue assumptions. But the bid discipline is the part that matters: the model solves the break-even licence fee at ${lk(wa.licence_fee_year1)} a year against BDA's ${lk(r.reserve_licence_fee_year_lakh, 0)} reserve — ${pc((wa.licence_fee_year1 / r.reserve_licence_fee_year_lakh - 1) * 100, 0)} of headroom in a sealed highest-bid process.`, 2.9);
  L.stats(s, 3.7, [
    { label: "Base case project IRR", value: pc(f.project_fcf.irr_pct), color: C.terra,
      tint: "FBF1EE", line: C.terra, sub: "Below the cost of its own debt" },
    { label: "On BDA's own assumption", value: pc(v.scenarios.bda_indicative.project_irr_pct), color: C.green,
      tint: "EDFAF4", line: C.green, sub: "500 visitors a day, 60% buying the show" },
    { label: "The whole difference", value: "Show conversion", small: true,
      sub: "42% → 52% modelled here against BDA's 60%. There is no operating history to calibrate against." },
  ], { h: 1.42 });
  L.verdict(s, 5.42, "note", "What would change the recommendation",
    "Three written answers from BDA move this from marginal to clearly fundable: the show's capacity, slot count and any soft-launch footfall; an agreed tariff with a contractual escalation path; and resolution of the five-versus-seven-year lock-in conflict. All three are free to ask.");
  L.foot(s, NAME);

  // 01 the project
  s = slide(p);
  let y = L.head(s, "01", "The project",
    "BDA has built a 33,000 square metre thematic park around the Ramayana. The centrepiece is a 51-foot bronze Lord Ram by Ram Sutar, with a 3D holographic laser and sound programme projected onto the statue.");
  y = L.table(s, y, ["Term", "What the RFP says"], [
    { cells: ["Authority", r.authority] },
    { cells: ["Contract period", `${r.term} · ${r.area_sqm.toLocaleString()} sq m (~${r.area_acres} acres)`] },
    { cells: ["Lock-in", `${r.lock_in}  —  clause 9 says seven years where clause 14 says five. Unresolved.`] },
    { cells: ["Selection", "Technically qualified plus financially H1, sealed bid, with presentation"] },
    { cells: ["Reserve licence fee", `${lk(r.reserve_licence_fee_year_lakh, 0)} a year · ${lk(r.reserve_licence_fee_year_lakh / 4, 2)} quarterly in advance`] },
    { cells: ["Performance security", `${lk(r.performance_security_lakh, 0)}, interest-free, held until three months after completion`] },
    { cells: ["Statutory burden", "EPF and ESI mandatory; agreement compulsorily registered, stamp duty on the operator"] },
  ], { colW: [3.0, L.W - 2 * L.M - 3.0], rowH: 0.36, fontSize: 11 });
  L.verdict(s, y, "stop", "Two clauses that decide how this can be financed",
    "No charge over the asset. The Vatika cannot be mortgaged, pledged or hypothecated to any bank, FI or NBFC. That removes conventional project finance and leaves a collateral-free CGTMSE facility as the only sensible debt route — the guarantee substitutes for the security the contract forbids.\n\nNo change of control without consent. No change in ownership pattern, shareholding structure or controlling interest during the lock-in without BDA's prior written approval. That is a condition precedent on Options A and C, not a footnote.", 1.72);
  L.foot(s, NAME);

  // 02 the ask
  s = slide(p);
  y = L.head(s, "02", "What the money is for",
    `The brief was two years of opex. Sized literally that is ${cr(f.facility_ask)}. The project's capacity to service debt is ${cr(dc.max_total_limit)}. The gap between those two numbers is the whole question.`);
  y = L.stats(s, y, [
    { label: "Facility as briefed", value: cr(f.facility_ask), sub: "Two full years of operating cost" },
    { label: "True capital at risk", value: cr(cap.total), sub: "Mobilisation, toy train, and two years of deficit" },
    { label: "Serviceable at 1.30× DSCR", value: cr(dc.max_total_limit), tint: "FBF1EE", line: C.terra,
      sub: `Gap to the brief: ${cr(f.facility_ask - dc.max_total_limit)}` },
  ], { h: 1.26 });
  y = L.table(s, y, ["Requirement", "Amount"], [
    { cells: ["Mobilisation capex — ticketing, food court, activity equipment, signage", lk(mob.capex_year0)] },
    { cells: ["Performance security — interest-free for the whole 15-year term", lk(mob.performance_security)] },
    { cells: ["EMD, bid fee, stamp duty, registration and the first quarter's licence fee",
              lk(mob.emd + mob.bid_fee + mob.stamp_duty_registration + mob.advance_licence_fee_q1)] },
    { cells: ["Sub-total — mobilisation", lk(mob.total)], emphasis: "sub" },
    { cells: ["Toy train (year 2, optional) and two years of operating expenditure",
              lk(mob.capex_year2_toy_train + v.opex_year1 + v.opex_year2)] },
    { cells: ["Facility requested", lk(f.facility_ask)], emphasis: "total" },
  ], { colW: [10.0, L.W - 2 * L.M - 10.0], rowH: 0.33 });
  L.verdict(s, y, "caution", "The performance security is the hidden cost",
    `${lk(r.performance_security_lakh, 0)} sits with BDA interest-free for fifteen years — roughly ₹52 lakh of foregone return at an 11.5% opportunity cost, more than a year and a half of licence fee. Price it into the bid.`);
  L.foot(s, NAME);

  // 03 revenue
  s = slide(p);
  y = L.head(s, "03", "Revenue model",
    `BDA published its own indicative revenue of ₹2.25–2.30 crore a year. This model sits below it early and reaches it in year 3 — because the assumption BDA's number rests on is the one most likely to be wrong.`);
  const RK = [["entry", "Entry ticketing"], ["show", "Holographic & laser show"], ["fnb", "Food court"]];
  y = L.chart(s, p, y, "barStacked", [
    ...RK.map(([k, n]) => ({ name: n, labels: yrs.map(x => `Yr ${x.year}`),
                             values: yrs.map(x => +crN(x.revenue[k])) })),
    { name: "Parking, events, toy train, ancillary", labels: yrs.map(x => `Yr ${x.year}`),
      values: yrs.map(x => +crN(x.revenue.parking + x.revenue.events
                              + x.revenue.ancillary + x.revenue.toy_train)) },
  ], { h: 2.80, axisTitle: "₹ crore", labelPos: "ctr",
       colors: [C.blue, C.terra, C.green, "8A93A6"] });
  L.verdict(s, y + 0.05, "stop", "Where this model parts company with BDA",
    `BDA's ₹2.30 crore assumes 500 visitors a day with 300 of them paying ₹125 for the show — a 60% conversion, implying three in five visitors including morning walkers, families with small children and school groups buy an evening show. This model starts at 42% and reaches 52% by year 10. That single assumption is worth about ${lk(f.conversion_gap_value.value_lakh, 0)} a year at year-5 volumes.`, 1.42);
  L.foot(s, NAME);

  // 04 cost
  s = slide(p);
  y = L.head(s, "04", "Cost model",
    "A maintenance-heavy contract. BDA transfers the entire comprehensive maintenance obligation — civil, electrical, horticultural, statuary and IT — to the operator, at the operator's cost.");
  const VK = [["licence_fee", "Licence fee to BDA"], ["manpower", "Payroll"],
              ["electricity", "Electricity"], ["horticulture", "Horticulture"],
              ["show_amc", "Show AMC"], ["statue_upkeep", "Statue and artefact upkeep"]];
  y = L.table(s, y, ["₹ crore", ...yrs.filter((_, i) => i % 2 === 0).map(x => `Yr ${x.year}`)],
    [...VK.map(([k, n]) => ({ cells: [n, ...yrs.filter((_, i) => i % 2 === 0).map(x => crN(x.opex[k]))] })),
     { cells: ["Other operating cost", ...yrs.filter((_, i) => i % 2 === 0).map(x =>
        crN(x.opex.total - VK.reduce((a, [k]) => a + x.opex[k], 0)))] },
     { cells: ["Total operating cost", ...yrs.filter((_, i) => i % 2 === 0).map(x => crN(x.opex.total))], emphasis: "total" },
     { cells: ["Revenue", ...yrs.filter((_, i) => i % 2 === 0).map(x => crN(rev(x)))], emphasis: "sub" },
     { cells: ["EBITDA margin", ...yrs.filter((_, i) => i % 2 === 0).map(x => pc(x.ebitda_margin, 0))], emphasis: "total" }],
    { colW: [4.2, ...Array(5).fill((L.W - 2 * L.M - 4.2) / 5)], rowH: 0.32, fontSize: 10.5 });
  L.verdict(s, y, "caution", "The manpower floor is contractual, not discretionary",
    "BDA prescribes 4 sweepers and 5 security per shift plus 8 gardeners, a site manager, an electrician and a plumber per day — about 29 heads before a ticket is sold, and roughly 37 with ticketing and show staff. Payroll cannot flex in a bad season. That is why the margin here is thinner than at Geeta Govind Vatika.");
  L.foot(s, NAME);

  sectionProjection(p, f, yrs, NAME,
    "Two loss-making years, then a slow climb. The shape is the direct consequence of a fixed manpower floor meeting a ramping revenue line.");
  sectionReturns(p, f, NAME, "Below the cost of its own guaranteed debt");
  sectionScenarios(p, v.scenarios, NAME,
    "One assumption separates a project that should not be bid from one that comfortably clears its cost of capital: how many visitors buy the show.",
    "go", "BDA's own case works — and it is not implausible",
    `On BDA's own assumptions the project returns ${pc(v.scenarios.bda_indicative.project_irr_pct)}. Bid a price that survives the base case and rewards the BDA case.`);

  // 08 equity
  s = slide(p);
  const eq = f.equity;
  y = L.head(s, "08", "Option A · Equity",
    "Sized to the true capital requirement rather than the gross facility, and valued at exit on the discounted cash flow still to come over the balance of the concession.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: ["Capital", cr(eq.investment)] },
    { cells: ["Stake offered", pc(eq.stake_pct, 0)] },
    { cells: ["Exit", `End of year ${eq.exit_year}, at ${cr(eq.exit_equity_value)} of project equity value`] },
    { cells: ["Investor IRR", pc(eq.irr_pct)], emphasis: "total" },
    { cells: ["Stake needed to clear a 22% hurdle", pc(eq.stake_for_22pct, 0)], emphasis: "total" },
  ], { colW: [7.4, L.W - 2 * L.M - 7.4], rowH: 0.36 });
  L.verdict(s, y + 0.24, "stop", "The arithmetic does not work — and it needs BDA's consent",
    `At ${pc(eq.stake_pct, 0)} of the project an investor earns ${pc(eq.irr_pct)}; a 22% hurdle would take ${pc(eq.stake_for_22pct, 0)} — the whole project and then some.\n\nAny structure that changes VAPPL's shareholding also needs BDA's prior written approval during the lock-in, with forfeiture of the performance security as the stated consequence. The equity conversation starts at BDA's office.`);
  L.foot(s, NAME);

  sectionDebt(p, f, NAME,
    "The RFP forbids any charge over the Vatika. That is not an obstacle to a CGTMSE facility — it is the reason to use one. The guarantee replaces the security the contract will not allow.",
    { kind: "stop", head: "The facility as briefed does not clear a bank's coverage test",
      body: `At ${cr(db.total_limit)} the minimum post-moratorium DSCR is ${xx(db.min_dscr_post_moratorium)}; banks underwrite to 1.30×. The workable structure sanctions ${cr(f.facility_ask)} but commits ${cr(dc.max_total_limit)}. Two full years of opex presented as committed term money will be declined.` });

  // 10 CCD
  s = slide(p);
  const cc = f.ccd;
  y = L.head(s, "10", "Option C · Debt converted to equity",
    "Money in as debt, a coupon while the park ramps, compulsory conversion into equity on a fixed formula.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: ["Principal", cr(cc.principal)] },
    { cells: ["Coupon, annual until conversion", pc(cc.coupon_pct, 1)] },
    { cells: ["Conversion", `End of year ${cc.conversion_year}, into ${pc(cc.conversion_stake_pct, 0)} of project equity`] },
    { cells: ["Coupon paid to conversion", cr(cc.coupon_paid_total)] },
    { cells: ["Investor IRR", pc(cc.irr_pct)], emphasis: "total" },
  ], { colW: [8.4, L.W - 2 * L.M - 8.4], rowH: 0.36 });
  L.verdict(s, y + 0.3, "stop", "Three separate reasons this is the worst of the three here",
    `Cash — the coupon falls due in years 1 to ${cc.conversion_year}, precisely the years the project loses money at EBITDA. ${cr(cc.coupon_paid_total)} has to come from somewhere, and it is not coming from the gate.\n\nConsent — conversion changes the shareholding pattern, which needs BDA's prior written approval inside the lock-in. An instrument that must convert on a fixed date, into a change a third party can refuse to approve, is a structural mismatch.\n\nLeverage — until it converts a CCD is borrowing. Layered on VAPPL's 3.04× gearing it breaches the covenant on any CGTMSE facility running alongside it.`, 2.3);
  L.foot(s, NAME);

  sectionCompare(p, f, NAME, null, {
    num: "11", kind: "caution",
    head: `Bid at reserve. Fund with a CGTMSE limit, committed at ${cr(dc.max_total_limit)}.`,
    body: `Of the three structures only debt is both viable and permitted without BDA's consent — and viable only if the facility is sanctioned at ${cr(f.facility_ask)} but committed at ${cr(dc.max_total_limit)}. The binding condition sits earlier than the financing: break-even licence fee is ${lk(wa.licence_fee_year1)} a year against a ${lk(r.reserve_licence_fee_year_lakh, 0)} reserve — ${pc((wa.licence_fee_year1 / r.reserve_licence_fee_year_lakh - 1) * 100, 0)} of headroom in a sealed highest-bid process. Bid at or barely above reserve, or do not bid. On a contract with a five-year lock-in and a fifteen-year restoration obligation, winning at the wrong price is worse than losing.`,
  });

  // 12 risks
  s = slide(p);
  y = L.head(s, "12", "Risks and open items");
  L.itemList(s, y, [
    { title: "Show conversion", color: C.terra,
      body: "Roughly half the revenue comes from one product with no operating history. Mitigation: obtain slot capacity and soft-launch data pre-bid; bid a price that survives the base case." },
    { title: "Bid price in a sealed H1 process", color: C.terra,
      body: `Break-even is ${lk(wa.licence_fee_year1)} against a ${lk(r.reserve_licence_fee_year_lakh, 0)} reserve, in a format that rewards the highest bid. Mitigation: a board-approved ceiling before the bid is sealed.` },
    { title: "Five-year lock-in", color: C.terra,
      body: `Exit before it expires costs the remaining contractual amount plus the ${lk(r.performance_security_lakh, 0)} security. Payback lands at roughly year seven. No contractual mitigation — the bid price has to be right.` },
    { title: "Restoration at handover", color: C.amber,
      body: "Every asset returned in handover condition, BDA's decision binding. A bronze statue and a Miyawaki forest over fifteen years. Mitigation: photographed joint handover report on day one; accrue a provision annually." },
    { title: "Lock-in conflict unresolved", color: C.blue,
      body: "Clause 9 states seven years where clause 14 states five. A seven-year lock-in materially worsens the risk. Settle by pre-bid query before anything is committed." },
    { title: "Restoration at handover", color: C.amber,
      body: "Every asset returned in handover condition, BDA's decision binding. A bronze statue and a Miyawaki forest over fifteen years. Mitigation: a photographed joint handover report on day one and a restoration provision accrued annually." },
  ], { cols: 2, rowH: 1.26 });
  L.foot(s, NAME);

  return p.writeFile({ fileName: path.join(OUT, "EOD-Ramayan-Vatika-Project-Finance.pptx") });
}

/* ================================ 3 · KARNAL =========================== */
function buildKarnal() {
  const k = M.karnal, f = k.financing, ff = k.facts, db = f.debt, yrs = k.years;
  const p = newDeck("Karnal — Project Finance", "NH-1 private sub-lease, 15 years");
  const NAME = "Karnal · NH-1 Gharaunda · Project finance";

  L.cover(slide(p), {
    eyebrow: "Project finance · 03 of 04", title: "Karnal",
    sub: "The only one of the three that is a build, not a takeover. Fifteen years on India's busiest national highway, a signed sub-lease, a long rent-free construction window — and the only project in the portfolio with assets a lender can take a charge over.",
    meta: "Sub-lease with A4A Highway Nest LLP · NH-1 Milestone 109, Gharaunda · 15-year term\nMinimum guarantee ₹2–3 lakh a month from opening · Phase 1 build-out ₹4.00 Cr · opening ~September 2027",
    stats: [
      { label: "Project cost", value: cr(f.project_cost), sub: "Phase 1 build-out, as committed in the investor deck" },
      { label: "Project IRR", value: pc(f.project_fcf.irr_pct), sub: `Payback ${f.project_fcf.payback_years.toFixed(1)} years` },
      { label: "Minimum DSCR", value: xx(db.min_dscr_post_moratorium), sub: "Comfortably above the 1.30× bank floor" },
      { label: "First full year EBITDA", value: cr(yrs[1].ebitda), sub: `${pc(yrs[1].ebitda_margin)} on ${cr(yrs[1].revenue)}` },
    ],
  });

  // 01 the project
  let s = slide(p);
  let y = L.head(s, "01", "The project",
    "Karnal replicates the Delhi–Meerut Expressway format on a busier corridor. DME proved the highway-stopover model works and exposed exactly where it fails — indoor-only product against a fixed common-area charge. Karnal is built with the outdoor activity stack from day one.");
  y = L.table(s, y, ["Term", "Position"], [
    { cells: ["Site", ff.site] },
    { cells: ["Counterparty", `${ff.counterparty} — a private sub-lease, not a government concession`] },
    { cells: ["Term", `${ff.term_years} years · minimum guarantee ₹2–3 lakh a month from opening`] },
    { cells: ["Build", `${ff.build_months} months · opening ${ff.open_estimate} · long rent-free build period`] },
    { cells: ["Asset position", "E-O-D owns the activity equipment, fit-out and fixtures — a lender can hypothecate them"], emphasis: "total" },
  ], { colW: [3.0, L.W - 2 * L.M - 3.0], rowH: 0.36 });
  y = L.verdict(s, y + 0.2, "go", "The strongest of the three — and one fact to settle first",
    "No auction, no authority tariff control, no mandated manpower floor, no restoration obligation over somebody else's bronze statue — and real assets that can secure the facility funding them.\n\nBut: index.html records ~22,000 sq ft where financials.html reads ~6 acres. The footprint drives the revenue ceiling. Confirm it against the executed sub-lease before any drawdown.");
  L.foot(s, NAME);

  // 02 project cost
  s = slide(p);
  y = L.head(s, "02", "Project cost",
    "Unlike the two concessions, every rupee here is capital. There is no revolving working-capital component to separate out — the money buys assets that stay bought.");
  y = L.chart(s, p, y, "bar", [
    { name: "Capex", labels: k.capex_lines.map(c => c.item.split(" — ")[0].split(",")[0].slice(0, 30)),
      values: k.capex_lines.map(c => +crN(c.amount)) },
  ], { h: 2.15, axisTitle: "₹ crore", colors: [C.blue],
       extra: { barDir: "bar", catAxisLabelFontSize: 9 } });
  y = L.stats(s, y + 0.05, [
    { label: "Project cost", value: cr(f.project_cost), sub: "As committed in the ₹10 Cr investor deck" },
    { label: "Promoter contribution", value: cr(db.promoter_contribution),
      sub: `${pc(db.promoter_margin_pct, 0)} margin — the standard bank requirement` },
    { label: "Term loan sought", value: cr(db.term_loan), sub: "Against the assets financed" },
  ], { h: 1.22 });
  L.verdict(s, y + 0.02, "note", "This is already funded in the existing plan — the question is how",
    `The round earmarks ₹4 crore for Karnal. On these numbers that is not the cheapest way: the project earns ${pc(f.project_fcf.irr_pct)} against ${pc(f.cost_of_capital.all_in_cost_of_cgtmse_debt_pct, 2)} guaranteed debt. Debt-funding it frees that ₹4 crore for the parks with no debt route.`);
  L.foot(s, NAME);

  // 03 projection
  s = slide(p);
  y = L.head(s, "03", "Ten-year projection",
    "Revenue follows the range published in the company financial model: ₹0.50–1.00 crore in the FY27-28 stub half-year, ₹3.00–4.00 crore in the first full year. Midpoints used throughout.");
  y = L.chart(s, p, y, "bar", [
    { name: "Revenue", labels: yrs.map(v => `Yr ${v.year}`), values: yrs.map(v => +crN(v.revenue)) },
    { name: "EBITDA", labels: yrs.map(v => `Yr ${v.year}`), values: yrs.map(v => +crN(v.ebitda)) },
  ], { h: 2.75, axisTitle: "₹ crore", colors: [C.blue, C.green] });
  L.stats(s, y + 0.05, [
    { label: "First full year", value: cr(yrs[1].revenue), sub: `${pc(yrs[1].ebitda_margin)} EBITDA margin` },
    { label: "Margin at year 5", value: pc(yrs[4].ebitda_margin), sub: "Against 21.6% at GGV and 20.3% at Ramayan Vatika in the same year" },
    { label: "Year 10 EBITDA", value: cr(yrs[9].ebitda), sub: "Five sub-lease years still to run beyond the model" },
  ], { h: 1.22 });
  L.foot(s, NAME);

  sectionReturns(p, f, NAME, "The closest of the three to clearing an equity hurdle", "04");
  sectionScenarios(p, k.scenarios, NAME,
    "The revenue range in the company financial model is ₹3–4 crore for the first full year. Base is the midpoint; downside sits below the published floor.",
    "go", "Even the downside services its debt",
    `At 25% below base — under the floor of the published range — the project still reaches ${cr(k.scenarios.downside.ebitda_stabilised)} of stabilised EBITDA. A project with its own assets flexes its cost base; one renting somebody else's cannot.`, "05");

  // 06 equity
  s = slide(p);
  const eq = f.equity;
  y = L.head(s, "06", "Option A · Equity",
    "How Karnal is funded in the existing plan — ₹4 crore of the ₹10 crore round. Shown at project level so it compares like for like against the other two instruments.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: [`Capital — ${cr(f.project_cost)} of build cost plus ${cr(f.true_capital_requirement.cumulative_operating_deficit)} for the year-1 ramp`, cr(eq.investment)] },
    { cells: ["Stake offered", pc(eq.stake_pct, 0)] },
    { cells: ["Distributions from year 3", cr(eq.dividends.reduce((a, b) => a + b, 0))] },
    { cells: ["Exit", `End of year ${eq.exit_year} at ${cr(eq.exit_equity_value)}`] },
    { cells: ["Investor IRR", pc(eq.irr_pct)], emphasis: "total" },
    { cells: ["Stake needed to clear a 22% hurdle", pc(eq.stake_for_22pct, 0)], emphasis: "total" },
  ], { colW: [9.0, L.W - 2 * L.M - 9.0], rowH: 0.36 });
  L.verdict(s, y + 0.3, "caution", "Better than the concessions, still short of a hurdle",
    `At ${pc(eq.stake_pct, 0)} the investor earns ${pc(eq.irr_pct)} — the best of the three project-level equity cases in this pack, and still well short of 22%. The reason is structural: a single park generating ₹2–2.6 crore of mature EBITDA cannot carry both a venture return on ₹4 crore and an operator's margin. Equity works at portfolio level, where one round backs five parks and a brand. It does not work one park at a time — which is an argument about where the equity sits, not whether to raise it.`, 1.6);
  L.foot(s, NAME);

  sectionDebt(p, f, NAME,
    "A conventional CGTMSE term loan against assets the borrower owns, with a promoter margin and a construction moratorium. Of the three projects, this is the one a credit committee will recognise immediately.",
    { kind: "go", head: "The cleanest credit in the pack",
      body: `A signed fifteen-year sub-lease, assets the bank can hypothecate, a ${db.tl_moratorium_years}-year moratorium covering construction and ramp, and DSCR at ${xx(db.min_dscr_post_moratorium)}. Bank this one first — the sanction establishes the CGTMSE record the two concession facilities will need.` }, "07");

  // 08 CCD
  s = slide(p);
  const cc = f.ccd;
  y = L.head(s, "08", "Option C · Debt converted to equity",
    "Debt with a fixed conversion date. The instrument that most closely matches a build-and-ramp project: no dilution while the site is under construction, conversion once it is trading.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: ["Principal", cr(cc.principal)] },
    { cells: ["Coupon, annual until conversion", pc(cc.coupon_pct, 1)] },
    { cells: ["Conversion — one full year after opening", `End of year ${cc.conversion_year}, into ${pc(cc.conversion_stake_pct, 0)}`] },
    { cells: ["Coupon paid to conversion", cr(cc.coupon_paid_total)] },
    { cells: ["Investor IRR", pc(cc.irr_pct)], emphasis: "total" },
  ], { colW: [8.4, L.W - 2 * L.M - 8.4], rowH: 0.36 });
  L.verdict(s, y + 0.2, "stop", "The coupon lands in the wrong years",
    `Years 1 to ${cc.conversion_year} are construction and ramp — the project loses ${cr(-yrs[0].ebitda)} at EBITDA in year 1, and there is no rent-free relief on a debenture coupon. ${cr(cc.coupon_paid_total)} has to come from the group while the site is being built. A CGTMSE term loan with a two-year moratorium defers the same burden for less.\n\nIf the objective is deferred dilution rather than debt capacity, a zero-coupon CCD with a conversion premium removes the cash burden — priced on the date of issue, to satisfy the FEMA formula test.`);
  L.foot(s, NAME);

  sectionCompare(p, f, NAME, null, {
    num: "09", kind: "go", head: "Option B — and take this facility to the bank first",
    body: `Karnal earns ${pc(f.project_fcf.irr_pct)} against ${pc(f.cost_of_capital.all_in_cost_of_cgtmse_debt_pct, 2)} guaranteed debt, covers its service at ${xx(db.min_dscr_post_moratorium)} from the first repayment year, and — uniquely in this pack — owns assets a lender can hypothecate. A ${cr(db.term_loan)} term loan with ${cr(db.promoter_contribution)} of promoter margin funds the whole build for ${cr(db.total_finance_cost)} of total finance cost, against giving away ${pc(eq.stake_pct, 0)} of a park generating ${cr(yrs[9].ebitda)} of EBITDA by year 10. The wider consequence matters more: funding Karnal with debt releases the ₹4 crore earmarked for it in the equity round, and that capital has no debt alternative at the two concessions.`,
  });

  // 10 risks
  s = slide(p);
  y = L.head(s, "10", "Risks and open items");
  L.itemList(s, y, [
    { title: "Footprint unconfirmed", color: C.terra,
      body: "index.html records ~22,000 sq ft; the Karnal assumption block in financials.html reads ~6 acres. The two are not reconcilable and the footprint drives the revenue ceiling. Read the executed sub-lease before any drawdown." },
    { title: "Construction and opening slippage", color: C.amber,
      body: "A twelve-month build to a September 2027 opening. Slipping past the summer pushes a full peak quarter into the next year. The two-year moratorium absorbs a season; contract the build with liquidated damages." },
    { title: "First-full-year revenue", color: C.amber,
      body: `${cr(yrs[1].revenue)} in the first full year is a projection for an unbuilt park. DME's first year was ₹25 lakh. Karnal opens with the outdoor stack DME lacked, on a busier corridor.` },
    { title: "Counterparty concentration", color: C.amber,
      body: "A single private sub-lessor holds the head lease. Its default or loss of tenure ends the project. Confirm the head-lease tenure exceeds the sub-lease; seek a direct agreement or step-in right." },
    { title: "Minimum guarantee in a weak year", color: C.amber,
      body: "₹2–3 lakh a month is payable whether or not anyone stops — the same mechanism that produced DME's ₹29.9 lakh fixed-CAM loss. Negotiate MG against a revenue share, whichever is higher." },
    { title: "Rent-free period undefined", color: C.blue,
      body: "Described as “long” without a duration. This model assumes no rent until opening. Confirm whether it is tied to commissioning or to a fixed date." },
  ], { cols: 2, rowH: 1.26 });
  L.foot(s, NAME);

  return p.writeFile({ fileName: path.join(OUT, "EOD-Karnal-Project-Finance.pptx") });
}

/* =============================== 4 · COMPANY =========================== */
function buildCompany() {
  const c = M.company, pr = c.profile, fy = pr.fy26, fin = c.financing;
  const eq = fin.equity, db = fin.debt, cc = fin.ccd, lev = db.leverage;
  const rpc = c.related_party_conversion, ms = c.msme, ex = c.exit_basis;
  const consol = M.consolidated.years, alloc = M.cgtmse_allocation;
  const p = newDeck("Vision Amusement Park — Company Capital Structure",
                    "Equity, CGTMSE debt and debt converted to equity");
  const NAME = "Vision Amusement Park Pvt. Ltd. · Company capital structure";

  L.cover(slide(p), {
    eyebrow: "Project finance · 04 of 04", title: "Vision\nAmusement Park",
    sub: "Three ways to fund the company rather than the projects — equity, guaranteed debt, and debt that becomes equity. One is materially cheaper than the headline round, and one balance-sheet move has to happen before any of them.",
    meta: `${pr.name} · CIN ${pr.cin}\nFY25-26 revenue ₹16.29 Cr · EBITDA ₹2.37 Cr · net worth ₹2.58 Cr · borrowings ₹7.85 Cr`,
    stats: [
      { label: "FY30-31 revenue", value: cr(ex.revenue, 0), sub: "Seven parks, including all three new projects" },
      { label: "Equity at ₹90 Cr pre", value: pc(eq.irr_pct), sub: "Investor IRR over five years" },
      { label: "CGTMSE ceiling", value: cr(alloc.ceiling, 0), sub: "Per borrower, across all lenders" },
      { label: "D/E after conversion", value: xx(rpc.convert_lt_plus_promoter_409.debt_equity), sub: "From 3.04× today" },
    ],
  });

  // 01 where the company stands
  let s = slide(p);
  let y = L.head(s, "01", "Where the company stands",
    "Only what determines whether VAPPL can borrow, and at what price.");
  y = L.table(s, y, ["FY25-26 position", "Amount", "What a credit committee sees"], [
    { cells: ["Revenue", cr(fy.revenue), { text: "All-time high, +27% year on year, four parks operating" }] },
    { cells: ["EBITDA", cr(fy.ebitda), "14.5% margin — a ramp year, below the 36% single-park benchmark of FY22-23"] },
    { cells: ["Net worth", cr(fy.net_worth), "Positive and improving. Was negative ₹1.30 Cr in FY22-23"] },
    { cells: ["Total borrowings", cr(fy.borrowings_total), "₹5.26 Cr short-term across 13 facilities, ₹2.60 Cr from related parties"] },
    { cells: ["Debt to equity", xx(rpc.base.debt_equity), { text: "Too high. Most banks want under 2× for an unsecured facility", color: C.terra }] },
    { cells: ["Current ratio", "~0.50×", "Below 1.0 every year — structurally dependent on revolving credit"] },
    { cells: ["Electricity arrears", cr(fy.electricity_arrears), { text: "A red flag on any sanction note", color: C.terra }], emphasis: "total" },
  ], { colW: [2.5, 1.5, L.W - 2 * L.M - 4.0], rowH: 0.36, fontSize: 10.5 });
  L.verdict(s, y, "stop", "Four things stand between VAPPL and a bank sanction",
    `Debt to equity at ${xx(rpc.base.debt_equity)}. Thirteen separate NBFC and bank facilities, which reads as distress borrowing regardless of how it arose. ${cr(fy.electricity_arrears)} of electricity arrears — a live utility default is the single item most likely to stop a sanction note. And a current ratio below 1.0 in every year on record. None of the options in this deck should reach a lender before these are fixed.`, 1.5);
  L.foot(s, NAME);

  // 02 MSME / CGTMSE
  s = slide(p);
  y = L.head(s, "02", "MSME status and CGTMSE eligibility",
    "CGTMSE covers micro and small enterprises only. VAPPL's eligibility is not marginal — but it has an expiry date, and the date is inside this plan.");
  y = L.stats(s, y, [
    { label: "Investment in plant & machinery", value: `₹${ms.investment_plant_machinery_cr.toFixed(2)} Cr`,
      sub: `Against a ₹25 Cr Small Enterprise limit — ₹${ms.headroom_investment_cr.toFixed(2)} Cr of headroom` },
    { label: "Annual turnover", value: `₹${ms.turnover_cr.toFixed(2)} Cr`,
      sub: `Against a ₹100 Cr limit — ₹${ms.headroom_turnover_cr.toFixed(2)} Cr of headroom` },
    { label: "Classification", value: "Small Enterprise", small: true, color: C.green,
      tint: "EDFAF4", line: C.green, sub: "CGTMSE eligible. Both tests cleared" },
  ], { h: 1.28 });
  y = L.table(s, y, ["Facility size", "Standard annual guarantee fee"],
    M.cgtmse.agf_slabs.filter(([capL]) => capL >= 200).map(([capL, rate]) => {
      const prevIdx = M.cgtmse.agf_slabs.findIndex(x => x[0] === capL) - 1;
      return { cells: [`Above ${money(M.cgtmse.agf_slabs[prevIdx][0])} and up to ${money(capL)}`, pc(rate, 2)],
               emphasis: capL === 1000 ? "total" : null };
    }), { colW: [8.6, L.W - 2 * L.M - 8.6], rowH: 0.28, fontSize: 10.5 });
  L.verdict(s, y, "note", "The thresholds moved in VAPPL's favour on 1 April 2025",
    "Small Enterprise limits rose to ₹25 Cr of investment and ₹100 Cr of turnover, and the CGTMSE ceiling doubled to ₹10 Cr per borrower. Both landed after the ₹10 crore equity round was designed — which is the reason this pack exists. A facility sanctioned while the company qualifies keeps its cover for its full tenor.");
  L.foot(s, NAME);

  // 03 balance sheet repair — the headline finding
  s = slide(p);
  y = L.head(s, "03", "Fix the balance sheet first",
    "Before raising anything there is a free move. Roughly ₹4 crore of VAPPL's ₹7.85 crore of borrowings is money the promoters already put in. Converting it costs no cash and transforms the balance sheet a lender is asked to lend against.");
  y = L.chart(s, p, y, "bar", [
    { name: "Largest facility inside a 2.0× covenant",
      labels: ["No\nconversion", "Convert the\n₹2.60 Cr", "Convert all\n₹4.09 Cr", "Convert all, drawn\nin tranches"],
      values: lev.cases.map(x => +crN(x.max_facility_at_covenant)) },
  ], { h: 2.15, axisTitle: "₹ crore",
       colors: lev.cases.map(x => x.max_facility_at_covenant >= 1000 ? C.green : C.terra) });
  y = L.table(s, y + 0.02, ["Conversion", "Net worth", "D/E once ₹10 Cr is drawn", "Max facility at 2.0×"],
    lev.cases.map(x => ({
      cells: [x.label.replace(/Rs /g, "₹"), cr(x.net_worth),
              { text: xx(x.debt_equity), color: x.debt_equity <= 2.0 ? C.green : C.terra },
              { text: cr(x.max_facility_at_covenant), color: x.max_facility_at_covenant >= 1000 ? C.green : C.terra }],
      emphasis: x.conversion === lev.conversion_full && !x.retained_earnings ? "total" : null,
    })), { colW: [5.4, 1.9, 2.6, 2.2], rowH: 0.34, fontSize: 10.5 });
  L.verdict(s, y, "stop", "Converting only the ₹2.60 crore is not enough",
    `Converting ${cr(260)} caps the facility at ${cr(lev.cases[1].max_facility_at_covenant)}. Converting all ${cr(lev.conversion_full)} lifts it to ${cr(lev.cases[2].max_facility_at_covenant)}. Converting nothing supports ${cr(lev.cases[0].max_facility_at_covenant)} — the company cannot borrow at all.`);
  L.foot(s, NAME);

  // 04 consolidated plan
  s = slide(p);
  y = L.head(s, "04", "The consolidated plan",
    "The existing four parks plus all three new projects, phased on the award and opening dates assumed in each project deck. Existing-portfolio figures are the midpoints already published in the company financial model.");
  y = L.chart(s, p, y, "barStacked", [
    { name: "Existing four parks", labels: consol.map(r => r.fy), values: consol.map(r => +crN(r.parts.existing.revenue)) },
    { name: "Geeta Govind Vatika", labels: consol.map(r => r.fy), values: consol.map(r => +crN(r.parts.ggv.revenue)) },
    { name: "Ramayan Vatika", labels: consol.map(r => r.fy), values: consol.map(r => +crN(r.parts.rv.revenue)) },
    { name: "Karnal", labels: consol.map(r => r.fy), values: consol.map(r => +crN(r.parts.karnal.revenue)) },
  ], { h: 2.70, axisTitle: "Revenue, ₹ crore", labelPos: "ctr", fmt: "0.0" });
  L.stats(s, y + 0.05, [
    { label: "FY30-31 revenue", value: cr(consol[4].revenue, 0), sub: "From ₹16.29 Cr in FY25-26" },
    { label: "FY30-31 EBITDA", value: cr(consol[4].ebitda, 0), sub: `${pc(consol[4].ebitda_margin)} margin` },
    { label: "New projects' share", value: pc(["ggv", "rv", "karnal"]
        .reduce((a, k) => a + consol[4].parts[k].revenue, 0) / consol[4].revenue * 100, 0),
      sub: "Of FY30-31 revenue. EMV was 73% of the group in FY25-26 — concentration risk materially reduced" },
  ], { h: 1.22 });
  L.foot(s, NAME);

  // 05 equity
  s = slide(p);
  y = L.head(s, "05", "Option A · Equity",
    "The existing round is ₹10 crore at ₹90 crore pre-money. Funding all three new projects with equity would take it to roughly ₹16 crore. Here is what that returns to the person writing the cheque.");
  y = L.table(s, y, ["Exit basis", "Value"], [
    { cells: [`Revenue at exit — ${ex.fy}, five years from a September 2026 close`, cr(ex.revenue, 0)] },
    { cells: [`Enterprise value at ${ex.ev_revenue_multiple.toFixed(1)}× revenue (11× EBITDA cross-checks at ${cr(ex.ev_ebitda_crosscheck, 0)})`, cr(ex.enterprise_value, 0)] },
    { cells: ["Equity value at exit, net of debt", cr(ex.equity_value, 0)], emphasis: "sub" },
    { cells: [`Investor proceeds — ${pc(eq.stake_pct, 1)} of exit equity value`, cr(eq.exit_proceeds, 0)] },
    { cells: ["Investor IRR over five years", pc(eq.irr_pct)], emphasis: "total" },
  ], { colW: [9.4, L.W - 2 * L.M - 9.4], rowH: 0.3 });
  y = L.table(s, y + 0.22, ["Investor hurdle", "Stake required", "Implied pre-money"], [
    { cells: ["18% — family office, strategic", pc(eq.pricing_sensitivity.irr_18.stake_pct), cr(eq.pricing_sensitivity.irr_18.pre_money, 0)] },
    { cells: ["22% — lower-quartile growth fund", pc(eq.pricing_sensitivity.irr_22.stake_pct), cr(eq.pricing_sensitivity.irr_22.pre_money, 0)] },
    { cells: ["25% — institutional growth equity", pc(eq.pricing_sensitivity.irr_25.stake_pct), cr(eq.pricing_sensitivity.irr_25.pre_money, 0)] },
    { cells: ["At the asking price", pc(eq.stake_pct, 1), cr(eq.pre_money, 0)], emphasis: "total" },
  ], { colW: [6.4, 2.8, L.W - 2 * L.M - 9.2], rowH: 0.32 });
  L.verdict(s, y, "caution", "₹90 crore pre-money prices most of the growth in",
    `At ₹90 crore pre-money an investor earns ${pc(eq.irr_pct)} over five years — an argument about counterparty, not valuation.`);
  L.foot(s, NAME);

  // 06 debt
  s = slide(p);
  y = L.head(s, "06", "Option B · Debt under CGTMSE",
    "A single collateral-free composite facility: a term loan for the project build-outs and a working-capital limit that consolidates the NBFC book.");
  y = L.chart(s, p, y, "bar", [
    { name: "New facility", labels: db.combined_service.map(r => `Yr ${r.year}`), values: db.combined_service.map(r => +crN(r.new_facility)) },
    { name: "Existing debt", labels: db.combined_service.map(r => `Yr ${r.year}`), values: db.combined_service.map(r => +crN(r.existing_debt)) },
    { name: "EBITDA available", labels: db.combined_service.map(r => `Yr ${r.year}`), values: db.combined_service.map(r => +crN(r.cfads)) },
  ], { h: 2.40, axisTitle: "₹ crore", colors: [C.terra, C.amber, C.blue] });
  y = L.stats(s, y + 0.02, [
    { label: "Total facility", value: cr(db.total_limit, 0),
      sub: `Term loan ${cr(db.term_loan)} + working capital ${cr(db.wc_limit)}` },
    { label: "All-in cost", value: pc(db.rate_pct + db.cgtmse.agf_rate_pct, 2),
      sub: `${pc(db.rate_pct, 2)} interest + ${pc(db.cgtmse.agf_rate_pct, 2)} guarantee fee` },
    { label: "Minimum DSCR", value: xx(db.min_dscr_combined), color: C.green,
      sub: "Including the existing ₹7.85 Cr book, not just the new facility" },
    { label: "Total finance cost", value: cr(db.total_finance_cost),
      sub: `Over seven years, against ${cr(ex.equity_value * eq.stake_pct / 100, 0)} for the equivalent equity` },
  ], { h: 1.32 });
  L.verdict(s, y + 0.02, "go", "The debt is roughly a fifth of the cost of the equity",
    `${cr(db.total_limit, 0)} collateral-free at ${pc(db.rate_pct + db.cgtmse.agf_rate_pct, 2)} costs ${cr(db.total_finance_cost)} over seven years — against ${cr(ex.equity_value * eq.stake_pct / 100, 0)} for the equivalent equity, on the company's own projections.`);
  L.foot(s, NAME);

  // 07 CCD
  s = slide(p);
  y = L.head(s, "07", "Option C · Debt converted to equity",
    "Money in as debt at a coupon, converting into equity on a fixed formula three years out. At company level — unlike at project level — this is genuinely competitive with both alternatives.");
  y = L.table(s, y, ["Term", "Structure"], [
    { cells: ["Principal", cr(cc.principal, 0)] },
    { cells: ["Coupon, annual until conversion", pc(cc.coupon_pct, 1)] },
    { cells: ["Conversion — compulsory", `End of year ${cc.conversion_year}, into ${pc(cc.conversion_stake_pct, 1)}`] },
    { cells: ["Implied conversion valuation, post-money", cr(cc.conversion_valuation_implied, 0)] },
    { cells: ["Coupon paid to conversion", cr(cc.coupon_paid_total)] },
    { cells: ["Investor IRR", pc(cc.irr_pct)], emphasis: "total" },
    { cells: ["Money multiple", `${cc.money_multiple.toFixed(2)}×`], emphasis: "total" },
  ], { colW: [8.4, L.W - 2 * L.M - 8.4], rowH: 0.32 });
  L.verdict(s, y + 0.2, "go", "The best risk-adjusted structure — with one condition",
    `${pc(cc.irr_pct)} against ${pc(eq.irr_pct)} for straight equity at the same valuation and exit. Dilution is deferred three years, and ${pc(cc.conversion_stake_pct, 1)} converted at ${cr(cc.conversion_valuation_implied, 0)} is cheaper than ${pc(eq.stake_pct, 1)} sold today at ₹90 crore pre-money.\n\nThe condition: a CCD is borrowing until it converts. Convert the related-party debt first, or agree in the sanction letter that the CGTMSE leverage covenant excludes compulsorily convertible instruments.`);
  L.foot(s, NAME);

  // 08 comparison
  s = slide(p);
  y = L.head(s, "08", "Which option, and why");
  y = L.optionCards(s, y, [
    { tag: "Option A", name: "Equity", big: pc(eq.irr_pct), cap: "Investor IRR", bigColor: C.amber, rows: [
      ["Money in", cr(eq.investment, 0)], ["Dilution", `${pc(eq.stake_pct, 1)} immediately`],
      ["Cost in FY30-31 money", cr(ex.equity_value * eq.stake_pct / 100, 0)], ["Time to close", "4–8 months"],
    ] },
    { tag: "Option B", name: "Debt · CGTMSE", big: cr(db.total_finance_cost), cap: "Total cost over 7 years",
      pick: true, bigSmall: true, bigColor: C.green, rows: [
      ["Money in", cr(db.total_limit, 0)], ["Dilution", "None"],
      ["All-in rate", pc(db.rate_pct + db.cgtmse.agf_rate_pct, 2)], ["Time to close", "6–12 weeks"],
    ] },
    { tag: "Option C", name: "Debt → equity (CCD)", big: pc(cc.irr_pct), cap: "Investor IRR", bigColor: C.green, rows: [
      ["Money in", cr(cc.principal, 0)], ["Dilution", `${pc(cc.conversion_stake_pct, 1)} in year 3`],
      ["Cost in FY30-31 money", cr(cc.coupon_paid_total + ex.equity_value * cc.conversion_stake_pct / 100, 0)],
      ["Time to close", "3–6 months"],
    ] },
  ], 3.1);
  L.verdict(s, y, "go", "All three, in sequence — not one instead of the others",
    `Step 1, now, no external party: convert all ${cr(lev.conversion_full)} of related-party and promoter debt. Gearing falls to ${xx(rpc.convert_lt_plus_promoter_409.debt_equity)}, clear the arrears, consolidate the NBFC book.  ·  Step 2, the cheap capital: a ${cr(db.total_limit, 0)} CGTMSE facility at ${pc(db.rate_pct + db.cgtmse.agf_rate_pct, 2)} all-in, ${cr(db.total_finance_cost)} total cost.  ·  Step 3, the equity, smaller and later: with the debt in place the round need not be ${cr(eq.investment, 0)} — ₹6–8 crore covers what debt cannot reach, at roughly half the dilution.`, 1.68);
  L.foot(s, NAME);

  // 09 conditions precedent
  s = slide(p);
  y = L.head(s, "09", "Conditions precedent to any lender approach");
  L.itemList(s, y, [
    { title: "Convert all ₹4.09 Cr of related-party debt", color: C.terra,
      body: "Takes D/E from 3.04× to 0.56×, and to 1.61× once drawn. Converting only the ₹2.60 Cr caps the facility at ₹8.11 Cr; converting nothing caps it at ₹0.31 Cr. Board resolution." },
    { title: "Clear the ₹2.14 Cr electricity arrears", color: C.terra,
      body: "A live utility default is the single item most likely to stop a sanction note in its tracks. Settle or formally reschedule with the discom before applying." },
    { title: "Consolidate the NBFC book", color: C.amber,
      body: "Thirteen facilities read as distress borrowing. Reduce to a countable number before applying — a lender will covenant against re-borrowing anyway." },
    { title: "Confirm Udyam registration and NIC code", color: C.amber,
      body: "CGTMSE cover requires a live registration on the correct activity code for the borrowing entity. Confirm before the application, not after a rejection." },
    { title: "Complete the FY25-26 audit", color: C.blue,
      body: "Provisional accounts carry a ₹54.5 lakh depreciation placeholder against an estimated ₹1.0–1.1 Cr. Net worth moves; EBITDA and DSCR do not. Expected August 2026." },
    { title: "Obtain BDA consent for any change of control", color: C.blue,
      body: "Ramayan Vatika's lock-in bars shareholding changes without prior written approval. Applies to the equity round and to CCD conversion alike." },
  ], { cols: 2, rowH: 1.26 });
  L.foot(s, NAME);

  return p.writeFile({ fileName: path.join(OUT, "EOD-Company-Capital-Structure.pptx") });
}

/* ================================ 5 · HUB ============================== */
function buildHub() {
  const g = M.ggv, v = M.rv, k = M.karnal, c = M.company;
  const gf = g.financing, vf = v.financing, kf = k.financing, cf = c.financing;
  const alloc = M.cgtmse_allocation, cg = M.cgtmse, consol = M.consolidated.years;
  const lev = cf.debt.leverage;
  const p = newDeck("E-O-D Project Finance — Portfolio", "Three projects, one balance sheet");
  const NAME = "E-O-D Parks · Project finance portfolio";

  const totalAsk = gf.ask + vf.facility_ask + kf.project_cost;
  const totalCap = gf.true_capital_requirement.total + vf.true_capital_requirement.total
                 + kf.true_capital_requirement.total;

  L.cover(slide(p), {
    eyebrow: "Project finance · Portfolio", title: "Three projects,\none balance sheet",
    sub: "Geeta Govind Vatika, Ramayan Vatika and Karnal, each modelled as equity, guaranteed debt, and debt that converts to equity — plus the company-level view that ties them together. Built on the ₹10 crore CGTMSE ceiling that came into force in April 2025.",
    meta: `${c.profile.name} · CIN ${c.profile.cin} · MSME classification Small Enterprise\nPrepared ${M.meta.prepared} · every figure generated from model/pf_model.py`,
    stats: [
      { label: "Total funding sought", value: cr(totalAsk, 1), sub: "Across the three projects, as briefed" },
      { label: "True capital at risk", value: cr(totalCap, 1), sub: "The balance is revolving liquidity" },
      { label: "CGTMSE ceiling", value: cr(alloc.ceiling, 0), sub: "Per borrower — the binding constraint" },
      { label: "Gross demand", value: cr(alloc.total_gross_demand, 1), sub: `${cr(alloc.excess_over_ceiling, 1)} over the ceiling` },
    ],
  });

  // 01 the three projects compared
  let s = slide(p);
  let y = L.head(s, "01", "The three projects, compared",
    "The same analysis run three times. What differs is not the method — it is how much capital each genuinely consumes, and what it earns on it.");
  y = L.table(s, y, ["", "Geeta Govind Vatika", "Ramayan Vatika", "Karnal"], [
    { cells: ["Counterparty", "Agra Dev. Authority", "Bareilly Dev. Authority", "A4A Highway Nest LLP"] },
    { cells: ["Term / lock-in", "7 + 4 yrs · none", "10 + 5 yrs · 5 years", "15 yrs · none"] },
    { cells: ["Funding sought", cr(gf.ask), cr(vf.facility_ask), cr(kf.project_cost)] },
    { cells: ["True capital at risk", cr(gf.true_capital_requirement.total), cr(vf.true_capital_requirement.total), cr(kf.true_capital_requirement.total)] },
    { cells: ["Stabilised EBITDA margin (yr 5)", pc(g.years[4].ebitda_margin), pc(v.years[4].ebitda_margin), pc(k.years[4].ebitda_margin)] },
    { cells: ["Project IRR",
        { text: pc(gf.project_fcf.irr_pct), color: C.green },
        { text: pc(vf.project_fcf.irr_pct), color: C.terra },
        { text: pc(kf.project_fcf.irr_pct), color: C.green }], emphasis: "sub" },
    { cells: ["Spread over guaranteed debt",
        { text: pp(gf.cost_of_capital.spread_over_debt_pct), color: C.green },
        { text: pp(vf.cost_of_capital.spread_over_debt_pct), color: C.terra },
        { text: pp(kf.cost_of_capital.spread_over_debt_pct), color: C.green }] },
    { cells: ["Minimum DSCR at the size asked", xx(gf.debt.min_dscr_post_moratorium), xx(vf.debt.min_dscr_post_moratorium), xx(kf.debt.min_dscr_post_moratorium)] },
    { cells: ["Assets a lender can charge", "None — ADA owns all", "None — expressly barred", "Yes — E-O-D owns fit-out"] },
    { cells: ["Equity IRR at project level", pc(gf.equity.irr_pct), pc(vf.equity.irr_pct), pc(kf.equity.irr_pct)] },
    { cells: ["Recommended instrument", "CGTMSE debt", "CGTMSE debt, at reserve", "CGTMSE debt"], emphasis: "total" },
  ], { colW: [4.0, ...Array(3).fill((L.W - 2 * L.M - 4.0) / 3)], rowH: 0.33, fontSize: 10.5 });
  L.verdict(s, y, "stop", "The same conclusion three times, for the same reason",
    "None of the three clears an equity hurdle at project level, and it is not because any is a bad project. A single park generating ₹1–2.5 crore of mature EBITDA cannot pay a 22% return on the capital it needs and leave an operator's margin. Equity works on a portfolio and a brand; it does not work one licence at a time. Two of the three out-earn guaranteed debt comfortably — fund them with it and keep the spread.", 0.98);
  L.foot(s, NAME);

  // 02 CGTMSE framework
  s = slide(p);
  y = L.head(s, "02", "The CGTMSE framework",
    "Every debt structure in this pack rests on the Credit Guarantee Fund Trust for Micro and Small Enterprises. The scheme changed materially on 1 April 2025, and the change is what makes this pack possible.");
  y = L.stats(s, y, [
    { label: "Guarantee ceiling", value: cr(cg.ceiling_per_borrower_cr * 100, 0), tint: "EDFAF4", line: C.green,
      sub: "Doubled from ₹5 Cr on 1 April 2025. Per borrower, aggregated across all lenders" },
    { label: "Coverage for a Small Enterprise", value: pc(cg.coverage_small_enterprise_pct, 0),
      sub: `Up to ${pc(cg.coverage_preferential_pct, 0)} for micro, women-owned, NER and ZED units` },
    { label: "Collateral required", value: "Nil", sub: "On the guaranteed portion. Third-party guarantee not permitted; director personal guarantee is" },
  ], { h: 1.34 });
  y = L.table(s, y, ["Parameter", "Position"], [
    { cells: ["Eligible borrowers", "Micro and small enterprises with a live Udyam registration. Amusement and recreation is a covered service activity"] },
    { cells: ["Ceiling basis", "Per borrower, across all member lending institutions — four sanctions from four banks still share one ceiling"] },
    { cells: ["Hybrid security", "Permitted — collateral on part of a facility with the remainder guaranteed. The route for exposure above the ceiling"] },
    { cells: ["Interest rate", "MLI rate not to exceed ~3% over its EBLR or MCLR. NBFC pricing for the same borrower runs 14–22%"] },
    { cells: ["Guarantee fee basis", "On the sanctioned amount in year 1; on the outstanding thereafter — an over-sanctioned, undrawn limit is expensive"] },
  ], { colW: [2.9, L.W - 2 * L.M - 2.9], rowH: 0.38, fontSize: 10.5 });
  L.verdict(s, y, "caution", "Verify before you apply, not after",
    "CGTMSE parameters are revised by circular and vary between lending institutions. These reflect the April 2025 revisions, checked against public sources in August 2026. Confirm the operative circular with the lender before relying on any number here.");
  L.foot(s, NAME);

  // 03 the ceiling problem
  s = slide(p);
  y = L.head(s, "03", "The ceiling problem",
    "The single most important structural fact in the pack, and easy to miss: the ₹10 crore ceiling is per borrower — not per project, per facility or per lender.");
  y = L.chart(s, p, y, "bar", [
    { name: "Gross demand", labels: Object.keys(alloc.gross_demand).map(x => x.replace(" — ", "\n").replace(" — ", "\n")),
      values: Object.values(alloc.gross_demand).map(x => +crN(x)) },
    { name: "Allocated within the ceiling", labels: Object.keys(alloc.gross_demand).map(x => x.replace(" — ", "\n").replace(" — ", "\n")),
      values: Object.values(alloc.single_borrower_plan).map(x => +crN(x)) },
  ], { h: 2.25, axisTitle: "₹ crore", colors: [C.terra, C.blue], extra: { catAxisLabelFontSize: 8.5 } });
  y = L.stats(s, y + 0.05, [
    { label: "Gross demand", value: cr(alloc.total_gross_demand, 1), color: C.terra,
      sub: "Adding the composite facilities from each deck plus company working capital" },
    { label: "CGTMSE ceiling", value: cr(alloc.ceiling, 0), sub: "Per borrower, across all member lending institutions" },
    { label: "To fund another way", value: cr(alloc.excess_over_ceiling, 1), tint: "FBF1EE", line: C.terra,
      sub: "Hybrid security, or the company-level equity round" },
  ], { h: 1.28 });
  L.verdict(s, y + 0.02, "note", "Routes for the residual",
    "Hybrid security is preferred — CGTMSE permits collateral on part of a facility with the balance guaranteed, needing no new entity and no consent. The company-level round covers the rest. Separate SPVs are legally available but fail the eligibility tests in both RFPs.");
  L.foot(s, NAME);

  // 04 recommended sequence
  L.closing(slide(p), {
    eyebrow: "The recommended sequence",
    headline: "Debt is the cheap capital, and it only just became available",
    body: `The ₹10 crore equity round was designed before the CGTMSE ceiling doubled and the MSME thresholds were raised, both on 1 April 2025. VAPPL is a Small Enterprise with ₹${c.msme.headroom_investment_cr.toFixed(1)} crore of investment headroom and ₹${c.msme.headroom_turnover_cr.toFixed(1)} crore of turnover headroom, and can now access ${cr(alloc.ceiling, 0)} of collateral-free guaranteed debt at ${pc(cf.debt.rate_pct + cf.debt.cgtmse.agf_rate_pct, 2)} all-in. Two of the three new projects out-earn that cost by six to seven percentage points; none out-earns an equity hurdle.`,
    steps: [
      { color: C.terra, title: "Convert the promoter debt",
        body: `All ${cr(lev.conversion_full)} of related-party and promoter debt to equity. Gearing 3.04× → ${xx(rpc(c).debt_equity)}. No cash, no third party, no permission. Without it a 2.0× covenant caps the facility at ${cr(lev.cases[0].max_facility_at_covenant)}.` },
      { color: C.blue, title: "Bank Karnal first",
        body: `A ${cr(alloc.single_borrower_plan["Karnal Phase 1 — term loan"])} CGTMSE term loan. The cleanest credit in the pack, and the sanction that establishes the track record the two concession facilities will need.` },
      { color: C.amber, title: "Bid the two concessions",
        body: `Only if each clears its walk-away price: ${lk(gf.walk_away.licence_fee_year1)} a year at Geeta Govind Vatika, ${lk(vf.walk_away.licence_fee_year1)} at Ramayan Vatika. Winning at the wrong price is worse than losing.` },
      { color: C.green, title: "Raise the equity, smaller",
        body: `With ${cr(alloc.ceiling, 0)} of guaranteed debt in place the round need not be ₹16 crore. ₹6–8 crore covers what debt cannot reach, at roughly half the dilution — or a CCD at ${pc(cf.ccd.irr_pct)} without repricing the company.` },
    ],
  });

  // 05 what still has to be verified
  s = slide(p);
  y = L.head(s, "05", "What still has to be verified",
    "These decks are a model, not a due-diligence report. Everything below is unknown, inconsistent in the source documents, or dependent on a third party — and each moves numbers.");
  L.itemList(s, y, [
    { title: "Karnal footprint", color: C.terra,
      body: "22,000 sq ft in index.html against ~6 acres in financials.html. Sizes the entire Karnal revenue thesis. Answer: the executed sub-lease." },
    { title: "Ramayan Vatika show conversion", color: C.terra,
      body: `42% assumed here against BDA's 60% — the difference between ${pc(vf.project_fcf.irr_pct)} and ${pc(v.scenarios.bda_indicative.project_irr_pct)}. Answer: BDA, on slot capacity and soft-launch footfall.` },
    { title: "Ramayan Vatika lock-in", color: C.amber,
      body: "Seven years in clause 9 against five in clause 14. A seven-year lock-in on a seven-year payback changes the risk materially. Answer: pre-bid clarification." },
    { title: "Geeta Govind Vatika show tariff", color: C.amber,
      body: "Not set in the RFP — left to be agreed with ADA. Roughly a third of GGV's revenue rests on a rate E-O-D does not control." },
    { title: "Winning licence fees", color: C.blue,
      body: "Both are competitive processes with no cap. Both models are built on assumed bids and must be re-run on award." },
    { title: "CGTMSE current circular", color: C.blue,
      body: "Fee slabs, coverage and ceiling as published April 2025. Confirm with the lending bank's MSME desk before relying on the basis points." },
  ], { cols: 2, rowH: 1.26 });
  L.foot(s, NAME);

  return p.writeFile({ fileName: path.join(OUT, "EOD-Project-Finance-Portfolio.pptx") });
}
const rpc = c => c.related_party_conversion.convert_lt_plus_promoter_409;

/* ================================= run ================================= */
(async () => {
  const jobs = [
    ["Portfolio hub", buildHub], ["Geeta Govind Vatika", buildGGV],
    ["Ramayan Vatika", buildRV], ["Karnal", buildKarnal],
    ["Company capital structure", buildCompany],
  ];
  for (const [name, fn] of jobs) {
    const file = await fn();
    const kb = (fs.statSync(file).size / 1024).toFixed(0);
    console.log(`  ${name.padEnd(28)} ${path.basename(file).padEnd(46)} ${kb} KB`);
  }
  const over = L.overflowReport();
  if (over.length) {
    console.log(`\n  ${over.length} panel(s) short of room — fix the source, do not ship clipped text:`);
    over.forEach(o => console.log(
      `    ${o.deck.split(" — ")[0].padEnd(26)} slide ${String(o.slide).padStart(2)}  short ${String(o.short).padStart(4)}"  "${o.headline}"`));
  } else {
    console.log("\n  no panel overflows");
  }
})();
