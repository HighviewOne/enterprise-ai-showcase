"""Loan Underwriting Application - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.underwriter import analyze_application, calculate_basic_ratios

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1e3a5f 0%, #2d6a4f 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .hero p { color: #c0d0c0; margin: 0.3rem 0 0 0; }
    .decision-approve { background: linear-gradient(135deg, #28a745dd, #20c99788);
        padding: 1.2rem; border-radius: 10px; color: white; text-align: center; }
    .decision-conditional { background: linear-gradient(135deg, #ffc107dd, #fd7e1488);
        padding: 1.2rem; border-radius: 10px; color: #333; text-align: center; }
    .decision-refer { background: linear-gradient(135deg, #17a2b8dd, #667eea88);
        padding: 1.2rem; border-radius: 10px; color: white; text-align: center; }
    .decision-deny { background: linear-gradient(135deg, #dc3545dd, #c8232388);
        padding: 1.2rem; border-radius: 10px; color: white; text-align: center; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.7rem 1rem;
        margin-bottom: 0.4rem; border-left: 4px solid #6c757d; }
    .risk-positive { border-left-color: #28a745; }
    .risk-negative { border-left-color: #dc3545; }
    .risk-neutral { border-left-color: #ffc107; }
    .bias-ok { background: #d4edda; border-radius: 8px; padding: 0.8rem; border-left: 4px solid #28a745; }
    .bias-warn { background: #f8d7da; border-radius: 8px; padding: 0.8rem; border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.markdown("### Compliance")
    st.markdown("- ECOA / Fair Housing Act")
    st.markdown("- Bias-free decisions")
    st.markdown("- Human-in-the-loop review")
    st.divider()
    # Review queue
    if "review_queue" not in st.session_state:
        st.session_state["review_queue"] = []
    queue_count = len([r for r in st.session_state["review_queue"] if r.get("status") == "Pending"])
    st.metric("Pending Reviews", queue_count)

st.markdown("""<div class="hero"><h1>Loan Underwriting System</h1>
<p>AI-powered credit assessment with bias guardrails and human-in-the-loop review</p></div>""",
unsafe_allow_html=True)

tab_apply, tab_review, tab_dashboard = st.tabs(["New Application", "Human Review Queue", "Dashboard"])

# ── Application Tab ──
with tab_apply:
    with st.form("loan_app"):
        st.subheader("Applicant Information")
        a1, a2, a3 = st.columns(3)
        with a1:
            applicant_name = st.text_input("Full Name", value="Alex Johnson")
            employer = st.text_input("Employer", value="TechCorp Inc.")
        with a2:
            employment_status = st.selectbox("Employment Status",
                ["Full-Time Employed", "Part-Time Employed", "Self-Employed", "Contractor", "Retired", "Unemployed"])
            employment_duration = st.selectbox("Employment Duration",
                ["Less than 1 year", "1-2 years", "3-5 years", "5-10 years", "10+ years"], index=3)
        with a3:
            annual_income = st.number_input("Annual Income ($)", min_value=0, value=95_000, step=5_000)
            monthly_debts = st.number_input("Monthly Debt Obligations ($)", min_value=0, value=1_200, step=100)

        st.divider()
        st.subheader("Loan Details")
        l1, l2, l3, l4 = st.columns(4)
        with l1:
            loan_purpose = st.selectbox("Loan Purpose",
                ["Home Purchase", "Refinance", "Auto Loan", "Personal Loan",
                 "Business Loan", "Student Loan", "Debt Consolidation"])
        with l2:
            requested_amount = st.number_input("Requested Amount ($)", min_value=1_000, value=350_000, step=10_000)
        with l3:
            requested_term = st.selectbox("Requested Term (months)",
                [12, 24, 36, 48, 60, 120, 180, 240, 360], index=8)
        with l4:
            property_value = st.number_input("Property Value ($)", min_value=0, value=425_000, step=10_000,
                                              help="Set to 0 if not applicable")

        st.divider()
        st.subheader("Credit Bureau Data")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=720)
            credit_history_years = st.number_input("Credit History (years)", min_value=0, value=12)
        with c2:
            open_accounts = st.number_input("Open Accounts", min_value=0, value=8)
            late_payments = st.number_input("Late Payments (2yr)", min_value=0, value=1)
        with c3:
            collections = st.number_input("Collections", min_value=0, value=0)
            bankruptcies = st.number_input("Bankruptcies", min_value=0, value=0)
        with c4:
            total_debt = st.number_input("Total Current Debt ($)", min_value=0, value=45_000, step=5_000)

        additional_info = st.text_area("Additional Information", value="Applicant has stable employment history with consistent raises. First-time homebuyer.",
                                        height=80, placeholder="Any additional context...")

        submitted = st.form_submit_button("Run Underwriting Analysis", type="primary", use_container_width=True)

    if submitted:
        if not api_key:
            st.error("API key required.")
            st.stop()

        app_data = dict(
            app_id=f"APP-{len(st.session_state.get('review_queue', [])) + 1001:04d}",
            applicant_name=applicant_name, loan_purpose=loan_purpose,
            requested_amount=requested_amount, requested_term=requested_term,
            property_value=property_value, annual_income=annual_income,
            employment_status=employment_status, employment_duration=employment_duration,
            employer=employer, monthly_debts=monthly_debts, credit_score=credit_score,
            credit_history_years=credit_history_years, open_accounts=open_accounts,
            late_payments=late_payments, collections=collections, bankruptcies=bankruptcies,
            total_debt=total_debt, additional_info=additional_info,
        )

        # Quick pre-screen
        ratios = calculate_basic_ratios(app_data)
        st.divider()
        st.subheader("Pre-Screen Ratios")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Est. Monthly Payment", f"${ratios['monthly_payment_est']:,.0f}")
        r2.metric("Debt-to-Income", f"{ratios['dti_pct']}%",
                   delta="Good" if ratios['dti_pct'] < 43 else "High", delta_color="normal" if ratios['dti_pct'] < 43 else "inverse")
        ltv_str = f"{ratios['ltv_pct']}%" if ratios['ltv_pct'] else "N/A"
        r3.metric("Loan-to-Value", ltv_str)
        r4.metric("Disposable Income", f"${ratios['disposable_after_payment']:,.0f}")

        # AI analysis
        st.divider()
        with st.spinner("Running AI underwriting analysis..."):
            try:
                result = analyze_application(app_data, api_key)
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()

        # Decision banner
        decision = result.get("preliminary_decision", "Refer to Human").lower().replace(" ", "-")
        css_map = {"approve": "decision-approve", "conditional-approve": "decision-conditional",
                   "refer-to-human": "decision-refer", "deny": "decision-deny"}
        css = css_map.get(decision, "decision-refer")
        st.markdown(f"""<div class="{css}">
            <h2 style="margin:0;">{result.get('preliminary_decision', 'N/A')}</h2>
            <p style="margin:0.3rem 0 0 0;">Risk: {result.get('risk_classification', 'N/A')} |
            Tier: {result.get('credit_tier', 'N/A')} | Confidence: {result.get('confidence', 0)}%</p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"**Summary:** {result.get('summary', '')}")

        # Recommended terms
        terms = result.get("recommended_terms", {})
        if terms.get("approved_amount"):
            st.subheader("Recommended Terms")
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("Approved Amount", f"${terms.get('approved_amount', 0):,.0f}")
            t2.metric("Interest Rate", f"{terms.get('interest_rate_pct', 0)}%")
            t3.metric("Term", f"{terms.get('term_months', 0)} months")
            t4.metric("Monthly Payment", f"${terms.get('monthly_payment', 0):,.0f}")
            if terms.get("conditions"):
                st.markdown("**Conditions:**")
                for cond in terms["conditions"]:
                    st.markdown(f"- {cond}")

        # Risk factors
        st.subheader("Risk Factor Analysis")
        for rf in result.get("risk_factors", []):
            impact = rf.get("impact", "neutral").lower()
            css_rf = f"risk-{impact}"
            st.markdown(f"""<div class="risk-card {css_rf}">
                <strong>[{rf.get('weight', '')}]</strong> {rf.get('factor', '')}
                <span style="float:right;">{rf.get('impact', '')}</span>
            </div>""", unsafe_allow_html=True)

        # Bias check
        st.subheader("Bias & Fairness Check")
        bias = result.get("bias_check", {})
        if bias.get("decision_based_on_financial_factors_only", True):
            st.markdown(f'<div class="bias-ok"><strong>PASS</strong> — {bias.get("notes", "Decision based on financial factors only.")}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bias-warn"><strong>WARNING</strong> — {bias.get("notes", "Review required.")}</div>',
                        unsafe_allow_html=True)

        # Denial reasons
        if result.get("denial_reasons"):
            st.subheader("Denial Reasons")
            for r in result["denial_reasons"]:
                st.markdown(f"- {r}")

        # Add to review queue
        review_item = {**result, "app_data": app_data, "status": "Pending", "reviewer_notes": ""}
        st.session_state["review_queue"].append(review_item)
        st.success(f"Application {app_data['app_id']} added to human review queue.")

        st.download_button("Download Analysis (JSON)", json.dumps(result, indent=2),
                           f"underwriting_{app_data['app_id']}.json", "application/json")

# ── Review Tab ──
with tab_review:
    st.subheader("Human Review Queue")
    queue = st.session_state.get("review_queue", [])
    pending = [r for r in queue if r.get("status") == "Pending"]

    if not pending:
        st.info("No applications pending review.")
    else:
        for i, item in enumerate(pending):
            app = item.get("app_data", {})
            with st.expander(f"{app.get('app_id', 'N/A')} — {app.get('applicant_name', '')} | "
                           f"AI Decision: {item.get('preliminary_decision', 'N/A')} | "
                           f"${app.get('requested_amount', 0):,.0f} {app.get('loan_purpose', '')}"):
                st.markdown(f"**Risk:** {item.get('risk_classification', '')} | "
                          f"**Credit Score:** {app.get('credit_score', '')} | "
                          f"**Confidence:** {item.get('confidence', 0)}%")
                st.markdown(f"**AI Summary:** {item.get('summary', '')}")

                col_a, col_b = st.columns(2)
                with col_a:
                    final_decision = st.selectbox("Final Decision",
                        ["Approve", "Conditional Approve", "Deny"],
                        key=f"dec_{i}")
                with col_b:
                    notes = st.text_area("Reviewer Notes", key=f"notes_{i}", height=80)

                if st.button("Submit Review", key=f"submit_{i}"):
                    idx = queue.index(item)
                    queue[idx]["status"] = "Reviewed"
                    queue[idx]["final_decision"] = final_decision
                    queue[idx]["reviewer_notes"] = notes
                    st.success(f"Review submitted: {final_decision}")
                    st.rerun()

    reviewed = [r for r in queue if r.get("status") == "Reviewed"]
    if reviewed:
        st.divider()
        st.subheader("Reviewed Applications")
        rows = []
        for r in reviewed:
            app = r.get("app_data", {})
            rows.append({
                "App ID": app.get("app_id", ""),
                "Applicant": app.get("applicant_name", ""),
                "Amount": f"${app.get('requested_amount', 0):,.0f}",
                "AI Decision": r.get("preliminary_decision", ""),
                "Final Decision": r.get("final_decision", ""),
                "Credit Score": app.get("credit_score", ""),
                "Reviewer Notes": r.get("reviewer_notes", ""),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Dashboard Tab ──
with tab_dashboard:
    st.subheader("Underwriting Dashboard")
    queue = st.session_state.get("review_queue", [])

    if not queue:
        st.info("No applications processed yet. Submit an application to see dashboard metrics.")
    else:
        # Summary metrics
        total = len(queue)
        reviewed = [r for r in queue if r.get("status") == "Reviewed"]
        pending_count = total - len(reviewed)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Applications", total)
        m2.metric("Reviewed", len(reviewed))
        m3.metric("Pending", pending_count)

        # AI decision distribution
        decisions = {}
        for r in queue:
            d = r.get("preliminary_decision", "Unknown")
            decisions[d] = decisions.get(d, 0) + 1

        if decisions:
            avg_confidence = sum(r.get("confidence", 0) for r in queue) / total
            m4.metric("Avg Confidence", f"{avg_confidence:.0f}%")

            colors = {"Approve": "#28a745", "Conditional Approve": "#ffc107",
                      "Refer to Human": "#17a2b8", "Deny": "#dc3545"}
            fig = go.Figure(go.Pie(
                labels=list(decisions.keys()), values=list(decisions.values()),
                marker=dict(colors=[colors.get(k, "#6c757d") for k in decisions.keys()]),
                hole=0.4,
            ))
            fig.update_layout(title="AI Decision Distribution", height=350)
            st.plotly_chart(fig, use_container_width=True)

        # Credit score distribution
        scores = [r.get("app_data", {}).get("credit_score", 0) for r in queue if r.get("app_data")]
        if scores:
            fig2 = go.Figure(go.Histogram(x=scores, nbinsx=10, marker_color="#667eea"))
            fig2.update_layout(title="Credit Score Distribution", height=300,
                             xaxis_title="Credit Score", yaxis_title="Count")
            st.plotly_chart(fig2, use_container_width=True)
