"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.financeModelSchema = void 0;
const zod_1 = require("zod");
// Python is the calculation owner. This boundary checks its JSON exchange shape;
// it never recomputes financial results or converts units. Money is INR lakh,
// except explicitly named _cr fields. Null metrics mean no defined result.
const metric = zod_1.z.number().nullable();
const MetaSchema = zod_1.z.object({
    "entity": zod_1.z.string(),
    "cin": zod_1.z.string(),
    "prepared": zod_1.z.string(),
    "units": zod_1.z.literal("INR lakh unless stated"),
    "generator": zod_1.z.literal("model/pf_model.py"),
    "tax_rate_pct": zod_1.z.number(),
    "bank_rate_pct": zod_1.z.number(),
});
const CgtmseSchema = zod_1.z.object({
    "scheme": zod_1.z.string(),
    "ceiling_per_borrower_cr": zod_1.z.number(),
    "ceiling_startup_dpiit_cr": zod_1.z.number(),
    "ceiling_basis": zod_1.z.string(),
    "coverage_small_enterprise_pct": zod_1.z.number(),
    "coverage_preferential_pct": zod_1.z.number(),
    "interest_cap_note": zod_1.z.string(),
    "agf_slabs": zod_1.z.array(zod_1.z.tuple([zod_1.z.number(), zod_1.z.number()])).nonempty(),
    "agf_basis_y1": zod_1.z.string(),
    "agf_basis_y2plus": zod_1.z.string(),
    "agf_concession_pct": zod_1.z.number(),
    "hybrid_security": zod_1.z.boolean(),
    "collateral": zod_1.z.string(),
    "third_party_guarantee": zod_1.z.string(),
});
const MsmeLimitsMicroSchema = zod_1.z.object({
    "investment_cr": zod_1.z.number(),
    "turnover_cr": zod_1.z.number(),
});
const MsmeLimitsSchema = zod_1.z.object({
    "micro": MsmeLimitsMicroSchema,
    "small": MsmeLimitsMicroSchema,
    "medium": MsmeLimitsMicroSchema,
});
const GgvRfpSchema = zod_1.z.object({
    "authority": zod_1.z.string(),
    "site": zod_1.z.string(),
    "area_acres": zod_1.z.number(),
    "term": zod_1.z.string(),
    "selection": zod_1.z.string(),
    "reserve_licence_fee_month_lakh": zod_1.z.number(),
    "reserve_licence_fee_year_lakh": zod_1.z.number(),
    "escalation_pct": zod_1.z.number(),
    "emd_lakh": zod_1.z.number(),
    "tender_fee_lakh": zod_1.z.number(),
    "security_deposit_basis": zod_1.z.string(),
    "payment_terms": zod_1.z.string(),
    "moratorium_days": zod_1.z.number(),
    "entry_tariff_inr": zod_1.z.number(),
    "free_entry": zod_1.z.string(),
    "show_tariff": zod_1.z.string(),
    "penalty_range_inr": zod_1.z.string(),
    "eligibility_turnover_cr": zod_1.z.number(),
    "eligibility_projects": zod_1.z.string(),
    "assets": zod_1.z.string(),
    "scope": zod_1.z.array(zod_1.z.string()).nonempty(),
});
const GgvCapexLinesRowSchema = zod_1.z.object({
    "item": zod_1.z.string(),
    "amount": zod_1.z.number(),
    "life_years": zod_1.z.number(),
});
const GgvMobilisationSchema = zod_1.z.object({
    "capex": zod_1.z.number(),
    "security_deposit": zod_1.z.number(),
    "advance_licence_fee_6m": zod_1.z.number(),
    "emd": zod_1.z.number(),
    "tender_fee": zod_1.z.number(),
    "total": zod_1.z.number(),
    "working_capital": zod_1.z.number(),
    "ask": zod_1.z.number(),
});
const GgvYearsRowRevenueSchema = zod_1.z.object({
    "entry": zod_1.z.number(),
    "show": zod_1.z.number(),
    "fnb": zod_1.z.number(),
    "activities": zod_1.z.number(),
    "activities_gross": zod_1.z.number(),
    "activities_owned_frac": zod_1.z.number(),
    "parking": zod_1.z.number(),
    "events_public": zod_1.z.number(),
    "events_private": zod_1.z.number(),
    "events": zod_1.z.number(),
    "total": zod_1.z.number(),
    "footfall_lakh": zod_1.z.number(),
});
const GgvYearsRowOpexSchema = zod_1.z.object({
    "licence_fee": zod_1.z.number(),
    "manpower": zod_1.z.number(),
    "electricity": zod_1.z.number(),
    "water_horticulture": zod_1.z.number(),
    "show_amc": zod_1.z.number(),
    "repairs": zod_1.z.number(),
    "fnb_cogs": zod_1.z.number(),
    "activity_cost": zod_1.z.number(),
    "events_cost": zod_1.z.number(),
    "marketing": zod_1.z.number(),
    "insurance_statutory": zod_1.z.number(),
    "it_cctv": zod_1.z.number(),
    "corporate_overhead": zod_1.z.number(),
    "contingency": zod_1.z.number(),
    "total": zod_1.z.number(),
});
const GgvYearsRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "revenue": GgvYearsRowRevenueSchema,
    "opex": GgvYearsRowOpexSchema,
    "ebitda": zod_1.z.number(),
    "ebitda_margin": zod_1.z.number(),
    "depreciation": zod_1.z.number(),
    "ebit": zod_1.z.number(),
    "growth_capex": zod_1.z.number(),
});
const GgvCostRatiosSchema = zod_1.z.object({
    "public_event_delivery_pct": zod_1.z.number(),
    "private_event_delivery_pct": zod_1.z.number(),
    "fnb_cogs_pct": zod_1.z.number(),
});
const GgvGrowthCapexSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "lines": zod_1.z.array(GgvCapexLinesRowSchema).min(2),
    "total": zod_1.z.number(),
    "annual_depreciation": zod_1.z.number(),
    "owned_activity_fraction_pct": zod_1.z.array(zod_1.z.number()).min(7),
    "owned_activity_cost_ratio_pct": zod_1.z.number(),
});
const GgvFinancingTrueCapitalRequirementSchema = zod_1.z.object({
    "mobilisation": zod_1.z.number(),
    "later_capex": zod_1.z.number(),
    "cumulative_operating_deficit": zod_1.z.number(),
    "total": zod_1.z.number(),
});
const GgvFinancingProjectFcfDetailRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
    "tax": zod_1.z.number(),
    "maintenance_capex": zod_1.z.number(),
    "growth_capex": zod_1.z.number(),
    "terminal_inflow": zod_1.z.number(),
    "fcf": zod_1.z.number(),
});
const GgvFinancingProjectFcfSchema = zod_1.z.object({
    "t0": zod_1.z.number(),
    "terminal_inflow": zod_1.z.number(),
    "flows": zod_1.z.array(zod_1.z.number()).nonempty(),
    "detail": zod_1.z.array(GgvFinancingProjectFcfDetailRowSchema).nonempty(),
    "irr_pct": metric,
    "npv_at_15pct": zod_1.z.number(),
    "payback_years": metric,
    "cumulative_fcf": zod_1.z.number(),
    "cumulative_fcf_net_of_capital": zod_1.z.number(),
});
const GgvFinancingCostOfCapitalSchema = zod_1.z.object({
    "project_irr_pct": metric,
    "all_in_cost_of_cgtmse_debt_pct": zod_1.z.number(),
    "equity_hurdle_pct": zod_1.z.number(),
    "spread_over_debt_pct": metric,
    "clears_debt": zod_1.z.boolean(),
    "clears_equity_hurdle": zod_1.z.boolean(),
    "verdict": zod_1.z.string(),
});
const GgvFinancingDebtCgtmseSchema = zod_1.z.object({
    "agf_rate_pct": zod_1.z.number(),
    "agf_slab": zod_1.z.string(),
    "coverage_pct": zod_1.z.number(),
    "guaranteed_amount": zod_1.z.number(),
    "uncovered_amount": zod_1.z.number(),
    "within_ceiling": zod_1.z.boolean(),
});
const GgvFinancingDebtScheduleRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "tl_opening": zod_1.z.number(),
    "tl_interest": zod_1.z.number(),
    "wc_outstanding": zod_1.z.number(),
    "wc_interest": zod_1.z.number(),
    "agf": zod_1.z.number(),
    "principal": zod_1.z.number(),
    "tl_closing": zod_1.z.number(),
    "debt_service": zod_1.z.number(),
    "cfads": zod_1.z.number(),
    "dscr": metric,
});
const GgvFinancingDebtSchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "term_loan": zod_1.z.number(),
    "wc_limit": zod_1.z.number(),
    "total_limit": zod_1.z.number(),
    "rate_pct": zod_1.z.number(),
    "tl_tenor_years": zod_1.z.number(),
    "tl_moratorium_years": zod_1.z.number(),
    "cgtmse": GgvFinancingDebtCgtmseSchema,
    "schedule": zod_1.z.array(GgvFinancingDebtScheduleRowSchema).nonempty(),
    "min_dscr": metric,
    "avg_dscr": metric,
    "min_dscr_post_moratorium": metric,
    "avg_dscr_post_moratorium": metric,
    "bankable": zod_1.z.boolean(),
    "total_interest": zod_1.z.number(),
    "total_agf": zod_1.z.number(),
    "total_finance_cost": zod_1.z.number(),
});
const GgvFinancingExitValuationSchema = zod_1.z.object({
    "dcf_remaining_term": zod_1.z.number(),
    "ebitda_multiple_crosscheck": zod_1.z.number(),
    "exit_year_ebitda": zod_1.z.number(),
    "ebitda_multiple": zod_1.z.number(),
    "discount_rate_pct": zod_1.z.number(),
    "used": zod_1.z.number(),
    "basis": zod_1.z.string(),
});
const GgvFinancingShowTariffSensitivitySchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "footfall_lakh": zod_1.z.number(),
    "show_conversion_pct": zod_1.z.number(),
    "value_per_rupee_of_tariff_lakh": zod_1.z.number(),
});
const GgvFinancingCashWaterfallDetailRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
    "tax": zod_1.z.number(),
    "maintenance_capex": zod_1.z.number(),
    "growth_capex": zod_1.z.number(),
    "debt_service": zod_1.z.number(),
    "net": zod_1.z.number(),
    "closing_cash": zod_1.z.number(),
});
const GgvFinancingCashWaterfallSchema = zod_1.z.object({
    "opening_cash": zod_1.z.number(),
    "detail": zod_1.z.array(GgvFinancingCashWaterfallDetailRowSchema).nonempty(),
    "lowest_balance": zod_1.z.number(),
    "closing_cash": zod_1.z.number(),
    "self_funding": zod_1.z.boolean(),
});
const GgvFinancingDebtCapacitySchema = zod_1.z.object({
    "target_dscr": zod_1.z.number(),
    "max_total_limit": zod_1.z.number(),
    "max_term_loan": zod_1.z.number(),
    "max_wc_limit": zod_1.z.number(),
    "achieved_min_dscr": metric,
    "facility": GgvFinancingDebtSchema,
});
const GgvFinancingSchema = zod_1.z.object({
    "ask": zod_1.z.number(),
    "true_capital_requirement": GgvFinancingTrueCapitalRequirementSchema,
    "opex_facility": zod_1.z.number(),
    "project_fcf": GgvFinancingProjectFcfSchema,
    "cost_of_capital": GgvFinancingCostOfCapitalSchema,
    "debt": GgvFinancingDebtSchema,
    "instruments": zod_1.z.array(zod_1.z.string()).nonempty(),
    "exit_equity_value": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_valuation": GgvFinancingExitValuationSchema,
    "debt_optimised": GgvFinancingDebtSchema,
    "agf_saving_optimised": zod_1.z.number(),
    "show_tariff_sensitivity": GgvFinancingShowTariffSensitivitySchema,
    "cash_waterfall": GgvFinancingCashWaterfallSchema,
    "debt_capacity": GgvFinancingDebtCapacitySchema,
});
const GgvScenariosDownsideMultipliersSchema = zod_1.z.object({
    "footfall": zod_1.z.number(),
    "yield": zod_1.z.number(),
    "opex": zod_1.z.number(),
    "licence": zod_1.z.number(),
});
const GgvScenariosDownsideSchema = zod_1.z.object({
    "note": zod_1.z.string(),
    "multipliers": GgvScenariosDownsideMultipliersSchema,
    "revenue_year1": zod_1.z.number(),
    "ebitda_year1": zod_1.z.number(),
    "revenue_stabilised": zod_1.z.number(),
    "ebitda_stabilised": zod_1.z.number(),
    "ebitda_margin_stabilised": zod_1.z.number(),
    "ebitda_final_year": zod_1.z.number(),
    "project_irr_pct": metric,
    "payback_years": metric,
    "cumulative_fcf": zod_1.z.number(),
});
const GgvScenariosBaseMultipliersSchema = zod_1.z.object({});
const GgvScenariosBaseSchema = zod_1.z.object({
    "note": zod_1.z.string(),
    "multipliers": GgvScenariosBaseMultipliersSchema,
    "revenue_year1": zod_1.z.number(),
    "ebitda_year1": zod_1.z.number(),
    "revenue_stabilised": zod_1.z.number(),
    "ebitda_stabilised": zod_1.z.number(),
    "ebitda_margin_stabilised": zod_1.z.number(),
    "ebitda_final_year": zod_1.z.number(),
    "project_irr_pct": metric,
    "payback_years": metric,
    "cumulative_fcf": zod_1.z.number(),
});
const GgvScenariosUpsideMultipliersSchema = zod_1.z.object({
    "footfall": zod_1.z.number(),
    "yield": zod_1.z.number(),
    "opex": zod_1.z.number(),
});
const GgvScenariosUpsideSchema = zod_1.z.object({
    "note": zod_1.z.string(),
    "multipliers": GgvScenariosUpsideMultipliersSchema,
    "revenue_year1": zod_1.z.number(),
    "ebitda_year1": zod_1.z.number(),
    "revenue_stabilised": zod_1.z.number(),
    "ebitda_stabilised": zod_1.z.number(),
    "ebitda_margin_stabilised": zod_1.z.number(),
    "ebitda_final_year": zod_1.z.number(),
    "project_irr_pct": metric,
    "payback_years": metric,
    "cumulative_fcf": zod_1.z.number(),
});
const GgvScenariosSchema = zod_1.z.object({
    "downside": GgvScenariosDownsideSchema,
    "base": GgvScenariosBaseSchema,
    "upside": GgvScenariosUpsideSchema,
});
const GgvSchema = zod_1.z.object({
    "rfp": GgvRfpSchema,
    "bid_licence_year1": zod_1.z.number(),
    "capex_lines": zod_1.z.array(GgvCapexLinesRowSchema).nonempty(),
    "mobilisation": GgvMobilisationSchema,
    "years": zod_1.z.array(GgvYearsRowSchema).min(7),
    "year1_opex": zod_1.z.number(),
    "funding_ask": zod_1.z.number(),
    "peak_cash_deficit": zod_1.z.number(),
    "annual_depreciation": zod_1.z.number(),
    "cost_ratios": GgvCostRatiosSchema,
    "growth_capex": GgvGrowthCapexSchema,
    "financing": GgvFinancingSchema,
    "scenarios": GgvScenariosSchema,
});
const RvRfpMinManpowerPerShiftSchema = zod_1.z.object({
    "sweepers": zod_1.z.number(),
    "security": zod_1.z.number(),
});
const RvRfpMinManpowerPerDaySchema = zod_1.z.object({
    "mali_gardener": zod_1.z.number(),
    "site_manager": zod_1.z.number(),
    "electrician": zod_1.z.number(),
    "plumber": zod_1.z.number(),
});
const RvRfpMinManpowerSchema = zod_1.z.object({
    "per_shift": RvRfpMinManpowerPerShiftSchema,
    "per_day": RvRfpMinManpowerPerDaySchema,
});
const RvRfpTechScoreSchema = zod_1.z.object({
    "experience": zod_1.z.number(),
    "financial_strength": zod_1.z.number(),
    "manpower": zod_1.z.number(),
    "om_plan": zod_1.z.number(),
    "technology": zod_1.z.number(),
});
const RvRfpSchema = zod_1.z.object({
    "authority": zod_1.z.string(),
    "site": zod_1.z.string(),
    "area_sqm": zod_1.z.number(),
    "area_acres": zod_1.z.number(),
    "term": zod_1.z.string(),
    "lock_in": zod_1.z.string(),
    "lock_in_conflict": zod_1.z.string(),
    "selection": zod_1.z.string(),
    "reserve_licence_fee_year_lakh": zod_1.z.number(),
    "escalation_pct": zod_1.z.number(),
    "payment_terms": zod_1.z.string(),
    "penal_interest": zod_1.z.string(),
    "emd_lakh": zod_1.z.number(),
    "bid_fee_lakh": zod_1.z.number(),
    "performance_security_lakh": zod_1.z.number(),
    "performance_security_note": zod_1.z.string(),
    "mortgage_prohibition": zod_1.z.string(),
    "shareholding_restriction": zod_1.z.string(),
    "min_manpower": RvRfpMinManpowerSchema,
    "statutory": zod_1.z.string(),
    "bda_free_use_days": zod_1.z.number(),
    "bda_indicative_revenue_cr": zod_1.z.array(zod_1.z.number()).nonempty(),
    "bda_indicative_basis": zod_1.z.string(),
    "assets": zod_1.z.array(zod_1.z.string()).nonempty(),
    "revenue_streams": zod_1.z.array(zod_1.z.string()).nonempty(),
    "tech_score": RvRfpTechScoreSchema,
});
const RvMobilisationSchema = zod_1.z.object({
    "capex_year0": zod_1.z.number(),
    "capex_year2_toy_train": zod_1.z.number(),
    "performance_security": zod_1.z.number(),
    "emd": zod_1.z.number(),
    "bid_fee": zod_1.z.number(),
    "stamp_duty_registration": zod_1.z.number(),
    "advance_licence_fee_q1": zod_1.z.number(),
    "total": zod_1.z.number(),
});
const RvYearsRowRevenueSchema = zod_1.z.object({
    "entry": zod_1.z.number(),
    "show": zod_1.z.number(),
    "fnb": zod_1.z.number(),
    "parking": zod_1.z.number(),
    "events": zod_1.z.number(),
    "ancillary": zod_1.z.number(),
    "toy_train": zod_1.z.number(),
    "total": zod_1.z.number(),
    "footfall_lakh": zod_1.z.number(),
});
const RvYearsRowOpexSchema = zod_1.z.object({
    "licence_fee": zod_1.z.number(),
    "manpower": zod_1.z.number(),
    "electricity": zod_1.z.number(),
    "water_consumables": zod_1.z.number(),
    "horticulture": zod_1.z.number(),
    "show_amc": zod_1.z.number(),
    "statue_upkeep": zod_1.z.number(),
    "repairs": zod_1.z.number(),
    "insurance": zod_1.z.number(),
    "marketing": zod_1.z.number(),
    "fnb_cogs": zod_1.z.number(),
    "it_cctv": zod_1.z.number(),
    "corporate_overhead": zod_1.z.number(),
    "contingency": zod_1.z.number(),
    "total": zod_1.z.number(),
});
const RvYearsRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "revenue": RvYearsRowRevenueSchema,
    "opex": RvYearsRowOpexSchema,
    "ebitda": zod_1.z.number(),
    "ebitda_margin": zod_1.z.number(),
    "depreciation": zod_1.z.number(),
    "ebit": zod_1.z.number(),
});
const RvFinancingEquitySchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "basis": zod_1.z.string(),
    "investment": zod_1.z.number(),
    "stake_pct": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_equity_value": zod_1.z.number(),
    "exit_proceeds": zod_1.z.number(),
    "distributable": zod_1.z.array(zod_1.z.number()).nonempty(),
    "dividends": zod_1.z.array(zod_1.z.number()).nonempty(),
    "flows": zod_1.z.array(zod_1.z.number()).nonempty(),
    "irr_pct": metric,
    "money_multiple": metric,
    "stake_for_18pct": zod_1.z.number(),
    "stake_for_22pct": zod_1.z.number(),
    "stake_for_25pct": zod_1.z.number(),
});
const RvFinancingCcdSchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "basis": zod_1.z.string(),
    "principal": zod_1.z.number(),
    "coupon_pct": zod_1.z.number(),
    "conversion_year": zod_1.z.number(),
    "conversion_stake_pct": zod_1.z.number(),
    "coupon_paid_total": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_equity_value": zod_1.z.number(),
    "exit_proceeds": zod_1.z.number(),
    "distributable": zod_1.z.array(zod_1.z.number()).nonempty(),
    "flows": zod_1.z.array(zod_1.z.number()).nonempty(),
    "irr_pct": metric,
    "money_multiple": metric,
});
const RvFinancingConversionGapValueSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "footfall_lakh": zod_1.z.number(),
    "bda_conversion_pct": zod_1.z.number(),
    "modelled_conversion_pct": zod_1.z.number(),
    "show_tariff_gross": zod_1.z.number(),
    "value_lakh": zod_1.z.number(),
});
const RvFinancingSchema = zod_1.z.object({
    "facility_ask": zod_1.z.number(),
    "true_capital_requirement": GgvFinancingTrueCapitalRequirementSchema,
    "opex_facility": zod_1.z.number(),
    "project_fcf": GgvFinancingProjectFcfSchema,
    "cost_of_capital": GgvFinancingCostOfCapitalSchema,
    "debt": GgvFinancingDebtSchema,
    "equity": RvFinancingEquitySchema,
    "ccd": RvFinancingCcdSchema,
    "exit_equity_value": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_valuation": GgvFinancingExitValuationSchema,
    "debt_optimised": GgvFinancingDebtSchema,
    "agf_saving_optimised": zod_1.z.number(),
    "conversion_gap_value": RvFinancingConversionGapValueSchema,
    "debt_capacity": GgvFinancingDebtCapacitySchema,
});
const RvScenariosBdaIndicativeMultipliersSchema = zod_1.z.object({
    "footfall": zod_1.z.number(),
    "yield": zod_1.z.number(),
});
const RvScenariosBdaIndicativeSchema = zod_1.z.object({
    "note": zod_1.z.string(),
    "multipliers": RvScenariosBdaIndicativeMultipliersSchema,
    "revenue_year1": zod_1.z.number(),
    "ebitda_year1": zod_1.z.number(),
    "revenue_stabilised": zod_1.z.number(),
    "ebitda_stabilised": zod_1.z.number(),
    "ebitda_margin_stabilised": zod_1.z.number(),
    "ebitda_final_year": zod_1.z.number(),
    "project_irr_pct": metric,
    "payback_years": metric,
    "cumulative_fcf": zod_1.z.number(),
});
const RvScenariosSchema = zod_1.z.object({
    "downside": GgvScenariosDownsideSchema,
    "base": GgvScenariosBaseSchema,
    "bda_indicative": RvScenariosBdaIndicativeSchema,
});
const RvSchema = zod_1.z.object({
    "rfp": RvRfpSchema,
    "bid_licence_year1": zod_1.z.number(),
    "capex_lines": zod_1.z.array(GgvCapexLinesRowSchema).nonempty(),
    "mobilisation": RvMobilisationSchema,
    "years": zod_1.z.array(RvYearsRowSchema).min(10),
    "opex_year1": zod_1.z.number(),
    "opex_year2": zod_1.z.number(),
    "two_year_opex": zod_1.z.number(),
    "facility_ask": zod_1.z.number(),
    "net_drawdown_requirement": zod_1.z.number(),
    "annual_depreciation_full": zod_1.z.number(),
    "financing": RvFinancingSchema,
    "scenarios": RvScenariosSchema,
});
const KarnalFactsSchema = zod_1.z.object({
    "site": zod_1.z.string(),
    "counterparty": zod_1.z.string(),
    "area_sqft": zod_1.z.number(),
    "term_years": zod_1.z.number(),
    "minimum_guarantee_month_lakh": zod_1.z.array(zod_1.z.number()).nonempty(),
    "rent_free": zod_1.z.string(),
    "status": zod_1.z.string(),
    "phase1_capex_cr": zod_1.z.number(),
    "build_months": zod_1.z.number(),
    "open_estimate": zod_1.z.string(),
    "deck_revenue_fy2728_cr": zod_1.z.array(zod_1.z.number()).nonempty(),
    "deck_revenue_fy2829_cr": zod_1.z.array(zod_1.z.number()).nonempty(),
    "area_discrepancy": zod_1.z.string(),
});
const KarnalYearsRowOpexSchema = zod_1.z.object({
    "minimum_guarantee": zod_1.z.number(),
    "manpower": zod_1.z.number(),
    "electricity": zod_1.z.number(),
    "activity_consumables_amc": zod_1.z.number(),
    "repairs": zod_1.z.number(),
    "marketing": zod_1.z.number(),
    "admin_overhead": zod_1.z.number(),
    "insurance_statutory": zod_1.z.number(),
    "fnb_cogs": zod_1.z.number(),
    "total": zod_1.z.number(),
});
const KarnalYearsRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "revenue": zod_1.z.number(),
    "opex": KarnalYearsRowOpexSchema,
    "ebitda": zod_1.z.number(),
    "ebitda_margin": zod_1.z.number(),
    "depreciation": zod_1.z.number(),
    "ebit": zod_1.z.number(),
});
const KarnalFinancingDebtSchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "term_loan": zod_1.z.number(),
    "wc_limit": zod_1.z.number(),
    "total_limit": zod_1.z.number(),
    "rate_pct": zod_1.z.number(),
    "tl_tenor_years": zod_1.z.number(),
    "tl_moratorium_years": zod_1.z.number(),
    "cgtmse": GgvFinancingDebtCgtmseSchema,
    "schedule": zod_1.z.array(GgvFinancingDebtScheduleRowSchema).nonempty(),
    "min_dscr": metric,
    "avg_dscr": metric,
    "min_dscr_post_moratorium": metric,
    "avg_dscr_post_moratorium": metric,
    "bankable": zod_1.z.boolean(),
    "total_interest": zod_1.z.number(),
    "total_agf": zod_1.z.number(),
    "total_finance_cost": zod_1.z.number(),
    "promoter_contribution": zod_1.z.number(),
    "promoter_margin_pct": zod_1.z.number(),
});
const KarnalFinancingExitValuationSchema = zod_1.z.object({
    "dcf_remaining_term": zod_1.z.number(),
    "ebitda_multiple_crosscheck": zod_1.z.number(),
    "exit_year_ebitda": zod_1.z.number(),
    "ebitda_multiple": zod_1.z.number(),
    "discount_rate_pct": zod_1.z.number(),
    "used": zod_1.z.number(),
    "basis": zod_1.z.string(),
    "beyond_model_horizon": zod_1.z.number(),
});
const KarnalFinancingSchema = zod_1.z.object({
    "project_cost": zod_1.z.number(),
    "true_capital_requirement": GgvFinancingTrueCapitalRequirementSchema,
    "project_fcf": GgvFinancingProjectFcfSchema,
    "cost_of_capital": GgvFinancingCostOfCapitalSchema,
    "debt": KarnalFinancingDebtSchema,
    "equity": RvFinancingEquitySchema,
    "ccd": RvFinancingCcdSchema,
    "exit_equity_value": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_valuation": KarnalFinancingExitValuationSchema,
    "debt_capacity": GgvFinancingDebtCapacitySchema,
});
const KarnalScenariosDownsideMultipliersSchema = zod_1.z.object({
    "footfall": zod_1.z.number(),
    "opex": zod_1.z.number(),
});
const KarnalScenariosDownsideSchema = zod_1.z.object({
    "note": zod_1.z.string(),
    "multipliers": KarnalScenariosDownsideMultipliersSchema,
    "revenue_year1": zod_1.z.number(),
    "ebitda_year1": zod_1.z.number(),
    "revenue_stabilised": zod_1.z.number(),
    "ebitda_stabilised": zod_1.z.number(),
    "ebitda_margin_stabilised": zod_1.z.number(),
    "ebitda_final_year": zod_1.z.number(),
    "project_irr_pct": metric,
    "payback_years": metric,
    "cumulative_fcf": zod_1.z.number(),
});
const KarnalScenariosSchema = zod_1.z.object({
    "downside": KarnalScenariosDownsideSchema,
    "base": GgvScenariosBaseSchema,
    "upside": KarnalScenariosDownsideSchema,
});
const KarnalSchema = zod_1.z.object({
    "facts": KarnalFactsSchema,
    "capex_lines": zod_1.z.array(GgvCapexLinesRowSchema).nonempty(),
    "capex_total": zod_1.z.number(),
    "years": zod_1.z.array(KarnalYearsRowSchema).min(5),
    "annual_depreciation": zod_1.z.number(),
    "financing": KarnalFinancingSchema,
    "scenarios": KarnalScenariosSchema,
});
const ConsolidatedYearsRowPartsExistingSchema = zod_1.z.object({
    "revenue": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
});
const ConsolidatedYearsRowPartsSchema = zod_1.z.object({
    "existing": ConsolidatedYearsRowPartsExistingSchema,
    "ggv": ConsolidatedYearsRowPartsExistingSchema,
    "rv": ConsolidatedYearsRowPartsExistingSchema,
    "karnal": ConsolidatedYearsRowPartsExistingSchema,
});
const ConsolidatedYearsRowSchema = zod_1.z.object({
    "fy": zod_1.z.string(),
    "parts": ConsolidatedYearsRowPartsSchema,
    "revenue": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
    "ebitda_margin": zod_1.z.number(),
});
const ConsolidatedSchema = zod_1.z.object({
    "phasing_note": zod_1.z.string(),
    "years": zod_1.z.array(ConsolidatedYearsRowSchema).min(5),
});
const CompanyProfileFy26Schema = zod_1.z.object({
    "revenue": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
    "pat": zod_1.z.number(),
    "net_worth": zod_1.z.number(),
    "reserves": zod_1.z.number(),
    "borrowings_short": zod_1.z.number(),
    "borrowings_long_related": zod_1.z.number(),
    "borrowings_total": zod_1.z.number(),
    "cash": zod_1.z.number(),
    "fdr": zod_1.z.number(),
    "gross_block": zod_1.z.number(),
    "net_block": zod_1.z.number(),
    "electricity_arrears": zod_1.z.number(),
    "finance_cost_total": zod_1.z.number(),
    "trade_payables": zod_1.z.number(),
    "other_current_liabilities": zod_1.z.number(),
});
const CompanyProfilePromoterRelatedDebtSchema = zod_1.z.object({
    "sanjeev_bewtra_and_team_buildcon_lt": zod_1.z.number(),
    "promoter_loans_fy26": zod_1.z.number(),
    "apoorv_babbar_huf": zod_1.z.number(),
    "geetika_jain": zod_1.z.number(),
});
const CompanyProfileProjectionsFY2627Schema = zod_1.z.object({
    "revenue": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
    "pat": zod_1.z.number(),
});
const CompanyProfileProjectionsSchema = zod_1.z.object({
    "FY26-27": CompanyProfileProjectionsFY2627Schema,
    "FY27-28": CompanyProfileProjectionsFY2627Schema,
    "FY28-29": CompanyProfileProjectionsFY2627Schema,
});
const CompanyProfileExistingRaiseSchema = zod_1.z.object({
    "amount_cr": zod_1.z.number(),
    "pre_money_cr": zod_1.z.number(),
    "dilution_pct": zod_1.z.number(),
});
const CompanyProfileSubhashParkSchema = zod_1.z.object({
    "opened": zod_1.z.string(),
    "fy2627_revenue_to_date_lakh": zod_1.z.number(),
    "fy2627_months_elapsed": zod_1.z.number(),
    "fy2627_run_rate_expectation_lakh": zod_1.z.number(),
    "net_margin_first_four_months_pct": zod_1.z.number(),
});
const CompanyProfileSchema = zod_1.z.object({
    "name": zod_1.z.string(),
    "cin": zod_1.z.string(),
    "share_capital_lakh": zod_1.z.number(),
    "shares_outstanding": zod_1.z.number(),
    "face_value_inr": zod_1.z.number(),
    "fy26": CompanyProfileFy26Schema,
    "promoter_related_debt": CompanyProfilePromoterRelatedDebtSchema,
    "projections": CompanyProfileProjectionsSchema,
    "existing_raise": CompanyProfileExistingRaiseSchema,
    "subhash_park": CompanyProfileSubhashParkSchema,
});
const CompanyMsmeSchema = zod_1.z.object({
    "investment_plant_machinery_cr": zod_1.z.number(),
    "turnover_cr": zod_1.z.number(),
    "classification": zod_1.z.string(),
    "headroom_investment_cr": zod_1.z.number(),
    "headroom_turnover_cr": zod_1.z.number(),
    "cgtmse_eligible": zod_1.z.boolean(),
});
const CompanyRelatedPartyConversionBaseSchema = zod_1.z.object({
    "borrowings": zod_1.z.number(),
    "net_worth": zod_1.z.number(),
    "debt_equity": zod_1.z.number(),
});
const CompanyRelatedPartyConversionConvertLtRelated260Schema = zod_1.z.object({
    "converted": zod_1.z.number(),
    "borrowings": zod_1.z.number(),
    "net_worth": zod_1.z.number(),
    "debt_equity": zod_1.z.number(),
});
const CompanyRelatedPartyConversionSchema = zod_1.z.object({
    "base": CompanyRelatedPartyConversionBaseSchema,
    "convert_lt_related_260": CompanyRelatedPartyConversionConvertLtRelated260Schema,
    "convert_lt_plus_promoter_409": CompanyRelatedPartyConversionConvertLtRelated260Schema,
});
const CompanyExitBasisSchema = zod_1.z.object({
    "fy": zod_1.z.string(),
    "revenue": zod_1.z.number(),
    "ebitda": zod_1.z.number(),
    "ev_revenue_multiple": zod_1.z.number(),
    "enterprise_value": zod_1.z.number(),
    "ev_ebitda_crosscheck": zod_1.z.number(),
    "net_debt": zod_1.z.number(),
    "equity_value": zod_1.z.number(),
});
const CompanyFinancingEquityExistingRoundSchema = zod_1.z.object({
    "amount": zod_1.z.number(),
    "pre_money": zod_1.z.number(),
    "dilution_pct": zod_1.z.number(),
});
const CompanyFinancingEquityPricingSensitivityIrr18Schema = zod_1.z.object({
    "stake_pct": zod_1.z.number(),
    "post_money": zod_1.z.number(),
    "pre_money": zod_1.z.number(),
});
const CompanyFinancingEquityPricingSensitivitySchema = zod_1.z.object({
    "irr_18": CompanyFinancingEquityPricingSensitivityIrr18Schema,
    "irr_22": CompanyFinancingEquityPricingSensitivityIrr18Schema,
    "irr_25": CompanyFinancingEquityPricingSensitivityIrr18Schema,
});
const CompanyFinancingEquitySchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "basis": zod_1.z.string(),
    "investment": zod_1.z.number(),
    "stake_pct": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_equity_value": zod_1.z.number(),
    "exit_proceeds": zod_1.z.number(),
    "distributable": zod_1.z.array(zod_1.z.number()).nonempty(),
    "dividends": zod_1.z.array(zod_1.z.number()).nonempty(),
    "flows": zod_1.z.array(zod_1.z.number()).nonempty(),
    "irr_pct": metric,
    "money_multiple": metric,
    "stake_for_18pct": zod_1.z.number(),
    "stake_for_22pct": zod_1.z.number(),
    "stake_for_25pct": zod_1.z.number(),
    "pre_money": zod_1.z.number(),
    "post_money": zod_1.z.number(),
    "existing_round": CompanyFinancingEquityExistingRoundSchema,
    "pricing_sensitivity": CompanyFinancingEquityPricingSensitivitySchema,
});
const CompanyFinancingDebtCombinedServiceRowSchema = zod_1.z.object({
    "year": zod_1.z.number(),
    "new_facility": zod_1.z.number(),
    "existing_debt": zod_1.z.number(),
    "total_debt_service": zod_1.z.number(),
    "cfads": zod_1.z.number(),
    "dscr": metric,
});
const CompanyFinancingDebtLeverageCasesRowSchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "conversion": zod_1.z.number(),
    "retained_earnings": zod_1.z.number(),
    "net_worth": zod_1.z.number(),
    "borrowings": zod_1.z.number(),
    "debt_equity": zod_1.z.number(),
    "max_facility_at_covenant": zod_1.z.number(),
});
const CompanyFinancingDebtLeverageSchema = zod_1.z.object({
    "covenant_assumed": zod_1.z.number(),
    "cases": zod_1.z.array(CompanyFinancingDebtLeverageCasesRowSchema).min(3),
    "conversion_full": zod_1.z.number(),
});
const CompanyFinancingDebtSchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "term_loan": zod_1.z.number(),
    "wc_limit": zod_1.z.number(),
    "total_limit": zod_1.z.number(),
    "rate_pct": zod_1.z.number(),
    "tl_tenor_years": zod_1.z.number(),
    "tl_moratorium_years": zod_1.z.number(),
    "cgtmse": GgvFinancingDebtCgtmseSchema,
    "schedule": zod_1.z.array(GgvFinancingDebtScheduleRowSchema).nonempty(),
    "min_dscr": metric,
    "avg_dscr": metric,
    "min_dscr_post_moratorium": metric,
    "avg_dscr_post_moratorium": metric,
    "bankable": zod_1.z.boolean(),
    "total_interest": zod_1.z.number(),
    "total_agf": zod_1.z.number(),
    "total_finance_cost": zod_1.z.number(),
    "combined_service": zod_1.z.array(CompanyFinancingDebtCombinedServiceRowSchema).nonempty(),
    "min_dscr_combined": zod_1.z.number(),
    "avg_dscr_combined": zod_1.z.number(),
    "nbfc_refinance": zod_1.z.number(),
    "leverage": CompanyFinancingDebtLeverageSchema,
});
const CompanyFinancingCcdSchema = zod_1.z.object({
    "label": zod_1.z.string(),
    "basis": zod_1.z.string(),
    "principal": zod_1.z.number(),
    "coupon_pct": zod_1.z.number(),
    "conversion_year": zod_1.z.number(),
    "conversion_stake_pct": zod_1.z.number(),
    "coupon_paid_total": zod_1.z.number(),
    "exit_year": zod_1.z.number(),
    "exit_equity_value": zod_1.z.number(),
    "exit_proceeds": zod_1.z.number(),
    "distributable": zod_1.z.array(zod_1.z.number()).nonempty(),
    "flows": zod_1.z.array(zod_1.z.number()).nonempty(),
    "irr_pct": metric,
    "money_multiple": metric,
    "conversion_valuation_implied": zod_1.z.number(),
    "balance_sheet_note": zod_1.z.string(),
});
const CompanyFinancingSchema = zod_1.z.object({
    "equity": CompanyFinancingEquitySchema,
    "debt": CompanyFinancingDebtSchema,
    "ccd": CompanyFinancingCcdSchema,
});
const CompanySchema = zod_1.z.object({
    "profile": CompanyProfileSchema,
    "msme": CompanyMsmeSchema,
    "related_party_conversion": CompanyRelatedPartyConversionSchema,
    "exit_basis": CompanyExitBasisSchema,
    "financing": CompanyFinancingSchema,
});
const CgtmseAllocationSchema = zod_1.z.object({
    "ceiling": zod_1.z.number(),
    "ceiling_basis": zod_1.z.string(),
    "gross_demand": zod_1.z.object({ "Geeta Govind Vatika — composite": zod_1.z.number(), "Ramayan Vatika — composite": zod_1.z.number(), "Karnal Phase 1 — term loan + WC": zod_1.z.number(), "VAPPL — working capital and NBFC consolidation": zod_1.z.number() }),
    "total_gross_demand": zod_1.z.number(),
    "excess_over_ceiling": zod_1.z.number(),
    "single_borrower_plan": zod_1.z.object({ "Karnal Phase 1 — term loan": zod_1.z.number(), "Ramayan Vatika — term loan + standby WC": zod_1.z.number(), "Geeta Govind Vatika — term loan + standby WC": zod_1.z.number(), "VAPPL — working capital, NBFC consolidation": zod_1.z.number() }),
    "single_borrower_plan_total": zod_1.z.number(),
    "headroom": zod_1.z.number(),
    "residual_to_fund_outside_cgtmse": zod_1.z.number(),
});
exports.financeModelSchema = zod_1.z.object({
    meta: MetaSchema,
    cgtmse: CgtmseSchema,
    msme_limits: MsmeLimitsSchema,
    ggv: GgvSchema,
    rv: RvSchema,
    karnal: KarnalSchema,
    consolidated: ConsolidatedSchema,
    company: CompanySchema,
    cgtmse_allocation: CgtmseAllocationSchema,
});
//# sourceMappingURL=finance-contract.js.map