#!/usr/bin/env python3
"""
E-O-D Parks / Vision Amusement Park Pvt. Ltd.
Project-finance model engine for:
    - Geeta Govind Vatika, Agra      (ADA · 7+4 yrs · licence fee)
    - Ramayan Vatika, Bareilly       (BDA · 10+5 yrs · licence fee)
    - Karnal, NH-1 Gharaunda         (private sub-lease · 15 yrs)
    - VAPPL consolidated (company-level capital structure)

Every figure in the HTML decks under /pf-*.html is produced here.
Run:  python3 model/pf_model.py        -> writes model/pf_model.json
All money in INR lakh unless a name ends in _cr.
"""

import json, math, os

L = 1.0          # 1 unit == INR 1 lakh
CR = 100.0       # 1 crore == 100 lakh

# ----------------------------------------------------------------------------
# CGTMSE — Credit Guarantee Fund Trust for Micro and Small Enterprises
# Credit Guarantee Scheme I (CGS-I), parameters effective 01 April 2025.
# Sources: CGTMSE circulars; Union Budget 2025-26 ceiling enhancement.
# ----------------------------------------------------------------------------
CGTMSE = {
    "scheme": "CGS-I",
    "ceiling_per_borrower_cr": 10.0,       # raised from Rs 5 Cr w.e.f. 01-Apr-2025
    "ceiling_startup_dpiit_cr": 20.0,
    "ceiling_basis": "per borrower, aggregated across all member lending institutions",
    "coverage_small_enterprise_pct": 75.0, # standard cover for a Small Enterprise
    "coverage_preferential_pct": 85.0,     # women / SC-ST / NER / Aspirational District / ZED
    "interest_cap_note": "MLI rate not to exceed ~3% over its EBLR/MCLR",
    "agf_slabs": [                          # (upper bound in lakh, standard AGF % p.a.)
        (10,    0.37),
        (50,    0.55),
        (100,   0.60),
        (200,   0.85),
        (500,   1.00),
        (800,   1.10),
        (1000,  1.20),
    ],
    "agf_basis_y1": "sanctioned amount",
    "agf_basis_y2plus": "outstanding principal at start of the year",
    "agf_concession_pct": 10.0,            # women / SC-ST / NER / Aspirational Dist / ZED
    "hybrid_security": True,
    "collateral": "nil on the guaranteed portion",
    "third_party_guarantee": "not permitted; personal guarantee of directors is permitted",
}

# Scenario multipliers applied to every project build. Reset between runs.
SCEN = {"footfall": 1.0, "yield": 1.0, "opex": 1.0, "licence": 1.0}

def agf_rate(sanctioned_lakh):
    """Standard CGTMSE annual guarantee fee rate for a facility size, % p.a."""
    for cap, rate in CGTMSE["agf_slabs"]:
        if sanctioned_lakh <= cap:
            return rate
    return CGTMSE["agf_slabs"][-1][1]

# ----------------------------------------------------------------------------
# MSME classification (Udyam), thresholds revised w.e.f. 01 April 2025
# ----------------------------------------------------------------------------
MSME_LIMITS = {
    "micro":  {"investment_cr": 2.5,  "turnover_cr": 10.0},
    "small":  {"investment_cr": 25.0, "turnover_cr": 100.0},
    "medium": {"investment_cr": 125.0,"turnover_cr": 500.0},
}

def msme_class(investment_cr, turnover_cr):
    for name in ("micro", "small", "medium"):
        lim = MSME_LIMITS[name]
        if investment_cr <= lim["investment_cr"] and turnover_cr <= lim["turnover_cr"]:
            return name
    return "beyond_msme"

# ----------------------------------------------------------------------------
# Generic finance helpers
# ----------------------------------------------------------------------------
def npv(rate, flows):
    return sum(f / (1 + rate) ** i for i, f in enumerate(flows))

def irr(flows, lo=-0.95, hi=5.0, tol=1e-7):
    """Bisection IRR. flows[0] is t=0. Returns None if no sign change."""
    def f(r): return npv(r, flows)
    a, b = lo, hi
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return None
    for _ in range(400):
        m = (a + b) / 2
        fm = f(m)
        if abs(fm) < tol:
            return m
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return (a + b) / 2

def payback_year(flows):
    """Years (fractional) until cumulative flow turns positive. flows[0] = t0 outflow."""
    cum = 0.0
    for i, f in enumerate(flows):
        prev = cum
        cum += f
        if cum >= 0 and i > 0:
            return i - 1 + (abs(prev) / f if f else 0)
    return None

def amortise(principal, rate_pa, tenor_years, moratorium_years,
             guarantee_fee_rate=None, agf_concession=0.0):
    """
    Equal-principal term loan with an interest-serviced moratorium.
    Returns a per-year schedule (year 1..tenor) of opening / interest / AGF /
    principal / closing / total debt service.  All in lakh.
    """
    repay_years = tenor_years - moratorium_years
    per = principal / repay_years if repay_years > 0 else 0.0
    rows, opening = [], principal
    for y in range(1, tenor_years + 1):
        interest = opening * rate_pa
        if guarantee_fee_rate is None:
            agf = 0.0
        else:
            base = principal if y == 1 else opening
            agf = base * (guarantee_fee_rate / 100.0) * (1 - agf_concession / 100.0)
        princ = 0.0 if y <= moratorium_years else per
        closing = opening - princ
        rows.append({
            "year": y, "opening": opening, "interest": interest, "agf": agf,
            "principal": princ, "closing": closing,
            "debt_service": interest + agf + princ,
        })
        opening = closing
    return rows

def dscr_series(cfads, schedule):
    """Cash available for debt service / debt service, per year."""
    out = []
    for i, row in enumerate(schedule):
        ds = row["debt_service"]
        c = cfads[i] if i < len(cfads) else 0.0
        out.append({"year": row["year"], "cfads": c, "debt_service": ds,
                    "dscr": (c / ds) if ds else None})
    return out

def straight_line_dep(capex_blocks):
    """capex_blocks: list of (amount_lakh, useful_life_years) -> annual depreciation."""
    return sum(a / l for a, l in capex_blocks)

# ============================================================================
# PROJECT 1 — GEETA GOVIND VATIKA, AGRA (Agra Development Authority)
# ============================================================================
GGV_RFP = {
    "authority": "Agra Development Authority (ADA)",
    "site": "Geeta Govind Vatika (formerly Zonal Park), Taj Nagri Phase-II, Agra 282004",
    "area_acres": 19,
    "term": "7 years + 4 years extendable (performance + mutual consent)",
    "selection": "Technical evaluation, then forward e-auction on licence fee",
    "reserve_licence_fee_month_lakh": 2.5,
    "reserve_licence_fee_year_lakh": 30.0,
    "escalation_pct": 5.0,
    "emd_lakh": 1.0,
    "tender_fee_lakh": 0.059,
    "security_deposit_basis": "3 months of the licence fee at the winning e-auction bid",
    "payment_terms": "First 6 months in advance within 7 days of Work Order; thereafter half-yearly in advance",
    "moratorium_days": 15,
    "entry_tariff_inr": 20,
    "free_entry": "children under 5; morning walkers 05:00-08:00 summer / 06:00-09:00 winter",
    "show_tariff": "Musical Fountain & Laser Show at rates approved by ADA",
    "penalty_range_inr": "\u20b95,000 to \u20b950,000 per violation; liquidated damages capped at 10% of total remittance",
    "eligibility_turnover_cr": 1.0,
    "eligibility_projects": "2 similar projects in last 5 years, each >= ₹50 lakh",
    "assets": "ADA owns all assets. No permanent structures permitted. Electricity paid direct to discom.",
    "scope": ["Musical fountains O&M", "40-min Krishna Leela laser show O&M (content not to be altered)",
              "6 kiosks 8x8 ft + 2 kiosks 10x10 ft (ready-to-eat + tea/coffee only, no cooking)",
              "Parking", "Horticulture over 19 acres", "Ticket counter",
              "Additional entertainment activities", "Private events, photo and pre-wedding shoots"],
}

GGV_BID_LICENCE_YEAR_1 = 36.0     # base case: Rs 3.0 lakh/month, 20% over the Rs 2.5 lakh reserve

# Footfall in lakh visits per licence year
GGV_FOOTFALL = [3.75, 4.35, 4.75, 5.05, 5.30, 5.55, 5.80]

def ggv_revenue(year_idx):
    """Bottom-up revenue for licence year (1-indexed), in lakh, net of GST."""
    y = year_idx - 1
    f = GGV_FOOTFALL[y] * SCEN["footfall"]

    # tariffs quoted gross of GST; net realisation applies the blended GST rate
    entry_gross, entry_gst = 20.0, 0.18
    show_gross_by_year = [100, 100, 110, 110, 120, 120, 130]     # ADA-approved, reviewed periodically
    show_gst = 0.18
    fnb_spend_by_year  = [35, 36, 38, 40, 42, 44, 46]
    fnb_gst = 0.12
    act_spend_by_year  = [120, 130, 140, 150, 160, 170, 180]
    act_gst = 0.18

    paid_entry_ratio = [0.76, 0.77, 0.78, 0.78, 0.79, 0.79, 0.80][y]
    fnb_capture      = [0.32, 0.34, 0.35, 0.36, 0.37, 0.38, 0.38][y]
    # Show conversion steps up in year 4: the year-3 reinvestment adds a second
    # show, so an evening visit has two ticketed reasons to stay rather than one.
    show_conv        = [0.24, 0.26, 0.28, 0.34, 0.36, 0.37, 0.38][y] * SCEN["yield"]
    # More operators are signed from year 2 as the site proves its footfall, so a
    # larger share of visitors finds an activity they want.
    act_capture      = [0.11, 0.15, 0.17, 0.20, 0.21, 0.22, 0.22][y]

    entry = f * paid_entry_ratio * entry_gross / (1 + entry_gst)
    show  = f * show_conv * show_gross_by_year[y] / (1 + show_gst)
    fnb   = f * fnb_capture * fnb_spend_by_year[y] / (1 + fnb_gst)

    # Visitor spend at the activity layer, before it is split with the operators.
    act_gross = f * act_capture * act_spend_by_year[y] / (1 + act_gst)
    # Everything is vendor-run until the year-3 reinvestment. From year 4 E-O-D
    # owns part of the layer, so it books that part gross and carries its cost.
    owned = GGV_ACTIVITY_OWNED_FRACTION[y]
    act = (act_gross * (1 - owned) * GGV_ACTIVITY_REVENUE_SHARE) + (act_gross * owned)

    vehicles = f / 3.1
    park_gross = vehicles * (0.62 * 10 + 0.38 * 20)
    parking = park_gross / 1.18

    # Ticketed community events and E-O-D's own IPs. Year 1 builds the audience
    # through programming rather than through price.
    events_public = [32.0, 38.0, 43.0, 49.0, 54.0, 58.0, 62.0][y]
    # Weddings, corporate offsites, birthdays, pre-wedding and film shoots. This is
    # the line the Agra Chaupati adjacency and the year-3 show build most affect.
    events_private = [18.0, 24.0, 29.0, 37.0, 42.0, 46.0, 50.0][y]

    return {"entry": entry, "show": show, "fnb": fnb,
            "activities": act, "activities_gross": act_gross, "activities_owned_frac": owned,
            "parking": parking,
            "events_public": events_public, "events_private": events_private,
            "events": events_public + events_private,
            "total": entry + show + fnb + act + parking + events_public + events_private,
            "footfall_lakh": f}

def ggv_opex(year_idx, rev, licence_year_1=GGV_BID_LICENCE_YEAR_1):
    """Opex scales on three drivers: contracted escalation, cost inflation, and footfall."""
    y = year_idx - 1
    licence = licence_year_1 * SCEN["licence"] * (1.05 ** y)
    infl = 1.065 ** y                                     # 6.5% cost inflation
    scale = 1 + 0.35 * (rev["footfall_lakh"] / GGV_FOOTFALL[0] - 1)   # staffing/consumables load
    manpower   = 70.4 * (1.07 ** y) * scale               # 31 heads at year-1 footfall
    electricity= 26.0 * infl * (1 + 0.25 * (scale - 1))
    water_hort = 9.0 * infl                               # fixed to the 19-acre area
    show_amc   = 14.0 * infl
    rm         = 8.0 * infl * scale
    fnb_cogs   = 0.44 * rev["fnb"]   # supplied from the EAC kitchens, not bought in
    # Vendor-run activities cost E-O-D nothing. The owned part, from year 4, carries
    # manning, power and consumables at 35% of what it takes.
    act_cost   = rev["activities_gross"] * rev["activities_owned_frac"] * GGV_OWNED_ACTIVITY_COST_RATIO
    # Cost of delivering the events themselves. Public IPs carry artists, production
    # and permissions; private bookings carry incremental manning, power and
    # housekeeping only, because the client brings its own caterer and decorator.
    events_cost = (GGV_PUBLIC_EVENT_COST_RATIO * rev["events_public"] +
                   GGV_PRIVATE_EVENT_COST_RATIO * rev["events_private"])
    marketing  = [0.075, 0.065, 0.055, 0.050, 0.045, 0.045, 0.045][y] * rev["total"]
    insurance  = 5.0 * infl
    it_cctv    = 3.5 * infl
    overhead   = 0.050 * rev["total"]                     # Agra cluster allocation (shared with EAC/ESP)
    contingency= 3.0 * infl                               # ADA penalty provision
    total = (licence + manpower + electricity + water_hort + show_amc + rm +
             fnb_cogs + act_cost + events_cost + marketing + insurance + it_cctv +
             overhead + contingency)
    total *= SCEN["opex"]
    return {"licence_fee": licence, "manpower": manpower, "electricity": electricity,
            "water_horticulture": water_hort, "show_amc": show_amc, "repairs": rm,
            "fnb_cogs": fnb_cogs, "activity_cost": act_cost, "events_cost": events_cost,
            "marketing": marketing,
            "insurance_statutory": insurance, "it_cctv": it_cctv,
            "corporate_overhead": overhead, "contingency": contingency, "total": total}

# Nothing at mobilisation is an attraction. Every activity on site at opening is
# brought in by an operator on rent or revenue share, so none of it is funded by
# the facility and none of it appears here.
GGV_CAPEX = [
    ("Kiosk counters, common seating, shade structures", 8.0, 7),
    ("Ticketing, POS and CCTV", 6.0, 5),
    ("Horticulture equipment, tools, uniforms, safety kit", 8.0, 5),
    ("Signage, branding, wayfinding", 5.0, 5),
    ("Pre-operative and contingency", 3.0, 5),
]

# Vendor-run activities pay E-O-D a share of their takings, not the gross spend.
GGV_ACTIVITY_REVENUE_SHARE = 0.20

# Reinvestment out of operating cash at the end of year 3 — no new facility, no
# equity. It is discretionary and deferrable, which is why it sits below the debt
# service line and does not touch the coverage ratios.
GGV_GROWTH_CAPEX_YEAR = 3
GGV_GROWTH_CAPEX = [
    ("Second laser and projection show", 26.0, 7),
    ("Owned activity installations, demountable", 14.0, 5),
]
# Share of the activity layer E-O-D owns and operates itself once that build is
# commissioned. The rest stays with the operators on revenue share.
GGV_ACTIVITY_OWNED_FRACTION = [0.0, 0.0, 0.0, 0.30, 0.32, 0.34, 0.36]
GGV_OWNED_ACTIVITY_COST_RATIO = 0.35

# Cost of putting the events on, counting only what is genuinely incremental.
# Manning, power, housekeeping and security are already carried in their own
# lines and are not charged again here. What is left is artists, external stage
# and sound hire, and permissions for a public IP; for a private booking, little
# more than consumables, because the client's own caterer and decorator do the
# rest and a shoot is a location fee against a site that is already staffed.
GGV_PUBLIC_EVENT_COST_RATIO = 0.20
GGV_PRIVATE_EVENT_COST_RATIO = 0.10

def build_ggv():
    years = []
    dep = straight_line_dep([(a, l) for _, a, l in GGV_CAPEX])
    # The year-3 build is commissioned at the end of that year, so it starts
    # depreciating — and starts earning — in year 4.
    growth_dep = straight_line_dep([(a, l) for _, a, l in GGV_GROWTH_CAPEX])
    for i in range(1, 8):
        rev = ggv_revenue(i)
        op = ggv_opex(i, rev)
        ebitda = rev["total"] - op["total"]
        dep_i = dep + (growth_dep if i > GGV_GROWTH_CAPEX_YEAR else 0.0)
        growth_capex = sum(a for _, a, _ in GGV_GROWTH_CAPEX) if i == GGV_GROWTH_CAPEX_YEAR else 0.0
        years.append({"year": i, "revenue": rev, "opex": op, "ebitda": ebitda,
                      "ebitda_margin": ebitda / rev["total"] * 100,
                      "depreciation": dep_i, "ebit": ebitda - dep_i,
                      "growth_capex": growth_capex})
    capex_total = sum(a for _, a, _ in GGV_CAPEX)
    sec_dep = GGV_BID_LICENCE_YEAR_1 / 4                     # 3 months of licence fee
    adv_licence = GGV_BID_LICENCE_YEAR_1 / 2                 # first 6 months in advance
    mobilisation = {
        "capex": capex_total,
        "security_deposit": sec_dep,
        "advance_licence_fee_6m": adv_licence,
        "emd": GGV_RFP["emd_lakh"],
        "tender_fee": GGV_RFP["tender_fee_lakh"],
        "total": capex_total + sec_dep + adv_licence + GGV_RFP["emd_lakh"] + GGV_RFP["tender_fee_lakh"],
    }
    year1_opex = years[0]["opex"]["total"]
    ask = 100.0                                     # Rs 1 crore
    mobilisation["working_capital"] = ask - mobilisation["total"]
    mobilisation["ask"] = ask
    peak_deficit = mobilisation["total"] + max(0.0, -years[0]["ebitda"])
    return {"rfp": GGV_RFP, "bid_licence_year1": GGV_BID_LICENCE_YEAR_1,
            "capex_lines": [{"item": n, "amount": a, "life_years": l} for n, a, l in GGV_CAPEX],
            "mobilisation": mobilisation, "years": years,
            "year1_opex": year1_opex, "funding_ask": ask,
            "peak_cash_deficit": peak_deficit, "annual_depreciation": dep,
            "cost_ratios": {
                "public_event_delivery_pct": GGV_PUBLIC_EVENT_COST_RATIO * 100,
                "private_event_delivery_pct": GGV_PRIVATE_EVENT_COST_RATIO * 100,
                "fnb_cogs_pct": 44.0,
            },
            "growth_capex": {
                "year": GGV_GROWTH_CAPEX_YEAR,
                "lines": [{"item": n, "amount": a, "life_years": l} for n, a, l in GGV_GROWTH_CAPEX],
                "total": sum(a for _, a, _ in GGV_GROWTH_CAPEX),
                "annual_depreciation": growth_dep,
                "owned_activity_fraction_pct": [x * 100 for x in GGV_ACTIVITY_OWNED_FRACTION],
                "owned_activity_cost_ratio_pct": GGV_OWNED_ACTIVITY_COST_RATIO * 100,
            }}

# ============================================================================
# PROJECT 2 — RAMAYAN VATIKA, BAREILLY (Bareilly Development Authority)
# ============================================================================
RV_RFP = {
    "authority": "Bareilly Development Authority (BDA)",
    "site": "Ramayan Vatika, Sector-2, Ramganga Nagar, Bareilly",
    "area_sqm": 33000,
    "area_acres": 8.15,
    "term": "10 years + 5 years extendable",
    "lock_in": "5 years in the initial term; 2 years in the extended term",
    "lock_in_conflict": ("Clause 9 of the Key Terms states a 7-year lock-in while Clause 14 and the "
                         "Lock-in section state 5 years. To be resolved by pre-bid clarification."),
    "selection": "Technically qualified + financially H1 (highest annual licence fee), sealed bid, with presentation",
    "reserve_licence_fee_year_lakh": 30.0,
    "escalation_pct": 5.0,
    "payment_terms": "Quarterly in advance (₹7.5 lakh at reserve) by the 10th of the first month of each quarter",
    "penal_interest": "1% per month / 12% p.a. on delayed licence fee",
    "emd_lakh": 3.0,
    "bid_fee_lakh": 0.15,
    "performance_security_lakh": 30.0,
    "performance_security_note": "Interest-free, valid until 3 months after the completion period",
    "mortgage_prohibition": ("The Vatika, wholly or partially, shall not be mortgaged, pledged, hypothecated "
                             "or offered as security to any bank, FI, NBFC or third party."),
    "shareholding_restriction": ("No change in ownership pattern, shareholding structure or controlling interest "
                                 "during the lock-in without BDA's prior written approval."),
    "min_manpower": {"per_shift": {"sweepers": 4, "security": 5},
                     "per_day": {"mali_gardener": 8, "site_manager": 1, "electrician": 1, "plumber": 1}},
    "statutory": "EPF and ESI mandatory for all deployed staff; agreement compulsorily registered, stamp duty on operator",
    "bda_free_use_days": 10,
    "bda_indicative_revenue_cr": [2.25, 2.30],
    "bda_indicative_basis": "500 visitors/day; 300/day paying ₹125 for the show (60% conversion)",
    "assets": ["51-ft bronze Lord Ram statue by Ram Sutar", "3D holographic laser and sound show projected on the statue",
               "Six thematic vatikas (Ashoka, Kishkindha, Dronagiri, Panchvati, Dandakaranya, Chitrakoot)",
               "Miyawaki forest of ~16,000 trees", "Open-air theatre", "Shabri Ashram",
               "Marble statues, murals and fibre panels", "Food court", "Parking"],
    "revenue_streams": ["Entry ticketing", "Toy train (optional, future)", "Food court and vendor rentals",
                        "Parking", "Cultural events, Ram Katha, laser shows", "Souvenirs and merchandise",
                        "Photography charges", "Theme-consistent advertising", "School and educational packages"],
    "tech_score": {"experience": 30, "financial_strength": 20, "manpower": 20,
                   "om_plan": 15, "technology": 15},
}

RV_BID_LICENCE_YEAR_1 = 33.0      # base case: 10% over the Rs 30 lakh reserve (sealed H1 bid)
RV_YEARS = 10

RV_FOOTFALL = [1.65, 2.15, 2.55, 2.85, 3.10, 3.30, 3.45, 3.60, 3.72, 3.85]

def rv_revenue(year_idx):
    y = year_idx - 1
    f = RV_FOOTFALL[y] * SCEN["footfall"]

    entry_gross_by_year = [22, 22, 25, 25, 28, 28, 30, 30, 33, 33]
    # BDA caps tariffs for affordability: escalation is modelled well below inflation
    show_gross_by_year  = [150, 150, 160, 160, 165, 165, 175, 175, 185, 185]
    paid_ratio  = [0.80, 0.80, 0.81, 0.81, 0.82, 0.82, 0.82, 0.83, 0.83, 0.83][y]
    show_conv   = [0.42, 0.44, 0.46, 0.47, 0.48, 0.49, 0.50, 0.51, 0.51, 0.52][y] * SCEN["yield"]

    entry = f * paid_ratio * entry_gross_by_year[y] / 1.18
    show  = f * show_conv * show_gross_by_year[y] / 1.18

    # food court: 4 stalls on lease + directly operated outlets
    fnb = [16.0, 20.0, 24.0, 27.0, 30.0, 33.0, 35.0, 37.0, 39.0, 41.0][y]

    vehicles = f / 3.0
    parking = vehicles * (0.70 * 10 + 0.30 * 30) / 1.18

    events   = [11.0, 15.0, 19.0, 22.0, 25.0, 27.0, 29.0, 31.0, 33.0, 35.0][y]
    ancillary= [7.0, 10.0, 13.0, 15.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0][y]   # souvenirs, photo, school, advertising
    toy_train= [0.0, 9.0, 12.0, 14.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0][y]    # commissioned in year 2

    total = entry + show + fnb + parking + events + ancillary + toy_train
    return {"entry": entry, "show": show, "fnb": fnb, "parking": parking,
            "events": events, "ancillary": ancillary, "toy_train": toy_train,
            "total": total, "footfall_lakh": f}

def rv_opex(year_idx, rev, licence_year_1=RV_BID_LICENCE_YEAR_1):
    y = year_idx - 1
    licence = licence_year_1 * SCEN["licence"] * (1.05 ** y)
    infl = 1.065 ** y
    scale = 1 + 0.30 * (rev["footfall_lakh"] / RV_FOOTFALL[0] - 1)
    manpower    = 66.0 * (1.07 ** y) * scale   # 37 heads at Bareilly rates incl. the BDA-mandated
                                           # minimum, loaded for EPF and ESI
    electricity = 22.0 * infl * (1 + 0.25 * (scale - 1))
    water_cons  = 5.0 * infl
    horticulture= 11.0 * infl                  # Miyawaki forest + six vatikas + lawns
    show_amc    = 14.0 * infl                  # 3D holographic, laser, sound
    statue_upkeep = 7.0 * infl                 # polishing, painting, restoration per RFP clause 1
    rm          = 9.0 * infl * scale
    insurance   = 6.0 * infl                   # property, fire, public liability, third-party
    marketing   = 0.045 * rev["total"]
    fnb_cogs    = 0.22 * rev["fnb"]
    it_cctv     = 3.0 * infl
    overhead    = 0.040 * rev["total"]
    contingency = 3.0 * infl
    total = (licence + manpower + electricity + water_cons + horticulture + show_amc +
             statue_upkeep + rm + insurance + marketing + fnb_cogs + it_cctv + overhead + contingency)
    total *= SCEN["opex"]
    return {"licence_fee": licence, "manpower": manpower, "electricity": electricity,
            "water_consumables": water_cons, "horticulture": horticulture, "show_amc": show_amc,
            "statue_upkeep": statue_upkeep, "repairs": rm, "insurance": insurance,
            "marketing": marketing, "fnb_cogs": fnb_cogs, "it_cctv": it_cctv,
            "corporate_overhead": overhead, "contingency": contingency, "total": total}

RV_CAPEX = [
    ("Computerised ticketing, POS, access control, CCTV", 22.0, 5),
    ("Food court fit-out, seating, shade and kitchen equipment", 26.0, 7),
    ("Theme-consistent activity and children's zone equipment (BDA approval required)", 30.0, 8),
    ("Toy train and track (year 2 — optional revenue stream)", 38.0, 10),
    ("Signage, wayfinding, thematic branding", 8.0, 5),
    ("Housekeeping, horticulture and safety equipment", 7.0, 3),
    ("Pre-operative, mobilisation and contingency", 9.0, 5),
]

def build_rv():
    years = []
    dep_immediate = straight_line_dep([(a, l) for n, a, l in RV_CAPEX if "Toy train" not in n])
    dep_full = straight_line_dep([(a, l) for _, a, l in RV_CAPEX])
    for i in range(1, RV_YEARS + 1):
        rev = rv_revenue(i)
        op = rv_opex(i, rev)
        ebitda = rev["total"] - op["total"]
        dep = dep_immediate if i == 1 else dep_full
        years.append({"year": i, "revenue": rev, "opex": op, "ebitda": ebitda,
                      "ebitda_margin": ebitda / rev["total"] * 100,
                      "depreciation": dep, "ebit": ebitda - dep})
    capex_y0 = sum(a for n, a, _ in RV_CAPEX if "Toy train" not in n)
    capex_y2 = sum(a for n, a, _ in RV_CAPEX if "Toy train" in n)
    stamp_duty = 8.0
    q1_licence = RV_BID_LICENCE_YEAR_1 / 4
    mobilisation = {
        "capex_year0": capex_y0,
        "capex_year2_toy_train": capex_y2,
        "performance_security": RV_RFP["performance_security_lakh"],
        "emd": RV_RFP["emd_lakh"],
        "bid_fee": RV_RFP["bid_fee_lakh"],
        "stamp_duty_registration": stamp_duty,
        "advance_licence_fee_q1": q1_licence,
        "total": capex_y0 + RV_RFP["performance_security_lakh"] + RV_RFP["emd_lakh"] +
                 RV_RFP["bid_fee_lakh"] + stamp_duty + q1_licence,
    }
    opex_y1, opex_y2 = years[0]["opex"]["total"], years[1]["opex"]["total"]
    two_year_opex = opex_y1 + opex_y2
    # net drawdown: mobilisation + year-2 capex + cumulative EBITDA deficit while negative
    cum, peak = 0.0, 0.0
    cum += mobilisation["total"]
    peak = cum
    for i, yr in enumerate(years):
        cum += -yr["ebitda"]
        if i == 1:
            cum += capex_y2
        peak = max(peak, cum)
        if yr["ebitda"] > 0 and cum < peak:
            pass
    return {"rfp": RV_RFP, "bid_licence_year1": RV_BID_LICENCE_YEAR_1,
            "capex_lines": [{"item": n, "amount": a, "life_years": l} for n, a, l in RV_CAPEX],
            "mobilisation": mobilisation, "years": years,
            "opex_year1": opex_y1, "opex_year2": opex_y2,
            "two_year_opex": two_year_opex,
            "facility_ask": two_year_opex,
            "net_drawdown_requirement": peak,
            "annual_depreciation_full": dep_full}

# ============================================================================
# PROJECT 3 — KARNAL, NH-1 GHARAUNDA (private sub-lease, A4A Highway Nest LLP)
# ============================================================================
KARNAL_FACTS = {
    "site": "NH-1 Milestone 109, Gharaunda, Karnal (Delhi-Amritsar highway)",
    "counterparty": "Sub-lease with A4A Highway Nest LLP",
    "area_sqft": 22000,
    "term_years": 15,
    "minimum_guarantee_month_lakh": [2.0, 3.0],
    "rent_free": "Long rent-free build period",
    "status": "Signed. Build-out is raise-dependent.",
    "phase1_capex_cr": 4.0,
    "build_months": 12,
    "open_estimate": "September 2027",
    "deck_revenue_fy2728_cr": [0.50, 1.00],
    "deck_revenue_fy2829_cr": [3.00, 4.00],
    "area_discrepancy": ("index.html records ~22,000 sq ft; the Karnal assumption block in financials.html "
                         "reads '~6 acres'. The two are not reconcilable and the footprint drives the "
                         "revenue ceiling. To be confirmed against the signed sub-lease before this model is bid."),
}

KARNAL_CAPEX = [
    ("Civil, site development, utilities, drainage", 130.0, 15),
    ("Activity equipment — go-kart, zipline, obstacle course, soft play, arcade", 190.0, 10),
    ("F&B outlet fit-out and kitchen equipment", 35.0, 7),
    ("Ticketing, POS, CCTV, IT infrastructure", 15.0, 5),
    ("Highway signage, branding, wayfinding", 12.0, 5),
    ("Pre-operative, mobilisation and contingency", 18.0, 5),
]

KARNAL_YEARS = 10
KARNAL_REVENUE = [75.0, 325.0, 400.0, 460.0, 510.0, 550.0, 588.0, 625.0, 660.0, 695.0]
KARNAL_MG_YEAR_1 = 30.0    # Rs 2.5 lakh/month minimum guarantee, from opening

def karnal_opex(year_idx, revenue):
    y = year_idx - 1
    part_year = 0.5 if year_idx == 1 else 1.0      # year 1 is a half-year stub (H2 FY27-28)
    infl = 1.065 ** max(0, y)
    mg          = KARNAL_MG_YEAR_1 * (1.05 ** max(0, y - 1)) * part_year
    manpower    = 78.0 * (1.07 ** max(0, y - 1)) * part_year
    electricity = 20.0 * infl * part_year
    activity    = 28.0 * infl * part_year
    rm          = 14.0 * infl * part_year
    marketing   = 18.0 * infl * part_year
    admin       = 18.0 * infl * part_year
    insurance   = 4.0 * infl * part_year
    fnb_cogs    = 0.11 * revenue
    total = (mg + manpower + electricity + activity + rm + marketing + admin + insurance + fnb_cogs) * SCEN["opex"]
    return {"minimum_guarantee": mg, "manpower": manpower, "electricity": electricity,
            "activity_consumables_amc": activity, "repairs": rm, "marketing": marketing,
            "admin_overhead": admin, "insurance_statutory": insurance, "fnb_cogs": fnb_cogs,
            "total": total}

def build_karnal():
    dep = straight_line_dep([(a, l) for _, a, l in KARNAL_CAPEX])
    years = []
    for i in range(1, KARNAL_YEARS + 1):
        rev = KARNAL_REVENUE[i - 1] * SCEN["footfall"] * SCEN["yield"]
        op = karnal_opex(i, rev)
        ebitda = rev - op["total"]
        d = dep * (0.5 if i == 1 else 1.0)
        years.append({"year": i, "revenue": rev, "opex": op, "ebitda": ebitda,
                      "ebitda_margin": ebitda / rev * 100, "depreciation": d,
                      "ebit": ebitda - d})
    capex_total = sum(a for _, a, _ in KARNAL_CAPEX)
    return {"facts": KARNAL_FACTS,
            "capex_lines": [{"item": n, "amount": a, "life_years": l} for n, a, l in KARNAL_CAPEX],
            "capex_total": capex_total, "years": years, "annual_depreciation": dep}

# ============================================================================
# COMPANY — VISION AMUSEMENT PARK PVT. LTD.
# ============================================================================
COMPANY = {
    "name": "Vision Amusement Park Pvt. Ltd.",
    "cin": "U93000DL2011PTC212814",
    "share_capital_lakh": 2.0,
    "shares_outstanding": 20000,
    "face_value_inr": 10,
    "fy26": {
        "revenue": 1629.0, "ebitda": 237.0, "pat": 66.0,
        "net_worth": 258.0, "reserves": 256.0,
        "borrowings_short": 526.0, "borrowings_long_related": 260.0, "borrowings_total": 785.0,
        "cash": 140.0, "fdr": 222.0, "gross_block": 613.0, "net_block": 580.0,
        "electricity_arrears": 214.0, "finance_cost_total": 71.0,
        "trade_payables": 4.0, "other_current_liabilities": 209.0,
    },
    "promoter_related_debt": {
        "sanjeev_bewtra_and_team_buildcon_lt": 260.0,
        "promoter_loans_fy26": 76.6,
        "apoorv_babbar_huf": 59.5,
        "geetika_jain": 13.0,
    },
    "projections": {   # midpoints of the ranges published in financials.html
        "FY26-27": {"revenue": 2400.0, "ebitda": 550.0, "pat": 300.0},
        "FY27-28": {"revenue": 3300.0, "ebitda": 800.0, "pat": 525.0},
        "FY28-29": {"revenue": 4350.0, "ebitda": 1200.0, "pat": 800.0},
    },
    "existing_raise": {"amount_cr": 10.0, "pre_money_cr": 90.0, "dilution_pct": 10.0},
}

def company_msme_status():
    inv_cr = COMPANY["fy26"]["gross_block"] / CR
    to_cr = COMPANY["fy26"]["revenue"] / CR
    return {"investment_plant_machinery_cr": inv_cr, "turnover_cr": to_cr,
            "classification": msme_class(inv_cr, to_cr),
            "headroom_investment_cr": MSME_LIMITS["small"]["investment_cr"] - inv_cr,
            "headroom_turnover_cr": MSME_LIMITS["small"]["turnover_cr"] - to_cr,
            "cgtmse_eligible": msme_class(inv_cr, to_cr) in ("micro", "small")}

def related_party_conversion():
    """Effect of converting related-party / promoter debt into equity."""
    fy = COMPANY["fy26"]
    base_de = fy["borrowings_total"] / fy["net_worth"]
    out = {"base": {"borrowings": fy["borrowings_total"], "net_worth": fy["net_worth"],
                    "debt_equity": base_de}}
    for label, amt in [("convert_lt_related_260", 260.0),
                       ("convert_lt_plus_promoter_409", 260.0 + 76.6 + 59.5 + 13.0)]:
        b = fy["borrowings_total"] - amt
        nw = fy["net_worth"] + amt
        out[label] = {"converted": amt, "borrowings": b, "net_worth": nw,
                      "debt_equity": b / nw}
    return out


# ============================================================================
# FINANCING STRUCTURES
# ============================================================================
# A licence-fee O&M concession consumes very little capital: the mobilisation
# spend plus deposits is the only true project cost. The much larger "one year"
# or "two years" of operating expenditure is a LIQUIDITY requirement, funded by
# a revolving working-capital limit and repaid out of collections, not a capital
# requirement funded by term money. Every structure below is built on that split:
#     Term loan       -> mobilisation capex, deposits, advance licence fee
#     Working capital -> the opex facility (interest-serviced, revolving)
# ----------------------------------------------------------------------------

CORPORATE_TAX = 0.25          # 25% effective (new-regime 22% + surcharge and cess)

def composite_facility(term_loan, wc_limit, wc_utilisation, rate, tl_tenor,
                       tl_moratorium, cfads, label, coverage_pct=None):
    """
    CGTMSE-covered composite facility: an amortising term loan plus a revolving
    working-capital limit. AGF is charged on the aggregate guaranteed exposure.
    wc_utilisation: average drawn balance on the WC limit, per year.
    """
    coverage_pct = coverage_pct or CGTMSE["coverage_small_enterprise_pct"]
    total_limit = term_loan + wc_limit
    rate_agf = agf_rate(total_limit)

    repay_years = tl_tenor - tl_moratorium
    per = term_loan / repay_years if repay_years > 0 else 0.0
    rows, opening = [], term_loan
    for y in range(1, tl_tenor + 1):
        wc_out = wc_utilisation[y - 1] if y - 1 < len(wc_utilisation) else 0.0
        tl_interest = opening * rate
        wc_interest = wc_out * rate
        exposure = (total_limit if y == 1 else opening + wc_out)
        agf = exposure * rate_agf / 100.0
        princ = 0.0 if y <= tl_moratorium else per
        closing = opening - princ
        ds = tl_interest + wc_interest + agf + princ
        c = cfads[y - 1] if y - 1 < len(cfads) else 0.0
        rows.append({"year": y, "tl_opening": opening, "tl_interest": tl_interest,
                     "wc_outstanding": wc_out, "wc_interest": wc_interest,
                     "agf": agf, "principal": princ, "tl_closing": closing,
                     "debt_service": ds, "cfads": c,
                     "dscr": (c / ds) if ds else None})
        opening = closing

    d = [r["dscr"] for r in rows if r["dscr"] is not None]
    post = [r["dscr"] for r in rows[tl_moratorium:] if r["dscr"] is not None]
    return {
        "label": label,
        "term_loan": term_loan, "wc_limit": wc_limit, "total_limit": total_limit,
        "rate_pct": rate * 100, "tl_tenor_years": tl_tenor,
        "tl_moratorium_years": tl_moratorium,
        "cgtmse": {
            "agf_rate_pct": rate_agf,
            "agf_slab": f"limit of Rs {total_limit/CR:.2f} Cr",
            "coverage_pct": coverage_pct,
            "guaranteed_amount": total_limit * coverage_pct / 100,
            "uncovered_amount": total_limit * (1 - coverage_pct / 100),
            "within_ceiling": total_limit <= CGTMSE["ceiling_per_borrower_cr"] * CR,
        },
        "schedule": rows,
        "min_dscr": min(d) if d else None,
        "avg_dscr": sum(d) / len(d) if d else None,
        "min_dscr_post_moratorium": min(post) if post else None,
        "avg_dscr_post_moratorium": (sum(post) / len(post)) if post else None,
        "bankable": (min(post) >= 1.30) if post else False,
        "total_interest": sum(r["tl_interest"] + r["wc_interest"] for r in rows),
        "total_agf": sum(r["agf"] for r in rows),
        "total_finance_cost": sum(r["tl_interest"] + r["wc_interest"] + r["agf"] for r in rows),
    }

def cash_waterfall(fcf_detail, schedule, opening_cash):
    """
    What is actually left in the account after the loan is served.

    The project free cash flow view answers "does this project earn its capital
    back". This answers a different and blunter question a lender asks: with the
    facility being repaid on schedule, does the balance ever go below zero — and
    can the business fund its own reinvestment without coming back for more money.
    """
    ds = {x["year"]: x["debt_service"] for x in schedule}
    cash, rows, low = opening_cash, [], opening_cash
    for d in fcf_detail:
        service = ds.get(d["year"], 0.0)
        net = (d["ebitda"] - d["tax"] - d["maintenance_capex"]
               - d.get("growth_capex", 0.0) - service)
        cash += net
        low = min(low, cash)
        rows.append({"year": d["year"], "ebitda": d["ebitda"], "tax": d["tax"],
                     "maintenance_capex": d["maintenance_capex"],
                     "growth_capex": d.get("growth_capex", 0.0),
                     "debt_service": service, "net": net, "closing_cash": cash})
    return {"opening_cash": opening_cash, "detail": rows,
            "lowest_balance": low, "closing_cash": cash,
            "self_funding": low >= 0.0}

def debt_capacity(cfads, rate, tl_tenor, tl_moratorium, wc_share, wc_util_profile,
                  target_dscr=1.30, hi=2000.0):
    """
    Largest CGTMSE facility the project can service at the target minimum DSCR.
    Bisects on the total limit, splitting it between term loan and working capital
    in the given proportion.
    """
    lo = 0.0
    best = None
    for _ in range(60):
        mid = (lo + hi) / 2
        wc = mid * wc_share
        tl = mid - wc
        util = [min(u, wc) for u in wc_util_profile]
        f = composite_facility(tl, wc, util, rate, tl_tenor, tl_moratorium, cfads,
                               label="Debt capacity at the target DSCR")
        m = f["min_dscr_post_moratorium"]
        if m is not None and m >= target_dscr:
            best = f
            lo = mid
        else:
            hi = mid
    return {"target_dscr": target_dscr,
            "max_total_limit": best["total_limit"] if best else 0.0,
            "max_term_loan": best["term_loan"] if best else 0.0,
            "max_wc_limit": best["wc_limit"] if best else 0.0,
            "achieved_min_dscr": best["min_dscr_post_moratorium"] if best else None,
            "facility": best}

def project_fcf(years, t0_outflow, terminal_inflow=0.0, maint_capex_pct=0.02):
    """
    Unlevered free cash flow to the project.
    t0 is the true capital cost (mobilisation, deposits, advance licence fee) —
    the opex facility is financing, not project cost, so it is excluded here.
    """
    flows = [-t0_outflow]
    detail = []
    for i, y in enumerate(years):
        ebitda = y["ebitda"]
        ebit = ebitda - y["depreciation"]
        tax = max(0.0, ebit) * CORPORATE_TAX
        rev = y["revenue"]["total"] if isinstance(y["revenue"], dict) else y["revenue"]
        maint = rev * maint_capex_pct
        growth = y.get("growth_capex", 0.0)
        fcf = ebitda - tax - maint - growth
        term = terminal_inflow if i == len(years) - 1 else 0.0
        fcf += term
        flows.append(fcf)
        detail.append({"year": y["year"], "ebitda": ebitda, "tax": tax,
                       "maintenance_capex": maint, "growth_capex": growth,
                       "terminal_inflow": term, "fcf": fcf})
    r = irr(flows)
    return {"t0": t0_outflow, "terminal_inflow": terminal_inflow,
            "flows": flows, "detail": detail,
            "irr_pct": r * 100 if r is not None else None,
            "npv_at_15pct": npv(0.15, flows),
            "payback_years": payback_year(flows),
            # Operating free cash flow over the term, before the capital that was
            # deployed to earn it, and the same figure net of that capital. The
            # second is what the free-cash-flow column in the decks adds up to.
            "cumulative_fcf": sum(flows[1:]),
            "cumulative_fcf_net_of_capital": sum(flows)}

def exit_valuation(fcf_detail, years, exit_year, discount=0.15, terminal_inflow=0.0,
                   ebitda_multiple=5.0):
    """Two independent reads on what a stake is worth at the exit date."""
    dcf = residual_dcf(fcf_detail, exit_year, discount, terminal_inflow)
    eb = next((y["ebitda"] for y in years if y["year"] == exit_year), 0.0)
    return {"dcf_remaining_term": dcf,
            "ebitda_multiple_crosscheck": eb * ebitda_multiple,
            "exit_year_ebitda": eb, "ebitda_multiple": ebitda_multiple,
            "discount_rate_pct": discount * 100,
            "used": dcf,
            "basis": ("Discounted remaining concession cash flow. A licence that expires is a wasting "
                      "asset, so an EBITDA multiple flatters it; the multiple is shown only as a cross-check.")}

def residual_dcf(fcf_detail, exit_year, discount=0.15, terminal_inflow=0.0):
    """
    Value of a wasting concession at the exit date: the present value, at that date,
    of the free cash flow still to come before the concession expires. An EBITDA
    multiple overstates a licence that runs out; this does not.
    """
    v = 0.0
    for d in fcf_detail:
        if d["year"] <= exit_year:
            continue
        n = d["year"] - exit_year
        v += d["fcf"] / (1 + discount) ** n
    if terminal_inflow:
        n = fcf_detail[-1]["year"] - exit_year
        v += terminal_inflow / (1 + discount) ** n
    return v

def stake_for_target_irr(investment, exit_year, exit_equity_value, target_irr,
                         distributable=None):
    """
    Ownership percentage an investor must hold to clear a target IRR.
    distributable is the PROJECT cash paid out each year; the investor receives
    its stake share of it, so dividends scale with the stake being solved for.
    """
    dist = distributable or [0.0] * exit_year
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        flows = [-investment]
        for y in range(1, exit_year + 1):
            f = (dist[y - 1] if y - 1 < len(dist) else 0.0) * mid / 100.0
            if y == exit_year:
                f += exit_equity_value * mid / 100.0
            flows.append(f)
        r = irr(flows)
        if r is None or r < target_irr:
            lo = mid
        else:
            hi = mid
    return hi

def equity_option(investment, stake_pct, exit_year, exit_equity_value,
                  distributable=None, label="", basis=""):
    """
    distributable: project cash distributed to equity each year. The investor
    receives its stake share, so its dividends move with the stake.
    """
    dist = distributable or [0.0] * exit_year
    proceeds = exit_equity_value * stake_pct / 100.0
    div = [d * stake_pct / 100.0 for d in dist]
    flows = [-investment]
    for y in range(1, exit_year + 1):
        f = div[y - 1] if y - 1 < len(div) else 0.0
        if y == exit_year:
            f += proceeds
        flows.append(f)
    r = irr(flows)
    return {"label": label, "basis": basis, "investment": investment,
            "stake_pct": stake_pct, "exit_year": exit_year,
            "exit_equity_value": exit_equity_value, "exit_proceeds": proceeds,
            "distributable": dist, "dividends": div, "flows": flows,
            "irr_pct": r * 100 if r is not None else None,
            "money_multiple": sum(flows[1:]) / investment if investment else None,
            "stake_for_18pct": stake_for_target_irr(investment, exit_year, exit_equity_value, 0.18, dist),
            "stake_for_22pct": stake_for_target_irr(investment, exit_year, exit_equity_value, 0.22, dist),
            "stake_for_25pct": stake_for_target_irr(investment, exit_year, exit_equity_value, 0.25, dist)}

def ccd_option(principal, coupon_pct, conversion_year, conversion_stake_pct,
               exit_year, exit_equity_value, distributable=None, label="", basis=""):
    """
    Compulsorily convertible debenture. Coupon runs to conversion; the instrument
    then converts at a formula fixed on the day of issue and exits as equity.
    After conversion the holder is a shareholder and takes its stake share of
    distributions. Sits as DEBT on the balance sheet until conversion.
    """
    dist = distributable or [0.0] * exit_year
    proceeds = exit_equity_value * conversion_stake_pct / 100.0
    flows = [-principal]
    for y in range(1, exit_year + 1):
        if y <= conversion_year:
            f = principal * coupon_pct / 100.0                 # coupon phase
        else:
            f = (dist[y - 1] if y - 1 < len(dist) else 0.0) \
                * conversion_stake_pct / 100.0                  # equity phase
        if y == exit_year:
            f += proceeds
        flows.append(f)
    r = irr(flows)
    return {"label": label, "basis": basis, "principal": principal,
            "coupon_pct": coupon_pct, "conversion_year": conversion_year,
            "conversion_stake_pct": conversion_stake_pct,
            "coupon_paid_total": principal * coupon_pct / 100.0 * conversion_year,
            "exit_year": exit_year, "exit_equity_value": exit_equity_value,
            "exit_proceeds": proceeds, "distributable": dist, "flows": flows,
            "irr_pct": r * 100 if r is not None else None,
            "money_multiple": sum(flows[1:]) / principal if principal else None}

# ============================================================================
# ASSEMBLY
# ============================================================================
def capital_requirement(mobilisation_total, years, later_capex=None):
    """
    True capital a project consumes: mobilisation, plus any capex added later,
    plus the cumulative operating deficit before the project turns cash-positive.
    This — not the gross opex facility — is what equity must fund.
    """
    later_capex = later_capex or {}
    cum, peak, deficit = mobilisation_total, mobilisation_total, 0.0
    for y in years:
        cum += later_capex.get(y["year"], 0.0)
        if y["ebitda"] < 0:
            deficit += -y["ebitda"]
            cum += -y["ebitda"]
        peak = max(peak, cum)
    return {"mobilisation": mobilisation_total,
            "later_capex": sum(later_capex.values()),
            "cumulative_operating_deficit": deficit,
            "total": peak}

def cost_of_capital_view(project_irr_pct, debt_rate_pct, agf_pct, equity_hurdle_pct=22.0):
    all_in_debt = debt_rate_pct + agf_pct
    return {
        "project_irr_pct": project_irr_pct,
        "all_in_cost_of_cgtmse_debt_pct": all_in_debt,
        "equity_hurdle_pct": equity_hurdle_pct,
        "spread_over_debt_pct": (project_irr_pct - all_in_debt) if project_irr_pct is not None else None,
        "clears_debt": project_irr_pct is not None and project_irr_pct > all_in_debt,
        "clears_equity_hurdle": project_irr_pct is not None and project_irr_pct > equity_hurdle_pct,
        "verdict": (
            "Equity-fundable: the project out-earns a private-equity hurdle."
            if project_irr_pct is not None and project_irr_pct > equity_hurdle_pct else
            "Debt-fundable only: the project out-earns CGTMSE debt but not an equity hurdle. "
            "Third-party equity at this scale destroys value; fund it with the guaranteed facility "
            "and keep the upside."
            if project_irr_pct is not None and project_irr_pct > all_in_debt else
            "Below the cost of debt. Do not gear this project as modelled — re-bid the licence fee, "
            "renegotiate the manpower schedule, or stand down."
        ),
    }

def max_licence_fee(builder, base_licence, hurdle_pct, lo=0.2, hi=4.0):
    """
    Highest licence fee (as a multiple of the modelled bid) at which the project IRR
    still clears the given hurdle. This is the walk-away number for the auction.
    """
    saved = dict(SCEN)
    def irr_at(mult):
        SCEN.update({"footfall": 1.0, "yield": 1.0, "opex": 1.0, "licence": mult})
        p = builder()
        t0 = p["mobilisation"]["total"] if "mobilisation" in p else p["capex_total"]
        return project_fcf(p["years"], t0)["irr_pct"]
    a, b = lo, hi
    for _ in range(50):
        mid = (a + b) / 2
        v = irr_at(mid)
        if v is not None and v >= hurdle_pct:
            a = mid
        else:
            b = mid
    SCEN.update(saved)
    return {"hurdle_pct": hurdle_pct, "multiple_of_base": a,
            "licence_fee_year1": base_licence * a,
            "licence_fee_month": base_licence * a / 12}

def run_scenarios(builder, cases, terminal_inflow=0.0, t0_extra=0.0):
    """Re-run a project builder under scenario multipliers and report the headline metrics."""
    out = {}
    saved = dict(SCEN)
    for name, mult, note in cases:
        SCEN.update({"footfall": 1.0, "yield": 1.0, "opex": 1.0, "licence": 1.0})
        SCEN.update(mult)
        p = builder()
        yrs = p["years"]
        t0 = (p["mobilisation"]["total"] if "mobilisation" in p else p["capex_total"]) + t0_extra
        sc_fcf = project_fcf(yrs, t0, terminal_inflow=terminal_inflow)
        rev_stab = yrs[min(4, len(yrs) - 1)]
        out[name] = {
            "note": note, "multipliers": dict(mult),
            "revenue_year1": (yrs[0]["revenue"]["total"] if isinstance(yrs[0]["revenue"], dict)
                              else yrs[0]["revenue"]),
            "ebitda_year1": yrs[0]["ebitda"],
            "revenue_stabilised": (rev_stab["revenue"]["total"] if isinstance(rev_stab["revenue"], dict)
                                   else rev_stab["revenue"]),
            "ebitda_stabilised": rev_stab["ebitda"],
            "ebitda_margin_stabilised": rev_stab["ebitda_margin"],
            "ebitda_final_year": yrs[-1]["ebitda"],
            "project_irr_pct": sc_fcf["irr_pct"],
            "payback_years": sc_fcf["payback_years"],
            "cumulative_fcf": sc_fcf["cumulative_fcf"],
        }
    SCEN.update(saved)
    return out

def main():
    SCEN.update({"footfall": 1.0, "yield": 1.0, "opex": 1.0, "licence": 1.0})
    ggv = build_ggv()
    rv = build_rv()
    karnal = build_karnal()

    # ------------------------------------------------------------------ GGV --
    g_mob = ggv["mobilisation"]["total"]
    g_opex1 = ggv["year1_opex"]
    g_ask = ggv["funding_ask"]                       # mobilisation + one year of opex, as briefed
    g_cfads = [y["ebitda"] for y in ggv["years"]]
    g_wc_util = [34.0, 26.0, 18.0, 13.0, 9.0, 7.0, 5.0]
    g_debt = composite_facility(
        term_loan=58.0, wc_limit=42.0, wc_utilisation=g_wc_util,
        rate=DEBT_RATE_BANK, tl_tenor=7, tl_moratorium=1, cfads=g_cfads,
        label="CGTMSE composite facility \u2014 Geeta Govind Vatika")
    g_fcf = project_fcf(ggv["years"], g_mob,
                        terminal_inflow=ggv["mobilisation"]["security_deposit"] + GGV_RFP["emd_lakh"])
    g_cap = capital_requirement(g_mob, ggv["years"])
    g_exit_year = 5
    g_exit = exit_valuation(g_fcf["detail"], ggv["years"], g_exit_year, 0.15,
                            ggv["mobilisation"]["security_deposit"] + GGV_RFP["emd_lakh"], 4.5)
    g_exit_val = g_exit["used"]
    ggv["financing"] = {
        "ask": g_ask, "true_capital_requirement": g_cap, "opex_facility": g_opex1,
        "project_fcf": g_fcf,
        "cost_of_capital": cost_of_capital_view(g_fcf["irr_pct"], DEBT_RATE_BANK * 100,
                                                g_debt["cgtmse"]["agf_rate_pct"]),
        "debt": g_debt,
        # Geeta Govind Vatika is offered on debt only. No equity or CCD option is
        # computed for it, so nothing downstream can quote a stake or a dilution
        # figure for a project that is not on offer that way.
        "instruments": ["debt"],
        "exit_equity_value": g_exit_val, "exit_year": g_exit_year, "exit_valuation": g_exit,
    }
    ggv["financing"]["debt_optimised"] = composite_facility(
        term_loan=58.0, wc_limit=42.0, wc_utilisation=g_wc_util,
        rate=DEBT_RATE_BANK, tl_tenor=7, tl_moratorium=1, cfads=g_cfads,
        label="As proposed \u2014 the standby limit is already at peak drawdown")
    ggv["financing"]["agf_saving_optimised"] = (
        g_debt["total_agf"] - ggv["financing"]["debt_optimised"]["total_agf"])

    # What one rupee on the ADA-approved show tariff is worth in a full year
    _g3 = ggv["years"][2]["revenue"]
    ggv["financing"]["show_tariff_sensitivity"] = {
        "year": 3, "footfall_lakh": _g3["footfall_lakh"], "show_conversion_pct": 28.0,
        "value_per_rupee_of_tariff_lakh": _g3["footfall_lakh"] * 1e5 * 0.28 / 1.18 / 1e5,
    }
    # The break-even licence fee is an internal bid-discipline number, not deck
    # content. max_licence_fee() still computes it; re-enable the line below only
    # when it is asked for.
    # ggv["financing"]["walk_away"] = max_licence_fee(
    #     build_ggv, GGV_BID_LICENCE_YEAR_1, g_debt["cgtmse"]["agf_rate_pct"] + DEBT_RATE_BANK * 100)
    # The opening balance is the part of the facility not spent on mobilisation:
    # the standby working capital is what carries the thin first season.
    ggv["financing"]["cash_waterfall"] = cash_waterfall(
        g_fcf["detail"], g_debt["schedule"],
        opening_cash=ggv["mobilisation"]["working_capital"])
    # Capacity has to be measured on the structure actually proposed. Solving it at
    # a different term/working-capital split answers a question nobody asked, and
    # makes the headroom against the facility sought meaningless.
    ggv["financing"]["debt_capacity"] = debt_capacity(
        g_cfads, DEBT_RATE_BANK, 7, 1, g_debt["wc_limit"] / g_debt["total_limit"], g_wc_util)

    ggv["scenarios"] = run_scenarios(build_ggv, [
        ("downside", {"footfall": 0.85, "yield": 0.85, "opex": 1.05, "licence": 1.25},
         "15% below the footfall and show-conversion base, 5% cost overrun, licence bid 25% above the modelled fee"),
        ("base", {}, "As modelled: 3.75 lakh visits in the opening season, 24% show conversion, ₹36 lakh licence fee"),
        ("upside", {"footfall": 1.15, "yield": 1.20, "opex": 0.98},
         "15% more footfall, 20% better show conversion, tight cost control"),
    ], terminal_inflow=ggv["mobilisation"]["security_deposit"] + GGV_RFP["emd_lakh"])

    # ------------------------------------------------------------------- RV --
    r_mob = rv["mobilisation"]["total"]
    r_ask = rv["facility_ask"]                       # two years of opex, as briefed
    r_toy = rv["mobilisation"]["capex_year2_toy_train"]
    r_cfads = [y["ebitda"] for y in rv["years"]]
    r_wc_util = [110.0, 150.0, 120.0, 90.0, 60.0, 40.0, 25.0, 15.0, 10.0]
    r_tl = r_mob + r_toy
    r_debt = composite_facility(
        term_loan=r_tl, wc_limit=r_ask - r_tl, wc_utilisation=r_wc_util,
        rate=DEBT_RATE_BANK, tl_tenor=9, tl_moratorium=4, cfads=r_cfads,
        label="CGTMSE composite facility \u2014 Ramayan Vatika")
    r_fcf = project_fcf(rv["years"], r_tl,
                        terminal_inflow=RV_RFP["performance_security_lakh"] + RV_RFP["emd_lakh"])
    r_cap = capital_requirement(r_mob, rv["years"], later_capex={2: r_toy})
    r_exit_year = 7
    r_exit = exit_valuation(r_fcf["detail"], rv["years"], r_exit_year, 0.15,
                            RV_RFP["performance_security_lakh"] + RV_RFP["emd_lakh"], 5.0)
    r_exit_val = r_exit["used"]
    rv["financing"] = {
        "facility_ask": r_ask, "true_capital_requirement": r_cap,
        "opex_facility": r_ask - r_tl, "project_fcf": r_fcf,
        "cost_of_capital": cost_of_capital_view(r_fcf["irr_pct"], DEBT_RATE_BANK * 100,
                                                r_debt["cgtmse"]["agf_rate_pct"]),
        "debt": r_debt,
        "equity": equity_option(r_cap["total"], 70.0, r_exit_year, r_exit_val,
                                distributable=[max(0.0, d["fcf"]) for d in r_fcf["detail"][:r_exit_year]],
                                label="Project-level equity \u2014 Ramayan Vatika",
                                basis=("Sized to the true capital requirement. Exit at year 7 valued as "
                                       "the discounted remaining cash flow over the balance of the "
                                       "10+5 year concession.")),
        "ccd": ccd_option(r_cap["total"], 8.0, 4, 65.0, r_exit_year, r_exit_val,
                          distributable=[max(0.0, d["fcf"]) for d in r_fcf["detail"][:r_exit_year]],
                          label="CCD converting at the end of year 4 \u2014 Ramayan Vatika",
                          basis="8% coupon to conversion, then 65% of project equity"),
        "exit_equity_value": r_exit_val, "exit_year": r_exit_year, "exit_valuation": r_exit,
    }
    rv["financing"]["debt_optimised"] = composite_facility(
        term_loan=r_tl, wc_limit=170.0, wc_utilisation=r_wc_util,
        rate=DEBT_RATE_BANK, tl_tenor=9, tl_moratorium=4, cfads=r_cfads,
        label="Right-sized variant \u2014 working capital limit cut to peak drawdown")
    rv["financing"]["agf_saving_optimised"] = (
        r_debt["total_agf"] - rv["financing"]["debt_optimised"]["total_agf"])

    # What the gap between BDA's 60% show conversion and the modelled rate is worth
    _r5 = rv["years"][4]["revenue"]
    _gap = 0.60 - 0.48
    rv["financing"]["conversion_gap_value"] = {
        "year": 5, "footfall_lakh": _r5["footfall_lakh"],
        "bda_conversion_pct": 60.0, "modelled_conversion_pct": 48.0,
        "show_tariff_gross": 165,
        "value_lakh": _r5["footfall_lakh"] * 1e5 * _gap * 165 / 1.18 / 1e5,
    }
    # Internal only, as at Geeta Govind Vatika above.
    # rv["financing"]["walk_away"] = max_licence_fee(
    #     build_rv, RV_BID_LICENCE_YEAR_1, r_debt["cgtmse"]["agf_rate_pct"] + DEBT_RATE_BANK * 100)
    rv["financing"]["debt_capacity"] = debt_capacity(
        r_cfads, DEBT_RATE_BANK, 9, 4, r_debt["wc_limit"] / r_debt["total_limit"], r_wc_util)

    rv["scenarios"] = run_scenarios(build_rv, [
        ("downside", {"footfall": 0.85, "yield": 0.85, "opex": 1.05, "licence": 1.33},
         "15% below base on footfall and show conversion, 5% cost overrun, licence bid up to ₹44 lakh"),
        ("base", {}, "As modelled: 1.65 lakh visits in year 1, 42% show conversion, ₹33 lakh licence fee"),
        ("bda_indicative", {"footfall": 1.10, "yield": 1.40},
         "BDA's own indicative case: 500 visitors/day with 60% paying for the show"),
    ], terminal_inflow=RV_RFP["performance_security_lakh"] + RV_RFP["emd_lakh"],
       t0_extra=rv["mobilisation"]["capex_year2_toy_train"])

    # --------------------------------------------------------------- KARNAL --
    k_cost = karnal["capex_total"]
    k_cfads = [y["ebitda"] for y in karnal["years"]]
    k_promoter = k_cost * 0.25
    k_tl = k_cost - k_promoter
    k_wc_util = [25.0, 40.0, 35.0, 30.0, 25.0, 20.0, 15.0, 12.0, 10.0]
    k_debt = composite_facility(
        term_loan=k_tl, wc_limit=50.0, wc_utilisation=k_wc_util,
        rate=DEBT_RATE_BANK, tl_tenor=9, tl_moratorium=2, cfads=k_cfads,
        label="CGTMSE term loan and working capital \u2014 Karnal Phase 1")
    k_debt["promoter_contribution"] = k_promoter
    k_debt["promoter_margin_pct"] = 25.0
    k_fcf = project_fcf(karnal["years"], k_cost)
    k_cap = capital_requirement(k_cost, karnal["years"])
    k_exit_year = 6
    k_exit = exit_valuation(k_fcf["detail"], karnal["years"], k_exit_year, 0.15, 0.0, 6.0)
    k_exit_val = k_exit["used"]
    # the sub-lease runs 15 years; five years of cash flow beyond the model horizon
    k_exit["dcf_remaining_term"] = k_exit_val
    k_exit_val += sum(karnal["years"][-1]["ebitda"] * 1.03 ** n * 0.72 / (1.15 ** (n + 10 - k_exit_year))
                      for n in range(1, 6))
    k_exit["beyond_model_horizon"] = k_exit_val - k_exit["dcf_remaining_term"]
    k_exit["used"] = k_exit_val
    karnal["financing"] = {
        "project_cost": k_cost, "true_capital_requirement": k_cap, "project_fcf": k_fcf,
        "cost_of_capital": cost_of_capital_view(k_fcf["irr_pct"], DEBT_RATE_BANK * 100,
                                                k_debt["cgtmse"]["agf_rate_pct"]),
        "debt": k_debt,
        "equity": equity_option(k_cap["total"], 45.0, k_exit_year, k_exit_val,
                                distributable=[max(0.0, d["fcf"]) for d in k_fcf["detail"][:k_exit_year]],
                                label="Project-level equity \u2014 Karnal",
                                basis=("Sized to the project cost plus the year-1 operating deficit \u2014 equity has to "
                                       "fund the ramp as well as the build. Exit at year 6 valued as the discounted "
                                       "cash flow over the balance of the 15-year sub-lease.")),
        "ccd": ccd_option(k_cap["total"], 9.0, 3, 38.0, k_exit_year, k_exit_val,
                          distributable=[max(0.0, d["fcf"]) for d in k_fcf["detail"][:k_exit_year]],
                          label="CCD converting at the end of year 3 \u2014 Karnal",
                          basis="9% coupon to conversion, then 38% of project equity"),
        "exit_equity_value": k_exit_val, "exit_year": k_exit_year, "exit_valuation": k_exit,
    }
    karnal["financing"]["debt_capacity"] = debt_capacity(
        k_cfads, DEBT_RATE_BANK, 9, 2, k_debt["wc_limit"] / k_debt["total_limit"], k_wc_util)

    karnal["scenarios"] = run_scenarios(build_karnal, [
        ("downside", {"footfall": 0.75, "opex": 1.08},
         "25% below the revenue base \u2014 the low end of the deck's own FY28-29 range \u2014 with an 8% cost overrun"),
        ("base", {}, "As modelled: ₹3.25 Cr in the first full year, within the deck's ₹3–4 Cr range"),
        ("upside", {"footfall": 1.20, "opex": 0.97},
         "Top of the deck's range at ₹3.9 Cr in the first full year, with tight cost control"),
    ])

    # -------------------------------------------------------------- COMPANY --
    consol = consolidated_plan(ggv, rv, karnal)
    company = build_company(consol)

    # ------------------------------------------- CGTMSE ceiling allocation ---
    ceiling = CGTMSE["ceiling_per_borrower_cr"] * CR
    demand = {
        "Geeta Govind Vatika — composite": g_debt["total_limit"],
        "Ramayan Vatika — composite": r_debt["total_limit"],
        "Karnal Phase 1 — term loan + WC": k_debt["total_limit"],
        "VAPPL — working capital and NBFC consolidation": 350.0,
    }
    total_demand = sum(demand.values())
    plan = {
        "Karnal Phase 1 — term loan": 300.0,
        "Ramayan Vatika — term loan + standby WC": 260.0,
        "Geeta Govind Vatika — term loan + standby WC": 190.0,
        "VAPPL — working capital, NBFC consolidation": 250.0,
    }
    allocation = {
        "ceiling": ceiling, "ceiling_basis": CGTMSE["ceiling_basis"],
        "gross_demand": demand, "total_gross_demand": total_demand,
        "excess_over_ceiling": total_demand - ceiling,
        "single_borrower_plan": plan,
        "single_borrower_plan_total": sum(plan.values()),
        "headroom": ceiling - sum(plan.values()),
        "residual_to_fund_outside_cgtmse": total_demand - sum(plan.values()),
    }

    out = {
        "meta": {"entity": COMPANY["name"], "cin": COMPANY["cin"],
                 "prepared": "August 2026", "units": "INR lakh unless stated",
                 "generator": "model/pf_model.py",
                 "tax_rate_pct": CORPORATE_TAX * 100,
                 "bank_rate_pct": DEBT_RATE_BANK * 100},
        "cgtmse": CGTMSE, "msme_limits": MSME_LIMITS,
        "ggv": ggv, "rv": rv, "karnal": karnal,
        "consolidated": consol, "company": company,
        "cgtmse_allocation": allocation,
    }
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pf_model.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out

# ----------------------------------------------------------------------------
# Rates
# ----------------------------------------------------------------------------
DEBT_RATE_BANK = 0.115     # scheduled bank, repo-linked. CGTMSE norm keeps MLI
                           # pricing within ~3% of EBLR; NBFC money for the same
                           # borrower currently prices at 14-22%.

# ----------------------------------------------------------------------------
# Consolidated plan — existing four parks plus the three new projects
# ----------------------------------------------------------------------------
# Phasing assumed for the consolidation:
#   Geeta Govind Vatika  award ~Oct 2026  -> half of project year 1 lands in FY26-27
#   Ramayan Vatika       award ~Jan 2027  -> project year 1 lands in FY27-28
#   Karnal               opens ~Sep 2027  -> project year 1 (stub) lands in FY27-28
FY_LABELS = ["FY26-27", "FY27-28", "FY28-29", "FY29-30", "FY30-31"]

EXISTING_BASE = {   # midpoints from financials.html, extended two years at the stated maturity path
    "FY26-27": {"revenue": 2400.0, "ebitda": 550.0},
    "FY27-28": {"revenue": 3300.0, "ebitda": 800.0},
    "FY28-29": {"revenue": 4350.0, "ebitda": 1200.0},
    "FY29-30": {"revenue": 5100.0, "ebitda": 1450.0},
    "FY30-31": {"revenue": 5800.0, "ebitda": 1690.0},
}

def _blend(years, weights):
    """weights: list of (project_year_index, fraction) contributing to one fiscal year."""
    rev = ebitda = 0.0
    for idx, frac in weights:
        if idx < 0 or idx >= len(years):
            continue
        y = years[idx]
        r = y["revenue"]["total"] if isinstance(y["revenue"], dict) else y["revenue"]
        rev += r * frac
        ebitda += y["ebitda"] * frac
    return rev, ebitda

def consolidated_plan(ggv, rv, karnal):
    phasing = {
        "FY26-27": {"ggv": [(0, 0.50)], "rv": [], "karnal": []},
        "FY27-28": {"ggv": [(0, 0.50), (1, 0.50)], "rv": [(0, 1.0)], "karnal": [(0, 1.0)]},
        "FY28-29": {"ggv": [(1, 0.50), (2, 0.50)], "rv": [(1, 1.0)], "karnal": [(1, 1.0)]},
        "FY29-30": {"ggv": [(2, 0.50), (3, 0.50)], "rv": [(2, 1.0)], "karnal": [(2, 1.0)]},
        "FY30-31": {"ggv": [(3, 0.50), (4, 0.50)], "rv": [(3, 1.0)], "karnal": [(3, 1.0)]},
    }
    src = {"ggv": ggv["years"], "rv": rv["years"], "karnal": karnal["years"]}
    rows = []
    for fy in FY_LABELS:
        base = EXISTING_BASE[fy]
        parts = {"existing": {"revenue": base["revenue"], "ebitda": base["ebitda"]}}
        for k in ("ggv", "rv", "karnal"):
            r, e = _blend(src[k], phasing[fy][k])
            parts[k] = {"revenue": r, "ebitda": e}
        rev = sum(p["revenue"] for p in parts.values())
        eb = sum(p["ebitda"] for p in parts.values())
        rows.append({"fy": fy, "parts": parts, "revenue": rev, "ebitda": eb,
                     "ebitda_margin": eb / rev * 100 if rev else None})
    return {"phasing_note": ("Geeta Govind Vatika awarded ~Oct 2026, Ramayan Vatika ~Jan 2027, "
                            "Karnal opening ~Sep 2027. Existing-portfolio figures are the midpoints "
                            "published in financials.html, extended two further years on the stated "
                            "maturity path."),
            "years": rows}

# ----------------------------------------------------------------------------
# Company-level capital structure
# ----------------------------------------------------------------------------
def leverage_after_facility(facility, nbfc_refinanced, conversion_amount, retained_earnings=0.0):
    """
    Where debt-to-equity lands once the new facility is drawn. A lender covenanting
    at 2.0x will size the facility off this, not off the pre-drawdown position.
    """
    fy = COMPANY["fy26"]
    nw = fy["net_worth"] + conversion_amount + retained_earnings
    debt = fy["borrowings_total"] - conversion_amount - nbfc_refinanced + facility
    return {"conversion": conversion_amount, "retained_earnings": retained_earnings,
            "net_worth": nw, "borrowings": debt, "debt_equity": debt / nw if nw else None}

def max_facility_at_covenant(covenant, conversion_amount, nbfc_refinanced, retained_earnings=0.0):
    """Largest new facility that keeps debt-to-equity inside a covenant."""
    fy = COMPANY["fy26"]
    nw = fy["net_worth"] + conversion_amount + retained_earnings
    standing = fy["borrowings_total"] - conversion_amount - nbfc_refinanced
    return max(0.0, covenant * nw - standing)

def build_company(consol):
    fy = COMPANY["fy26"]
    exit_row = consol["years"][-1]                  # FY30-31
    exit_revenue = exit_row["revenue"]
    exit_ebitda = exit_row["ebitda"]

    # Valuation at exit: the deck's own peer frame is 3-5x forward revenue at this
    # stage of maturity. 3.0x is taken as the base and 11x EBITDA as the cross-check.
    ev_revenue_multiple = 3.0
    ev = exit_revenue * ev_revenue_multiple
    ev_ebitda_crosscheck = exit_ebitda * 11.0
    net_debt_at_exit = 800.0
    exit_equity_value = ev - net_debt_at_exit

    # --- Option 1: equity -----------------------------------------------------
    pre_money = 9000.0
    raise_amt = 1600.0
    stake = raise_amt / (pre_money + raise_amt) * 100
    eq = equity_option(raise_amt, stake, 5, exit_equity_value,
                       distributable=[0.0] * 5,
                       label="VAPPL primary equity round",
                       basis=f"Exit FY30-31 at {ev_revenue_multiple:.1f}x revenue "
                             f"(Rs {ev/CR:.0f} Cr EV) less Rs {net_debt_at_exit/CR:.0f} Cr net debt")
    eq["pre_money"] = pre_money
    eq["post_money"] = pre_money + raise_amt
    eq["existing_round"] = {"amount": 1000.0, "pre_money": 9000.0, "dilution_pct": 10.0}
    # what pre-money clears each hurdle
    def premoney_for(target):
        s = stake_for_target_irr(raise_amt, 5, exit_equity_value, target)
        post = raise_amt / (s / 100.0)
        return {"stake_pct": s, "post_money": post, "pre_money": post - raise_amt}
    eq["pricing_sensitivity"] = {"irr_18": premoney_for(0.18),
                                 "irr_22": premoney_for(0.22),
                                 "irr_25": premoney_for(0.25)}

    # --- Option 2: CGTMSE debt ------------------------------------------------
    _last = consol["years"][-1]["ebitda"]
    cfads = [r["ebitda"] for r in consol["years"]] + [_last * 1.06, _last * 1.12]
    wc_util = [250.0, 300.0, 280.0, 240.0, 200.0, 160.0, 120.0]
    debt = composite_facility(term_loan=650.0, wc_limit=350.0, wc_utilisation=wc_util,
                              rate=DEBT_RATE_BANK, tl_tenor=7, tl_moratorium=1,
                              cfads=cfads,
                              label="CGTMSE composite facility — VAPPL consolidated")
    # existing debt service must sit alongside the new facility
    existing_service = []
    for i in range(7):
        outstanding = max(0.0, fy["borrowings_short"] - 300.0) * (1 - i / 6)   # Rs 3 Cr refinanced into the new TL
        existing_service.append(outstanding * 0.145 + (fy["borrowings_short"] - 300.0) / 6)
    combined = []
    for i, row in enumerate(debt["schedule"]):
        tot = row["debt_service"] + existing_service[i]
        combined.append({"year": row["year"], "new_facility": row["debt_service"],
                         "existing_debt": existing_service[i], "total_debt_service": tot,
                         "cfads": row["cfads"],
                         "dscr": row["cfads"] / tot if tot else None})
    debt["combined_service"] = combined
    cvals = [c["dscr"] for c in combined if c["dscr"] is not None]
    debt["min_dscr_combined"] = min(cvals) if cvals else None
    debt["avg_dscr_combined"] = sum(cvals) / len(cvals) if cvals else None
    debt["nbfc_refinance"] = 300.0

    # Leverage headroom: the covenant, not the DSCR, is what caps the facility on day one.
    conv_lt = 260.0
    conv_all = sum(COMPANY["promoter_related_debt"].values())
    debt["leverage"] = {
        "covenant_assumed": 2.0,
        "cases": [
            {"label": "No conversion",
             **leverage_after_facility(1000.0, 300.0, 0.0),
             "max_facility_at_covenant": max_facility_at_covenant(2.0, 0.0, 300.0)},
            {"label": "Convert the Rs 2.60 Cr long-term related-party loans",
             **leverage_after_facility(1000.0, 300.0, conv_lt),
             "max_facility_at_covenant": max_facility_at_covenant(2.0, conv_lt, 300.0)},
            {"label": "Convert all related-party and promoter debt",
             **leverage_after_facility(1000.0, 300.0, conv_all),
             "max_facility_at_covenant": max_facility_at_covenant(2.0, conv_all, 300.0)},
            {"label": "Convert all, drawn in tranches as FY26-27 earnings retain",
             **leverage_after_facility(1000.0, 300.0, conv_all,
                                       retained_earnings=COMPANY["projections"]["FY26-27"]["pat"]),
             "max_facility_at_covenant": max_facility_at_covenant(
                 2.0, conv_all, 300.0, COMPANY["projections"]["FY26-27"]["pat"])},
        ],
        "conversion_full": conv_all,
    }

    # --- Option 3: debt converted to equity -----------------------------------
    ccd = ccd_option(1200.0, 8.0, 3, 13.0, 5, exit_equity_value,
                     label="VAPPL compulsorily convertible debentures",
                     basis="8% coupon for 3 years, then conversion into 13% of the company")
    ccd["conversion_valuation_implied"] = 1200.0 / 0.13
    ccd["balance_sheet_note"] = ("CCDs sit as borrowings until conversion. Layered on the FY26 "
                                 "position they take debt-to-equity from 3.04x to "
                                 f"{(fy['borrowings_total'] + 1200.0) / fy['net_worth']:.2f}x, "
                                 "which breaches the leverage covenant on any CGTMSE facility "
                                 "taken in parallel. Convert the related-party debt first.")

    return {
        "profile": COMPANY,
        "msme": company_msme_status(),
        "related_party_conversion": related_party_conversion(),
        "exit_basis": {"fy": exit_row["fy"], "revenue": exit_revenue, "ebitda": exit_ebitda,
                       "ev_revenue_multiple": ev_revenue_multiple, "enterprise_value": ev,
                       "ev_ebitda_crosscheck": ev_ebitda_crosscheck,
                       "net_debt": net_debt_at_exit, "equity_value": exit_equity_value},
        "financing": {"equity": eq, "debt": debt, "ccd": ccd},
    }

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    m = main()
    def cr(x): return f"{x/100:6.2f}"
    def d(x): return f"{x:.2f}" if x is not None else "  n/a"

    print("=== MSME / CGTMSE ELIGIBILITY ===")
    ms = m["company"]["msme"]
    print(f"  P&M Rs {ms['investment_plant_machinery_cr']:.2f} Cr | turnover Rs {ms['turnover_cr']:.2f} Cr"
          f" -> {ms['classification'].upper()} | CGTMSE eligible: {ms['cgtmse_eligible']}")

    for key, name in (("ggv", "GEETA GOVIND VATIKA"), ("rv", "RAMAYAN VATIKA")):
        p = m[key]
        print(f"\n=== {name} (Rs Cr) ===")
        for y in p["years"]:
            print(f"  Y{y['year']:<2} rev {cr(y['revenue']['total'])}  opex {cr(y['opex']['total'])}"
                  f"  EBITDA {cr(y['ebitda'])} ({y['ebitda_margin']:5.1f}%)")
        f = p["financing"]
        cap = f['true_capital_requirement']
        print(f"  true capital {cr(cap['total'])} (mobilisation {cr(cap['mobilisation'])}"
              f" + deficit {cr(cap['cumulative_operating_deficit'])}) | opex facility {cr(f['opex_facility'])}")
        coc = f['cost_of_capital']
        print(f"  project IRR {f['project_fcf']['irr_pct']:.1f}%  payback {f['project_fcf']['payback_years']:.1f} yrs"
              f"  | all-in debt {coc['all_in_cost_of_cgtmse_debt_pct']:.2f}%  spread {coc['spread_over_debt_pct']:+.1f}pp")
        print(f"  VERDICT: {coc['verdict']}")
        for sn, sv in p['scenarios'].items():
            print(f"    {sn:<15} Y1 rev {cr(sv['revenue_year1'])} EBITDA {cr(sv['ebitda_year1'])}"
                  f" | Y5 rev {cr(sv['revenue_stabilised'])} EBITDA {cr(sv['ebitda_stabilised'])}"
                  f" ({sv['ebitda_margin_stabilised']:5.1f}%)")
        db = f["debt"]
        print(f"  DEBT  TL {cr(db['term_loan'])} + WC {cr(db['wc_limit'])} = {cr(db['total_limit'])}"
              f" | AGF {db['cgtmse']['agf_rate_pct']}% | minDSCR(post-mor) {d(db['min_dscr_post_moratorium'])}"
              f" avg {d(db['avg_dscr_post_moratorium'])} | bankable {db['bankable']}")
        dc = f["debt_capacity"]
        print(f"  DEBT CAPACITY at DSCR {dc['target_dscr']}: {cr(dc['max_total_limit'])}"
              f" (TL {cr(dc['max_term_loan'])} + WC {cr(dc['max_wc_limit'])})")
        if "equity" in f:
            print(f"  EQUITY {f['equity']['stake_pct']:.0f}% -> IRR {f['equity']['irr_pct']:.1f}%"
                  f"  x{f['equity']['money_multiple']:.2f} | stake needed for 22%: {f['equity']['stake_for_22pct']:.0f}%")
        if "ccd" in f:
            print(f"  CCD    {f['ccd']['conversion_stake_pct']:.0f}% -> IRR {f['ccd']['irr_pct']:.1f}%"
                  f"  x{f['ccd']['money_multiple']:.2f}")
        if "instruments" in f:
            print(f"  OFFERED ON: {', '.join(f['instruments'])} only")

    p = m["karnal"]
    print("\n=== KARNAL (Rs Cr) ===")
    for y in p["years"]:
        print(f"  Y{y['year']:<2} rev {cr(y['revenue'])}  opex {cr(y['opex']['total'])}"
              f"  EBITDA {cr(y['ebitda'])} ({y['ebitda_margin']:5.1f}%)")
    f = p["financing"]
    coc = f['cost_of_capital']
    print(f"  project cost {cr(f['project_cost'])} | project IRR {f['project_fcf']['irr_pct']:.1f}%"
          f"  payback {f['project_fcf']['payback_years']:.1f} yrs | spread over debt {coc['spread_over_debt_pct']:+.1f}pp")
    print(f"  VERDICT: {coc['verdict']}")
    for sn, sv in p['scenarios'].items():
        print(f"    {sn:<15} Y2 EBITDA {cr(sv['ebitda_stabilised'])} ({sv['ebitda_margin_stabilised']:5.1f}%)")
    db = f["debt"]
    print(f"  DEBT  promoter {cr(db['promoter_contribution'])} + TL {cr(db['term_loan'])}"
          f" + WC {cr(db['wc_limit'])} | AGF {db['cgtmse']['agf_rate_pct']}%"
          f" | minDSCR(post-mor) {d(db['min_dscr_post_moratorium'])} | bankable {db['bankable']}")
    dc = f["debt_capacity"]
    print(f"  DEBT CAPACITY at DSCR {dc['target_dscr']}: {cr(dc['max_total_limit'])}"
          f" (TL {cr(dc['max_term_loan'])} + WC {cr(dc['max_wc_limit'])})")
    print(f"  EQUITY {f['equity']['stake_pct']:.0f}% -> IRR {f['equity']['irr_pct']:.1f}%"
          f" | stake needed for 22%: {f['equity']['stake_for_22pct']:.0f}%")
    print(f"  CCD    IRR {f['ccd']['irr_pct']:.1f}%")

    print("\n=== CONSOLIDATED PLAN (Rs Cr) ===")
    for r in m["consolidated"]["years"]:
        pr = r["parts"]
        print(f"  {r['fy']}  rev {cr(r['revenue'])} (exist {cr(pr['existing']['revenue'])}"
              f" ggv {cr(pr['ggv']['revenue'])} rv {cr(pr['rv']['revenue'])} krl {cr(pr['karnal']['revenue'])})"
              f"  EBITDA {cr(r['ebitda'])} ({r['ebitda_margin']:.1f}%)")

    print("\n=== COMPANY CAPITAL STRUCTURE ===")
    c = m["company"]
    print("  D/E:", {k: round(v["debt_equity"], 2) for k, v in c["related_party_conversion"].items()})
    x = c["exit_basis"]
    print(f"  exit {x['fy']}: rev {cr(x['revenue'])} EBITDA {cr(x['ebitda'])}"
          f" -> EV {cr(x['enterprise_value'])} (EBITDA x-check {cr(x['ev_ebitda_crosscheck'])})"
          f" equity {cr(x['equity_value'])}")
    e = c["financing"]["equity"]
    print(f"  EQUITY Rs {e['investment']/CR:.0f} Cr at Rs {e['pre_money']/CR:.0f} Cr pre"
          f" = {e['stake_pct']:.1f}% -> IRR {e['irr_pct']:.1f}% x{e['money_multiple']:.2f}")
    for k, lbl in (("irr_18", "18%"), ("irr_22", "22%"), ("irr_25", "25%")):
        s = e["pricing_sensitivity"][k]
        print(f"     pre-money clearing {lbl}: Rs {s['pre_money']/CR:.0f} Cr ({s['stake_pct']:.1f}% stake)")
    db = c["financing"]["debt"]
    print(f"  DEBT  TL {cr(db['term_loan'])} + WC {cr(db['wc_limit'])} = {cr(db['total_limit'])}"
          f" | AGF {db['cgtmse']['agf_rate_pct']}%")
    print(f"     DSCR new facility only min {d(db['min_dscr_post_moratorium'])};"
          f" incl. existing debt min {d(db['min_dscr_combined'])} avg {d(db['avg_dscr_combined'])}")
    cc = c["financing"]["ccd"]
    print(f"  CCD   Rs {cc['principal']/CR:.0f} Cr, {cc['coupon_pct']}% to yr {cc['conversion_year']},"
          f" {cc['conversion_stake_pct']}% -> IRR {cc['irr_pct']:.1f}% x{cc['money_multiple']:.2f}"
          f" | implied conversion valuation Rs {cc['conversion_valuation_implied']/CR:.0f} Cr")

    print("\n=== CGTMSE CEILING ===")
    a = m["cgtmse_allocation"]
    print(f"  gross demand {cr(a['total_gross_demand'])} vs ceiling {cr(a['ceiling'])}"
          f" -> excess {cr(a['excess_over_ceiling'])}")
    print(f"  single-borrower plan {cr(a['single_borrower_plan_total'])}"
          f" | to fund outside CGTMSE {cr(a['residual_to_fund_outside_cgtmse'])}")
