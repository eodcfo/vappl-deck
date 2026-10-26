import { z } from "zod";

// Python is the calculation owner. This boundary checks its JSON exchange shape;
// it never recomputes financial results or converts units. Money is INR lakh,
// except explicitly named _cr fields. Null metrics mean no defined result.
const metric = z.number().nullable();
const MetaSchema = z.object({
  "entity": z.string(),
  "cin": z.string(),
  "prepared": z.string(),
  "units": z.literal("INR lakh unless stated"),
  "generator": z.literal("model/pf_model.py"),
  "tax_rate_pct": z.number(),
  "bank_rate_pct": z.number(),
});

const CgtmseSchema = z.object({
  "scheme": z.string(),
  "ceiling_per_borrower_cr": z.number(),
  "ceiling_startup_dpiit_cr": z.number(),
  "ceiling_basis": z.string(),
  "coverage_small_enterprise_pct": z.number(),
  "coverage_preferential_pct": z.number(),
  "interest_cap_note": z.string(),
  "agf_slabs": z.array(z.tuple([z.number(),z.number()])).nonempty(),
  "agf_basis_y1": z.string(),
  "agf_basis_y2plus": z.string(),
  "agf_concession_pct": z.number(),
  "hybrid_security": z.boolean(),
  "collateral": z.string(),
  "third_party_guarantee": z.string(),
});

const MsmeLimitsMicroSchema = z.object({
  "investment_cr": z.number(),
  "turnover_cr": z.number(),
});

const MsmeLimitsSchema = z.object({
  "micro": MsmeLimitsMicroSchema,
  "small": MsmeLimitsMicroSchema,
  "medium": MsmeLimitsMicroSchema,
});

const GgvRfpSchema = z.object({
  "authority": z.string(),
  "site": z.string(),
  "area_acres": z.number(),
  "term": z.string(),
  "selection": z.string(),
  "reserve_licence_fee_month_lakh": z.number(),
  "reserve_licence_fee_year_lakh": z.number(),
  "escalation_pct": z.number(),
  "emd_lakh": z.number(),
  "tender_fee_lakh": z.number(),
  "security_deposit_basis": z.string(),
  "payment_terms": z.string(),
  "moratorium_days": z.number(),
  "entry_tariff_inr": z.number(),
  "free_entry": z.string(),
  "show_tariff": z.string(),
  "penalty_range_inr": z.string(),
  "eligibility_turnover_cr": z.number(),
  "eligibility_projects": z.string(),
  "assets": z.string(),
  "scope": z.array(z.string()).nonempty(),
});

const GgvCapexLinesRowSchema = z.object({
  "item": z.string(),
  "amount": z.number(),
  "life_years": z.number(),
});

const GgvMobilisationSchema = z.object({
  "capex": z.number(),
  "security_deposit": z.number(),
  "advance_licence_fee_6m": z.number(),
  "emd": z.number(),
  "tender_fee": z.number(),
  "total": z.number(),
  "working_capital": z.number(),
  "ask": z.number(),
});

const GgvYearsRowRevenueSchema = z.object({
  "entry": z.number(),
  "show": z.number(),
  "fnb": z.number(),
  "activities": z.number(),
  "activities_gross": z.number(),
  "activities_owned_frac": z.number(),
  "parking": z.number(),
  "events_public": z.number(),
  "events_private": z.number(),
  "events": z.number(),
  "total": z.number(),
  "footfall_lakh": z.number(),
});

const GgvYearsRowOpexSchema = z.object({
  "licence_fee": z.number(),
  "manpower": z.number(),
  "electricity": z.number(),
  "water_horticulture": z.number(),
  "show_amc": z.number(),
  "repairs": z.number(),
  "fnb_cogs": z.number(),
  "activity_cost": z.number(),
  "events_cost": z.number(),
  "marketing": z.number(),
  "insurance_statutory": z.number(),
  "it_cctv": z.number(),
  "corporate_overhead": z.number(),
  "contingency": z.number(),
  "total": z.number(),
});

const GgvYearsRowSchema = z.object({
  "year": z.number(),
  "revenue": GgvYearsRowRevenueSchema,
  "opex": GgvYearsRowOpexSchema,
  "ebitda": z.number(),
  "ebitda_margin": z.number(),
  "depreciation": z.number(),
  "ebit": z.number(),
  "growth_capex": z.number(),
});

const GgvCostRatiosSchema = z.object({
  "public_event_delivery_pct": z.number(),
  "private_event_delivery_pct": z.number(),
  "fnb_cogs_pct": z.number(),
});

const GgvGrowthCapexSchema = z.object({
  "year": z.number(),
  "lines": z.array(GgvCapexLinesRowSchema).min(2),
  "total": z.number(),
  "annual_depreciation": z.number(),
  "owned_activity_fraction_pct": z.array(z.number()).min(7),
  "owned_activity_cost_ratio_pct": z.number(),
});

const GgvFinancingTrueCapitalRequirementSchema = z.object({
  "mobilisation": z.number(),
  "later_capex": z.number(),
  "cumulative_operating_deficit": z.number(),
  "total": z.number(),
});

const GgvFinancingProjectFcfDetailRowSchema = z.object({
  "year": z.number(),
  "ebitda": z.number(),
  "tax": z.number(),
  "maintenance_capex": z.number(),
  "growth_capex": z.number(),
  "terminal_inflow": z.number(),
  "fcf": z.number(),
});

const GgvFinancingProjectFcfSchema = z.object({
  "t0": z.number(),
  "terminal_inflow": z.number(),
  "flows": z.array(z.number()).nonempty(),
  "detail": z.array(GgvFinancingProjectFcfDetailRowSchema).nonempty(),
  "irr_pct": metric,
  "npv_at_15pct": z.number(),
  "payback_years": metric,
  "cumulative_fcf": z.number(),
  "cumulative_fcf_net_of_capital": z.number(),
});

const GgvFinancingCostOfCapitalSchema = z.object({
  "project_irr_pct": metric,
  "all_in_cost_of_cgtmse_debt_pct": z.number(),
  "equity_hurdle_pct": z.number(),
  "spread_over_debt_pct": metric,
  "clears_debt": z.boolean(),
  "clears_equity_hurdle": z.boolean(),
  "verdict": z.string(),
});

const GgvFinancingDebtCgtmseSchema = z.object({
  "agf_rate_pct": z.number(),
  "agf_slab": z.string(),
  "coverage_pct": z.number(),
  "guaranteed_amount": z.number(),
  "uncovered_amount": z.number(),
  "within_ceiling": z.boolean(),
});

const GgvFinancingDebtScheduleRowSchema = z.object({
  "year": z.number(),
  "tl_opening": z.number(),
  "tl_interest": z.number(),
  "wc_outstanding": z.number(),
  "wc_interest": z.number(),
  "agf": z.number(),
  "principal": z.number(),
  "tl_closing": z.number(),
  "debt_service": z.number(),
  "cfads": z.number(),
  "dscr": metric,
});

const GgvFinancingDebtSchema = z.object({
  "label": z.string(),
  "term_loan": z.number(),
  "wc_limit": z.number(),
  "total_limit": z.number(),
  "rate_pct": z.number(),
  "tl_tenor_years": z.number(),
  "tl_moratorium_years": z.number(),
  "cgtmse": GgvFinancingDebtCgtmseSchema,
  "schedule": z.array(GgvFinancingDebtScheduleRowSchema).nonempty(),
  "min_dscr": metric,
  "avg_dscr": metric,
  "min_dscr_post_moratorium": metric,
  "avg_dscr_post_moratorium": metric,
  "bankable": z.boolean(),
  "total_interest": z.number(),
  "total_agf": z.number(),
  "total_finance_cost": z.number(),
});

const GgvFinancingExitValuationSchema = z.object({
  "dcf_remaining_term": z.number(),
  "ebitda_multiple_crosscheck": z.number(),
  "exit_year_ebitda": z.number(),
  "ebitda_multiple": z.number(),
  "discount_rate_pct": z.number(),
  "used": z.number(),
  "basis": z.string(),
});

const GgvFinancingShowTariffSensitivitySchema = z.object({
  "year": z.number(),
  "footfall_lakh": z.number(),
  "show_conversion_pct": z.number(),
  "value_per_rupee_of_tariff_lakh": z.number(),
});

const GgvFinancingCashWaterfallDetailRowSchema = z.object({
  "year": z.number(),
  "ebitda": z.number(),
  "tax": z.number(),
  "maintenance_capex": z.number(),
  "growth_capex": z.number(),
  "debt_service": z.number(),
  "net": z.number(),
  "closing_cash": z.number(),
});

const GgvFinancingCashWaterfallSchema = z.object({
  "opening_cash": z.number(),
  "detail": z.array(GgvFinancingCashWaterfallDetailRowSchema).nonempty(),
  "lowest_balance": z.number(),
  "closing_cash": z.number(),
  "self_funding": z.boolean(),
});

const GgvFinancingDebtCapacitySchema = z.object({
  "target_dscr": z.number(),
  "max_total_limit": z.number(),
  "max_term_loan": z.number(),
  "max_wc_limit": z.number(),
  "achieved_min_dscr": metric,
  "facility": GgvFinancingDebtSchema,
});

const GgvFinancingSchema = z.object({
  "ask": z.number(),
  "true_capital_requirement": GgvFinancingTrueCapitalRequirementSchema,
  "opex_facility": z.number(),
  "project_fcf": GgvFinancingProjectFcfSchema,
  "cost_of_capital": GgvFinancingCostOfCapitalSchema,
  "debt": GgvFinancingDebtSchema,
  "instruments": z.array(z.string()).nonempty(),
  "exit_equity_value": z.number(),
  "exit_year": z.number(),
  "exit_valuation": GgvFinancingExitValuationSchema,
  "debt_optimised": GgvFinancingDebtSchema,
  "agf_saving_optimised": z.number(),
  "show_tariff_sensitivity": GgvFinancingShowTariffSensitivitySchema,
  "cash_waterfall": GgvFinancingCashWaterfallSchema,
  "debt_capacity": GgvFinancingDebtCapacitySchema,
});

const GgvScenariosDownsideMultipliersSchema = z.object({
  "footfall": z.number(),
  "yield": z.number(),
  "opex": z.number(),
  "licence": z.number(),
});

const GgvScenariosDownsideSchema = z.object({
  "note": z.string(),
  "multipliers": GgvScenariosDownsideMultipliersSchema,
  "revenue_year1": z.number(),
  "ebitda_year1": z.number(),
  "revenue_stabilised": z.number(),
  "ebitda_stabilised": z.number(),
  "ebitda_margin_stabilised": z.number(),
  "ebitda_final_year": z.number(),
  "project_irr_pct": metric,
  "payback_years": metric,
  "cumulative_fcf": z.number(),
});

const GgvScenariosBaseMultipliersSchema = z.object({

});

const GgvScenariosBaseSchema = z.object({
  "note": z.string(),
  "multipliers": GgvScenariosBaseMultipliersSchema,
  "revenue_year1": z.number(),
  "ebitda_year1": z.number(),
  "revenue_stabilised": z.number(),
  "ebitda_stabilised": z.number(),
  "ebitda_margin_stabilised": z.number(),
  "ebitda_final_year": z.number(),
  "project_irr_pct": metric,
  "payback_years": metric,
  "cumulative_fcf": z.number(),
});

const GgvScenariosUpsideMultipliersSchema = z.object({
  "footfall": z.number(),
  "yield": z.number(),
  "opex": z.number(),
});

const GgvScenariosUpsideSchema = z.object({
  "note": z.string(),
  "multipliers": GgvScenariosUpsideMultipliersSchema,
  "revenue_year1": z.number(),
  "ebitda_year1": z.number(),
  "revenue_stabilised": z.number(),
  "ebitda_stabilised": z.number(),
  "ebitda_margin_stabilised": z.number(),
  "ebitda_final_year": z.number(),
  "project_irr_pct": metric,
  "payback_years": metric,
  "cumulative_fcf": z.number(),
});

const GgvScenariosSchema = z.object({
  "downside": GgvScenariosDownsideSchema,
  "base": GgvScenariosBaseSchema,
  "upside": GgvScenariosUpsideSchema,
});

const GgvSchema = z.object({
  "rfp": GgvRfpSchema,
  "bid_licence_year1": z.number(),
  "capex_lines": z.array(GgvCapexLinesRowSchema).nonempty(),
  "mobilisation": GgvMobilisationSchema,
  "years": z.array(GgvYearsRowSchema).min(7),
  "year1_opex": z.number(),
  "funding_ask": z.number(),
  "peak_cash_deficit": z.number(),
  "annual_depreciation": z.number(),
  "cost_ratios": GgvCostRatiosSchema,
  "growth_capex": GgvGrowthCapexSchema,
  "financing": GgvFinancingSchema,
  "scenarios": GgvScenariosSchema,
});

const RvRfpMinManpowerPerShiftSchema = z.object({
  "sweepers": z.number(),
  "security": z.number(),
});

const RvRfpMinManpowerPerDaySchema = z.object({
  "mali_gardener": z.number(),
  "site_manager": z.number(),
  "electrician": z.number(),
  "plumber": z.number(),
});

const RvRfpMinManpowerSchema = z.object({
  "per_shift": RvRfpMinManpowerPerShiftSchema,
  "per_day": RvRfpMinManpowerPerDaySchema,
});

const RvRfpTechScoreSchema = z.object({
  "experience": z.number(),
  "financial_strength": z.number(),
  "manpower": z.number(),
  "om_plan": z.number(),
  "technology": z.number(),
});

const RvRfpSchema = z.object({
  "authority": z.string(),
  "site": z.string(),
  "area_sqm": z.number(),
  "area_acres": z.number(),
  "term": z.string(),
  "lock_in": z.string(),
  "lock_in_conflict": z.string(),
  "selection": z.string(),
  "reserve_licence_fee_year_lakh": z.number(),
  "escalation_pct": z.number(),
  "payment_terms": z.string(),
  "penal_interest": z.string(),
  "emd_lakh": z.number(),
  "bid_fee_lakh": z.number(),
  "performance_security_lakh": z.number(),
  "performance_security_note": z.string(),
  "mortgage_prohibition": z.string(),
  "shareholding_restriction": z.string(),
  "min_manpower": RvRfpMinManpowerSchema,
  "statutory": z.string(),
  "bda_free_use_days": z.number(),
  "bda_indicative_revenue_cr": z.array(z.number()).nonempty(),
  "bda_indicative_basis": z.string(),
  "assets": z.array(z.string()).nonempty(),
  "revenue_streams": z.array(z.string()).nonempty(),
  "tech_score": RvRfpTechScoreSchema,
});

const RvMobilisationSchema = z.object({
  "capex_year0": z.number(),
  "capex_year2_toy_train": z.number(),
  "performance_security": z.number(),
  "emd": z.number(),
  "bid_fee": z.number(),
  "stamp_duty_registration": z.number(),
  "advance_licence_fee_q1": z.number(),
  "total": z.number(),
});

const RvYearsRowRevenueSchema = z.object({
  "entry": z.number(),
  "show": z.number(),
  "fnb": z.number(),
  "parking": z.number(),
  "events": z.number(),
  "ancillary": z.number(),
  "toy_train": z.number(),
  "total": z.number(),
  "footfall_lakh": z.number(),
});

const RvYearsRowOpexSchema = z.object({
  "licence_fee": z.number(),
  "manpower": z.number(),
  "electricity": z.number(),
  "water_consumables": z.number(),
  "horticulture": z.number(),
  "show_amc": z.number(),
  "statue_upkeep": z.number(),
  "repairs": z.number(),
  "insurance": z.number(),
  "marketing": z.number(),
  "fnb_cogs": z.number(),
  "it_cctv": z.number(),
  "corporate_overhead": z.number(),
  "contingency": z.number(),
  "total": z.number(),
});

const RvYearsRowSchema = z.object({
  "year": z.number(),
  "revenue": RvYearsRowRevenueSchema,
  "opex": RvYearsRowOpexSchema,
  "ebitda": z.number(),
  "ebitda_margin": z.number(),
  "depreciation": z.number(),
  "ebit": z.number(),
});

const RvFinancingEquitySchema = z.object({
  "label": z.string(),
  "basis": z.string(),
  "investment": z.number(),
  "stake_pct": z.number(),
  "exit_year": z.number(),
  "exit_equity_value": z.number(),
  "exit_proceeds": z.number(),
  "distributable": z.array(z.number()).nonempty(),
  "dividends": z.array(z.number()).nonempty(),
  "flows": z.array(z.number()).nonempty(),
  "irr_pct": metric,
  "money_multiple": metric,
  "stake_for_18pct": z.number(),
  "stake_for_22pct": z.number(),
  "stake_for_25pct": z.number(),
});

const RvFinancingCcdSchema = z.object({
  "label": z.string(),
  "basis": z.string(),
  "principal": z.number(),
  "coupon_pct": z.number(),
  "conversion_year": z.number(),
  "conversion_stake_pct": z.number(),
  "coupon_paid_total": z.number(),
  "exit_year": z.number(),
  "exit_equity_value": z.number(),
  "exit_proceeds": z.number(),
  "distributable": z.array(z.number()).nonempty(),
  "flows": z.array(z.number()).nonempty(),
  "irr_pct": metric,
  "money_multiple": metric,
});

const RvFinancingConversionGapValueSchema = z.object({
  "year": z.number(),
  "footfall_lakh": z.number(),
  "bda_conversion_pct": z.number(),
  "modelled_conversion_pct": z.number(),
  "show_tariff_gross": z.number(),
  "value_lakh": z.number(),
});

const RvFinancingSchema = z.object({
  "facility_ask": z.number(),
  "true_capital_requirement": GgvFinancingTrueCapitalRequirementSchema,
  "opex_facility": z.number(),
  "project_fcf": GgvFinancingProjectFcfSchema,
  "cost_of_capital": GgvFinancingCostOfCapitalSchema,
  "debt": GgvFinancingDebtSchema,
  "equity": RvFinancingEquitySchema,
  "ccd": RvFinancingCcdSchema,
  "exit_equity_value": z.number(),
  "exit_year": z.number(),
  "exit_valuation": GgvFinancingExitValuationSchema,
  "debt_optimised": GgvFinancingDebtSchema,
  "agf_saving_optimised": z.number(),
  "conversion_gap_value": RvFinancingConversionGapValueSchema,
  "debt_capacity": GgvFinancingDebtCapacitySchema,
});

const RvScenariosBdaIndicativeMultipliersSchema = z.object({
  "footfall": z.number(),
  "yield": z.number(),
});

const RvScenariosBdaIndicativeSchema = z.object({
  "note": z.string(),
  "multipliers": RvScenariosBdaIndicativeMultipliersSchema,
  "revenue_year1": z.number(),
  "ebitda_year1": z.number(),
  "revenue_stabilised": z.number(),
  "ebitda_stabilised": z.number(),
  "ebitda_margin_stabilised": z.number(),
  "ebitda_final_year": z.number(),
  "project_irr_pct": metric,
  "payback_years": metric,
  "cumulative_fcf": z.number(),
});

const RvScenariosSchema = z.object({
  "downside": GgvScenariosDownsideSchema,
  "base": GgvScenariosBaseSchema,
  "bda_indicative": RvScenariosBdaIndicativeSchema,
});

const RvSchema = z.object({
  "rfp": RvRfpSchema,
  "bid_licence_year1": z.number(),
  "capex_lines": z.array(GgvCapexLinesRowSchema).nonempty(),
  "mobilisation": RvMobilisationSchema,
  "years": z.array(RvYearsRowSchema).min(10),
  "opex_year1": z.number(),
  "opex_year2": z.number(),
  "two_year_opex": z.number(),
  "facility_ask": z.number(),
  "net_drawdown_requirement": z.number(),
  "annual_depreciation_full": z.number(),
  "financing": RvFinancingSchema,
  "scenarios": RvScenariosSchema,
});

const KarnalFactsSchema = z.object({
  "site": z.string(),
  "counterparty": z.string(),
  "area_sqft": z.number(),
  "term_years": z.number(),
  "minimum_guarantee_month_lakh": z.array(z.number()).nonempty(),
  "rent_free": z.string(),
  "status": z.string(),
  "phase1_capex_cr": z.number(),
  "build_months": z.number(),
  "open_estimate": z.string(),
  "deck_revenue_fy2728_cr": z.array(z.number()).nonempty(),
  "deck_revenue_fy2829_cr": z.array(z.number()).nonempty(),
  "area_discrepancy": z.string(),
});

const KarnalYearsRowOpexSchema = z.object({
  "minimum_guarantee": z.number(),
  "manpower": z.number(),
  "electricity": z.number(),
  "activity_consumables_amc": z.number(),
  "repairs": z.number(),
  "marketing": z.number(),
  "admin_overhead": z.number(),
  "insurance_statutory": z.number(),
  "fnb_cogs": z.number(),
  "total": z.number(),
});

const KarnalYearsRowSchema = z.object({
  "year": z.number(),
  "revenue": z.number(),
  "opex": KarnalYearsRowOpexSchema,
  "ebitda": z.number(),
  "ebitda_margin": z.number(),
  "depreciation": z.number(),
  "ebit": z.number(),
});

const KarnalFinancingDebtSchema = z.object({
  "label": z.string(),
  "term_loan": z.number(),
  "wc_limit": z.number(),
  "total_limit": z.number(),
  "rate_pct": z.number(),
  "tl_tenor_years": z.number(),
  "tl_moratorium_years": z.number(),
  "cgtmse": GgvFinancingDebtCgtmseSchema,
  "schedule": z.array(GgvFinancingDebtScheduleRowSchema).nonempty(),
  "min_dscr": metric,
  "avg_dscr": metric,
  "min_dscr_post_moratorium": metric,
  "avg_dscr_post_moratorium": metric,
  "bankable": z.boolean(),
  "total_interest": z.number(),
  "total_agf": z.number(),
  "total_finance_cost": z.number(),
  "promoter_contribution": z.number(),
  "promoter_margin_pct": z.number(),
});

const KarnalFinancingExitValuationSchema = z.object({
  "dcf_remaining_term": z.number(),
  "ebitda_multiple_crosscheck": z.number(),
  "exit_year_ebitda": z.number(),
  "ebitda_multiple": z.number(),
  "discount_rate_pct": z.number(),
  "used": z.number(),
  "basis": z.string(),
  "beyond_model_horizon": z.number(),
});

const KarnalFinancingSchema = z.object({
  "project_cost": z.number(),
  "true_capital_requirement": GgvFinancingTrueCapitalRequirementSchema,
  "project_fcf": GgvFinancingProjectFcfSchema,
  "cost_of_capital": GgvFinancingCostOfCapitalSchema,
  "debt": KarnalFinancingDebtSchema,
  "equity": RvFinancingEquitySchema,
  "ccd": RvFinancingCcdSchema,
  "exit_equity_value": z.number(),
  "exit_year": z.number(),
  "exit_valuation": KarnalFinancingExitValuationSchema,
  "debt_capacity": GgvFinancingDebtCapacitySchema,
});

const KarnalScenariosDownsideMultipliersSchema = z.object({
  "footfall": z.number(),
  "opex": z.number(),
});

const KarnalScenariosDownsideSchema = z.object({
  "note": z.string(),
  "multipliers": KarnalScenariosDownsideMultipliersSchema,
  "revenue_year1": z.number(),
  "ebitda_year1": z.number(),
  "revenue_stabilised": z.number(),
  "ebitda_stabilised": z.number(),
  "ebitda_margin_stabilised": z.number(),
  "ebitda_final_year": z.number(),
  "project_irr_pct": metric,
  "payback_years": metric,
  "cumulative_fcf": z.number(),
});

const KarnalScenariosSchema = z.object({
  "downside": KarnalScenariosDownsideSchema,
  "base": GgvScenariosBaseSchema,
  "upside": KarnalScenariosDownsideSchema,
});

const KarnalSchema = z.object({
  "facts": KarnalFactsSchema,
  "capex_lines": z.array(GgvCapexLinesRowSchema).nonempty(),
  "capex_total": z.number(),
  "years": z.array(KarnalYearsRowSchema).min(5),
  "annual_depreciation": z.number(),
  "financing": KarnalFinancingSchema,
  "scenarios": KarnalScenariosSchema,
});

const ConsolidatedYearsRowPartsExistingSchema = z.object({
  "revenue": z.number(),
  "ebitda": z.number(),
});

const ConsolidatedYearsRowPartsSchema = z.object({
  "existing": ConsolidatedYearsRowPartsExistingSchema,
  "ggv": ConsolidatedYearsRowPartsExistingSchema,
  "rv": ConsolidatedYearsRowPartsExistingSchema,
  "karnal": ConsolidatedYearsRowPartsExistingSchema,
});

const ConsolidatedYearsRowSchema = z.object({
  "fy": z.string(),
  "parts": ConsolidatedYearsRowPartsSchema,
  "revenue": z.number(),
  "ebitda": z.number(),
  "ebitda_margin": z.number(),
});

const ConsolidatedSchema = z.object({
  "phasing_note": z.string(),
  "years": z.array(ConsolidatedYearsRowSchema).min(5),
});

const CompanyProfileFy26Schema = z.object({
  "revenue": z.number(),
  "ebitda": z.number(),
  "pat": z.number(),
  "net_worth": z.number(),
  "reserves": z.number(),
  "borrowings_short": z.number(),
  "borrowings_long_related": z.number(),
  "borrowings_total": z.number(),
  "cash": z.number(),
  "fdr": z.number(),
  "gross_block": z.number(),
  "net_block": z.number(),
  "electricity_arrears": z.number(),
  "finance_cost_total": z.number(),
  "trade_payables": z.number(),
  "other_current_liabilities": z.number(),
});

const CompanyProfilePromoterRelatedDebtSchema = z.object({
  "sanjeev_bewtra_and_team_buildcon_lt": z.number(),
  "promoter_loans_fy26": z.number(),
  "apoorv_babbar_huf": z.number(),
  "geetika_jain": z.number(),
});

const CompanyProfileProjectionsFY2627Schema = z.object({
  "revenue": z.number(),
  "ebitda": z.number(),
  "pat": z.number(),
});

const CompanyProfileProjectionsSchema = z.object({
  "FY26-27": CompanyProfileProjectionsFY2627Schema,
  "FY27-28": CompanyProfileProjectionsFY2627Schema,
  "FY28-29": CompanyProfileProjectionsFY2627Schema,
});

const CompanyProfileExistingRaiseSchema = z.object({
  "amount_cr": z.number(),
  "pre_money_cr": z.number(),
  "dilution_pct": z.number(),
});

const CompanyProfileSubhashParkSchema = z.object({
  "opened": z.string(),
  "fy2627_revenue_to_date_lakh": z.number(),
  "fy2627_months_elapsed": z.number(),
  "fy2627_run_rate_expectation_lakh": z.number(),
  "net_margin_first_four_months_pct": z.number(),
});

const CompanyProfileSchema = z.object({
  "name": z.string(),
  "cin": z.string(),
  "share_capital_lakh": z.number(),
  "shares_outstanding": z.number(),
  "face_value_inr": z.number(),
  "fy26": CompanyProfileFy26Schema,
  "promoter_related_debt": CompanyProfilePromoterRelatedDebtSchema,
  "projections": CompanyProfileProjectionsSchema,
  "existing_raise": CompanyProfileExistingRaiseSchema,
  "subhash_park": CompanyProfileSubhashParkSchema,
});

const CompanyMsmeSchema = z.object({
  "investment_plant_machinery_cr": z.number(),
  "turnover_cr": z.number(),
  "classification": z.string(),
  "headroom_investment_cr": z.number(),
  "headroom_turnover_cr": z.number(),
  "cgtmse_eligible": z.boolean(),
});

const CompanyRelatedPartyConversionBaseSchema = z.object({
  "borrowings": z.number(),
  "net_worth": z.number(),
  "debt_equity": z.number(),
});

const CompanyRelatedPartyConversionConvertLtRelated260Schema = z.object({
  "converted": z.number(),
  "borrowings": z.number(),
  "net_worth": z.number(),
  "debt_equity": z.number(),
});

const CompanyRelatedPartyConversionSchema = z.object({
  "base": CompanyRelatedPartyConversionBaseSchema,
  "convert_lt_related_260": CompanyRelatedPartyConversionConvertLtRelated260Schema,
  "convert_lt_plus_promoter_409": CompanyRelatedPartyConversionConvertLtRelated260Schema,
});

const CompanyExitBasisSchema = z.object({
  "fy": z.string(),
  "revenue": z.number(),
  "ebitda": z.number(),
  "ev_revenue_multiple": z.number(),
  "enterprise_value": z.number(),
  "ev_ebitda_crosscheck": z.number(),
  "net_debt": z.number(),
  "equity_value": z.number(),
});

const CompanyFinancingEquityExistingRoundSchema = z.object({
  "amount": z.number(),
  "pre_money": z.number(),
  "dilution_pct": z.number(),
});

const CompanyFinancingEquityPricingSensitivityIrr18Schema = z.object({
  "stake_pct": z.number(),
  "post_money": z.number(),
  "pre_money": z.number(),
});

const CompanyFinancingEquityPricingSensitivitySchema = z.object({
  "irr_18": CompanyFinancingEquityPricingSensitivityIrr18Schema,
  "irr_22": CompanyFinancingEquityPricingSensitivityIrr18Schema,
  "irr_25": CompanyFinancingEquityPricingSensitivityIrr18Schema,
});

const CompanyFinancingEquitySchema = z.object({
  "label": z.string(),
  "basis": z.string(),
  "investment": z.number(),
  "stake_pct": z.number(),
  "exit_year": z.number(),
  "exit_equity_value": z.number(),
  "exit_proceeds": z.number(),
  "distributable": z.array(z.number()).nonempty(),
  "dividends": z.array(z.number()).nonempty(),
  "flows": z.array(z.number()).nonempty(),
  "irr_pct": metric,
  "money_multiple": metric,
  "stake_for_18pct": z.number(),
  "stake_for_22pct": z.number(),
  "stake_for_25pct": z.number(),
  "pre_money": z.number(),
  "post_money": z.number(),
  "existing_round": CompanyFinancingEquityExistingRoundSchema,
  "pricing_sensitivity": CompanyFinancingEquityPricingSensitivitySchema,
});

const CompanyFinancingDebtCombinedServiceRowSchema = z.object({
  "year": z.number(),
  "new_facility": z.number(),
  "existing_debt": z.number(),
  "total_debt_service": z.number(),
  "cfads": z.number(),
  "dscr": metric,
});

const CompanyFinancingDebtLeverageCasesRowSchema = z.object({
  "label": z.string(),
  "conversion": z.number(),
  "retained_earnings": z.number(),
  "net_worth": z.number(),
  "borrowings": z.number(),
  "debt_equity": z.number(),
  "max_facility_at_covenant": z.number(),
});

const CompanyFinancingDebtLeverageSchema = z.object({
  "covenant_assumed": z.number(),
  "cases": z.array(CompanyFinancingDebtLeverageCasesRowSchema).min(3),
  "conversion_full": z.number(),
});

const CompanyFinancingDebtSchema = z.object({
  "label": z.string(),
  "term_loan": z.number(),
  "wc_limit": z.number(),
  "total_limit": z.number(),
  "rate_pct": z.number(),
  "tl_tenor_years": z.number(),
  "tl_moratorium_years": z.number(),
  "cgtmse": GgvFinancingDebtCgtmseSchema,
  "schedule": z.array(GgvFinancingDebtScheduleRowSchema).nonempty(),
  "min_dscr": metric,
  "avg_dscr": metric,
  "min_dscr_post_moratorium": metric,
  "avg_dscr_post_moratorium": metric,
  "bankable": z.boolean(),
  "total_interest": z.number(),
  "total_agf": z.number(),
  "total_finance_cost": z.number(),
  "combined_service": z.array(CompanyFinancingDebtCombinedServiceRowSchema).nonempty(),
  "min_dscr_combined": z.number(),
  "avg_dscr_combined": z.number(),
  "nbfc_refinance": z.number(),
  "leverage": CompanyFinancingDebtLeverageSchema,
});

const CompanyFinancingCcdSchema = z.object({
  "label": z.string(),
  "basis": z.string(),
  "principal": z.number(),
  "coupon_pct": z.number(),
  "conversion_year": z.number(),
  "conversion_stake_pct": z.number(),
  "coupon_paid_total": z.number(),
  "exit_year": z.number(),
  "exit_equity_value": z.number(),
  "exit_proceeds": z.number(),
  "distributable": z.array(z.number()).nonempty(),
  "flows": z.array(z.number()).nonempty(),
  "irr_pct": metric,
  "money_multiple": metric,
  "conversion_valuation_implied": z.number(),
  "balance_sheet_note": z.string(),
});

const CompanyFinancingSchema = z.object({
  "equity": CompanyFinancingEquitySchema,
  "debt": CompanyFinancingDebtSchema,
  "ccd": CompanyFinancingCcdSchema,
});

const CompanySchema = z.object({
  "profile": CompanyProfileSchema,
  "msme": CompanyMsmeSchema,
  "related_party_conversion": CompanyRelatedPartyConversionSchema,
  "exit_basis": CompanyExitBasisSchema,
  "financing": CompanyFinancingSchema,
});

const CgtmseAllocationSchema = z.object({
  "ceiling": z.number(),
  "ceiling_basis": z.string(),
  "gross_demand": z.object({"Geeta Govind Vatika — composite":z.number(),"Ramayan Vatika — composite":z.number(),"Karnal Phase 1 — term loan + WC":z.number(),"VAPPL — working capital and NBFC consolidation":z.number()}),
  "total_gross_demand": z.number(),
  "excess_over_ceiling": z.number(),
  "single_borrower_plan": z.object({"Karnal Phase 1 — term loan":z.number(),"Ramayan Vatika — term loan + standby WC":z.number(),"Geeta Govind Vatika — term loan + standby WC":z.number(),"VAPPL — working capital, NBFC consolidation":z.number()}),
  "single_borrower_plan_total": z.number(),
  "headroom": z.number(),
  "residual_to_fund_outside_cgtmse": z.number(),
});

export const financeModelSchema = z.object({
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
export type FinanceModel = z.infer<typeof financeModelSchema>;
export type ProjectFinancing = FinanceModel["rv"]["financing"] | FinanceModel["karnal"]["financing"];
export type ProjectYear = FinanceModel["ggv"]["years"][number] | FinanceModel["rv"]["years"][number] | FinanceModel["karnal"]["years"][number];
export type Scenarios = FinanceModel["ggv"]["scenarios"] | FinanceModel["rv"]["scenarios"] | FinanceModel["karnal"]["scenarios"];
