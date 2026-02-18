"""AI Mortgage Consultant (MoJo) - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.mortgage_engine import analyze_mortgage

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .loan-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        margin-bottom: 0.8rem; }
    .loan-rec { border-top: 4px solid #4caf50; }
    .loan-alt { border-top: 4px solid #bdbdbd; }
    .fit-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        color: white; font-weight: bold; }
    .step-card { background: #f3e5f5; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #7b1fa2; margin-bottom: 0.4rem; }
    .breakdown-card { background: #e8eaf6; border-radius: 8px; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Note:** This tool provides estimates for educational purposes. "
            "Actual rates and approval depend on your lender.")

st.markdown("""<div class="hero"><h1>MoJo - Mortgage Journey AI</h1>
<p>Your AI mortgage consultant — loan matching, affordability analysis, and a personalized home buying plan</p></div>""",
unsafe_allow_html=True)

with st.form("mortgage_form"):
    st.subheader("Your Financial Profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        buyer_type = st.selectbox("Buyer Type",
            ["First-time Homebuyer", "Move-up Buyer", "Downsizing",
             "Investment Property", "Second Home", "Refinancing"])
        income = st.text_input("Annual Household Income", value="$125,000")
        credit_score = st.selectbox("Credit Score Range",
            ["800+ (Exceptional)", "740-799 (Very Good)", "670-739 (Good)",
             "580-669 (Fair)", "Below 580 (Poor)"], index=1)
    with c2:
        monthly_debts = st.text_input("Monthly Debt Payments",
            value="$850 (car loan $400, student loans $350, credit cards $100)")
        savings = st.text_input("Savings / Down Payment Available",
            value="$65,000 in savings, $15,000 in investments")
        employment = st.text_input("Employment Status",
            value="W-2 employed, software engineer, 4 years at current company")
    with c3:
        location = st.text_input("Target Location", value="Raleigh-Durham, NC")
        price_range = st.text_input("Target Price Range", value="$350,000 - $450,000")
        property_type = st.selectbox("Property Type",
            ["Single Family Home", "Townhouse", "Condo", "Multi-family (2-4 units)"])
        timeline = st.selectbox("Buying Timeline",
            ["Ready now (0-3 months)", "Soon (3-6 months)",
             "Planning (6-12 months)", "Exploring (12+ months)"], index=1)

    context = st.text_input("Additional Context",
        value="Married, dual income. Spouse earns $85K. Currently renting at $2,100/month. "
              "Want good school district. No VA eligibility.")

    submitted = st.form_submit_button("Analyze My Mortgage Options", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        buyer_type=buyer_type, income=income, monthly_debts=monthly_debts,
        credit_score=credit_score, savings=savings, location=location,
        price_range=price_range, property_type=property_type,
        timeline=timeline, employment=employment, context=context,
    )

    with st.spinner("Analyzing your mortgage options..."):
        try:
            result = analyze_mortgage(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    st.warning(result.get("disclaimer", "For educational purposes only."))

    # Financial Assessment
    fa = result.get("financial_assessment", {})
    st.subheader("Financial Readiness")
    fa1, fa2, fa3, fa4 = st.columns(4)
    fa1.metric("Readiness Score", f"{fa.get('readiness_score', 0)}/100")
    fa2.metric("Status", fa.get("readiness_level", "N/A"))
    fa3.metric("Comfortable Price", f"${fa.get('comfortable_home_price', 0):,.0f}")
    fa4.metric("Max Price", f"${fa.get('max_home_price', 0):,.0f}")

    # Readiness gauge
    fig_ready = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fa.get("readiness_score", 0),
        title={"text": "Mortgage Readiness"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#7b1fa2"},
            "steps": [
                {"range": [0, 40], "color": "#ffcdd2"},
                {"range": [40, 70], "color": "#fff9c4"},
                {"range": [70, 100], "color": "#c8e6c9"},
            ],
        }
    ))
    fig_ready.update_layout(height=250)
    st.plotly_chart(fig_ready, use_container_width=True)

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown(f"**Housing Budget:** ${fa.get('monthly_budget_for_housing', 0):,.0f}/mo")
        st.markdown(f"**Current DTI:** {fa.get('dti_ratio_current', 0):.1f}% | "
                   f"**Projected DTI:** {fa.get('dti_ratio_projected', 0):.1f}%")
        for s in fa.get("strengths", []):
            st.success(s)
    with fc2:
        for c in fa.get("concerns", []):
            st.warning(c)
        for imp in fa.get("improvements_needed", []):
            st.info(f"Improvement: {imp}")

    # Loan Recommendations
    loans = result.get("loan_recommendations", [])
    if loans:
        st.divider()
        st.subheader("Loan Product Recommendations")

        # Comparison chart
        rec_loans = [l for l in loans if l.get("recommended")]
        if rec_loans:
            fig_loans = go.Figure()
            fig_loans.add_trace(go.Bar(
                name="Monthly Payment",
                x=[l.get("loan_type", "") for l in rec_loans],
                y=[l.get("total_monthly_cost", 0) for l in rec_loans],
                marker_color="#7b1fa2",
                text=[f"${l.get('total_monthly_cost', 0):,.0f}" for l in rec_loans],
                textposition="outside",
            ))
            fig_loans.update_layout(title="Total Monthly Cost by Loan Type",
                                     height=300, yaxis_tickprefix="$")
            st.plotly_chart(fig_loans, use_container_width=True)

        for loan in sorted(loans, key=lambda x: x.get("fit_score", 0), reverse=True):
            cls = "loan-rec" if loan.get("recommended") else "loan-alt"
            fit = loan.get("fit_score", 0)
            fit_color = "#4caf50" if fit >= 7 else "#ff9800" if fit >= 5 else "#f44336"
            rec_label = " [RECOMMENDED]" if loan.get("recommended") else ""

            st.markdown(f"""<div class="loan-card {cls}">
                <span class="fit-badge" style="background:{fit_color};">{fit}/10 Fit</span>
                <strong> {loan.get('loan_type', '')}{rec_label}</strong><br/>
                Rate: <strong>{loan.get('estimated_rate', 'N/A')}</strong> |
                Monthly: <strong>${loan.get('total_monthly_cost', 0):,.0f}</strong> |
                Down: {loan.get('down_payment_required', 'N/A')} |
                PMI: {'Yes ($' + str(loan.get('pmi_monthly', 0)) + '/mo)' if loan.get('pmi_required') else 'No'}<br/>
                Qualification: {loan.get('qualification_likelihood', 'N/A')} |
                Best for: {loan.get('best_for', '')}
            </div>""", unsafe_allow_html=True)

        # Loan comparison table
        loan_df = pd.DataFrame([{
            "Loan Type": l.get("loan_type", ""),
            "Rate": l.get("estimated_rate", ""),
            "Monthly": f"${l.get('total_monthly_cost', 0):,.0f}",
            "Down Payment": l.get("down_payment_required", ""),
            "PMI": "Yes" if l.get("pmi_required") else "No",
            "Fit": f"{l.get('fit_score', 0)}/10",
        } for l in loans])
        st.dataframe(loan_df, use_container_width=True, hide_index=True)

    # Affordability Breakdown
    ab = result.get("affordability_breakdown", {})
    if ab:
        st.divider()
        st.subheader("Affordability Breakdown")
        ab1, ab2 = st.columns(2)
        with ab1:
            st.markdown(f"""<div class="breakdown-card">
                <h4>Home: ${ab.get('home_price', 0):,.0f}</h4>
                Down Payment: ${ab.get('down_payment', 0):,.0f}<br/>
                Loan Amount: ${ab.get('loan_amount', 0):,.0f}<br/>
                <strong>Total Monthly: ${ab.get('total_monthly_payment', 0):,.0f}</strong>
            </div>""", unsafe_allow_html=True)
        with ab2:
            # Payment breakdown pie
            fig_pay = go.Figure(go.Pie(
                labels=["P&I", "Property Tax", "Insurance", "PMI", "HOA"],
                values=[ab.get("monthly_principal_interest", 0),
                        ab.get("property_tax_monthly", 0),
                        ab.get("homeowners_insurance_monthly", 0),
                        ab.get("pmi_monthly", 0),
                        ab.get("hoa_estimate_monthly", 0)],
                hole=0.3,
            ))
            fig_pay.update_layout(title="Monthly Payment Breakdown", height=300)
            st.plotly_chart(fig_pay, use_container_width=True)

        st.markdown(f"**Cash Needed at Closing:** ${ab.get('cash_needed_at_closing', 0):,.0f} "
                   f"(includes closing costs ~${ab.get('closing_costs_estimate', 0):,.0f})")
        st.markdown(f"**Recommended Emergency Fund:** ${ab.get('emergency_fund_recommendation', 0):,.0f}")

    # Market Insights
    mkt = result.get("market_insights", {})
    if mkt:
        st.divider()
        st.subheader("Market Insights")
        st.metric("Market Type", mkt.get("market_condition", "N/A"))
        st.markdown(f"**Rates:** {mkt.get('rate_environment', '')}")
        st.markdown(f"**Timing:** {mkt.get('timing_advice', '')}")
        st.markdown(f"**Price Trends:** {mkt.get('price_trends', '')}")

    # Action Plan
    plan = result.get("action_plan", [])
    if plan:
        st.divider()
        st.subheader("Your Home Buying Action Plan")
        for step in plan:
            imp = step.get("importance", "Important")
            imp_icon = "🔴" if imp == "Critical" else "🟡" if imp == "Important" else "🟢"
            st.markdown(f"""<div class="step-card">
                {imp_icon} <strong>Step {step.get('step', '')}: {step.get('action', '')}</strong>
                — {step.get('timeline', '')}<br/>
                {step.get('details', '')}
            </div>""", unsafe_allow_html=True)

    # Tips
    tips = result.get("tips", {})
    if tips:
        st.divider()
        st.subheader("Pro Tips")
        tp1, tp2 = st.columns(2)
        with tp1:
            st.markdown("**Credit Optimization:**")
            for t in tips.get("credit_optimization", []):
                st.markdown(f"- {t}")
            st.markdown("**Savings Strategies:**")
            for t in tips.get("savings_strategies", []):
                st.markdown(f"- {t}")
        with tp2:
            st.markdown("**Negotiation Tips:**")
            for t in tips.get("negotiation_tips", []):
                st.markdown(f"- {t}")
            st.markdown("**Mistakes to Avoid:**")
            for t in tips.get("mistakes_to_avoid", []):
                st.warning(t)

    # Export
    st.divider()
    st.download_button("Download Mortgage Analysis (JSON)", json.dumps(result, indent=2),
                       "mortgage_analysis.json", "application/json")
