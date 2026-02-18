"""ROI calculation engine - pure financial math, no LLM needed."""

import math
from dataclasses import dataclass


@dataclass
class ProjectInputs:
    """User-provided project parameters."""
    product_name: str
    target_market: str
    product_description: str

    # Costs
    initial_investment: float  # one-time R&D / development cost
    annual_operating_cost: float  # ongoing annual costs
    annual_cost_growth_pct: float  # yearly cost increase %

    # Revenue
    total_addressable_market: int  # total market participants
    qualifying_ratio_pct: float  # % of market that qualifies
    hit_rate_pct: float  # expected conversion rate %
    avg_annual_license: float  # average annual revenue per customer
    revenue_start_month: int  # month when revenue begins (1-36)
    annual_revenue_growth_pct: float  # yearly revenue growth %

    # Timeline
    projection_years: int  # number of years to project (1-5)
    discount_rate_pct: float  # for NPV calculation


@dataclass
class ScenarioResult:
    """Financial projections for a single scenario."""
    label: str
    yearly_revenue: list[float]
    yearly_costs: list[float]
    yearly_profit: list[float]
    cumulative_profit: list[float]
    total_revenue: float
    total_costs: float
    total_profit: float
    roi_pct: float
    npv: float
    payback_month: int | None  # month when cumulative profit turns positive
    customer_count: int


def calculate_scenario(
    inputs: ProjectInputs,
    revenue_multiplier: float = 1.0,
    cost_multiplier: float = 1.0,
    label: str = "Base",
) -> ScenarioResult:
    """Calculate ROI for a given scenario with multipliers applied."""
    years = inputs.projection_years
    qualifying = int(inputs.total_addressable_market * inputs.qualifying_ratio_pct / 100)
    customers = max(1, int(qualifying * inputs.hit_rate_pct / 100 * revenue_multiplier))
    base_annual_revenue = customers * inputs.avg_annual_license

    yearly_revenue = []
    yearly_costs = []
    yearly_profit = []
    cumulative = []
    running_total = 0.0
    payback_month = None

    for year in range(1, years + 1):
        # Revenue: 0 until revenue_start_month, then prorated for first year
        rev_start = inputs.revenue_start_month
        if year == 1:
            if rev_start > 12:
                rev = 0.0
            else:
                active_months = max(0, 12 - rev_start + 1)
                rev = base_annual_revenue * (active_months / 12)
        else:
            months_since_start = (year - 1) * 12
            if months_since_start < rev_start:
                # Still in ramp-up
                active_months = max(0, year * 12 - rev_start + 1)
                rev = base_annual_revenue * (active_months / 12)
            else:
                growth_years = year - math.ceil(rev_start / 12)
                rev = base_annual_revenue * ((1 + inputs.annual_revenue_growth_pct / 100) ** growth_years)

        # Costs
        if year == 1:
            cost = (inputs.initial_investment + inputs.annual_operating_cost) * cost_multiplier
        else:
            cost = inputs.annual_operating_cost * ((1 + inputs.annual_cost_growth_pct / 100) ** (year - 1)) * cost_multiplier

        profit = rev - cost
        running_total += profit

        yearly_revenue.append(round(rev, 2))
        yearly_costs.append(round(cost, 2))
        yearly_profit.append(round(profit, 2))
        cumulative.append(round(running_total, 2))

        # Estimate payback month
        if payback_month is None and running_total >= 0:
            if year == 1:
                payback_month = 12
            else:
                prev_cum = cumulative[-2] if len(cumulative) > 1 else -inputs.initial_investment
                if profit > 0:
                    months_in_year = int(12 * (-prev_cum) / profit) if prev_cum < 0 else 0
                    payback_month = (year - 1) * 12 + max(1, months_in_year)
                else:
                    payback_month = year * 12

    total_revenue = sum(yearly_revenue)
    total_costs = sum(yearly_costs)
    total_profit = total_revenue - total_costs
    total_invested = sum(yearly_costs)
    roi_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0

    # NPV calculation
    npv = 0.0
    rate = inputs.discount_rate_pct / 100
    for i, profit in enumerate(yearly_profit):
        npv += profit / ((1 + rate) ** (i + 1))

    return ScenarioResult(
        label=label,
        yearly_revenue=yearly_revenue,
        yearly_costs=yearly_costs,
        yearly_profit=yearly_profit,
        cumulative_profit=cumulative,
        total_revenue=round(total_revenue, 2),
        total_costs=round(total_costs, 2),
        total_profit=round(total_profit, 2),
        roi_pct=round(roi_pct, 1),
        npv=round(npv, 2),
        payback_month=payback_month,
        customer_count=customers,
    )


def run_all_scenarios(inputs: ProjectInputs) -> dict[str, ScenarioResult]:
    """Run optimistic, most likely, and pessimistic scenarios."""
    return {
        "optimistic": calculate_scenario(inputs, revenue_multiplier=1.3, cost_multiplier=0.9, label="Optimistic"),
        "most_likely": calculate_scenario(inputs, revenue_multiplier=1.0, cost_multiplier=1.0, label="Most Likely"),
        "pessimistic": calculate_scenario(inputs, revenue_multiplier=0.7, cost_multiplier=1.15, label="Pessimistic"),
    }
