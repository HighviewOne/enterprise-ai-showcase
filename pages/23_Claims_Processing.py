"""Claims Processing Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.claims_engine import review_claims

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .claim-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .approve { border-left: 4px solid #4caf50; }
    .review { border-left: 4px solid #ff9800; }
    .deny { border-left: 4px solid #f44336; }
    .flag-chip { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 20px;
        margin: 0.1rem; font-size: 0.8rem; font-weight: 500; }
    .flag-high { background: #ffcdd2; color: #c62828; }
    .flag-med { background: #fff3e0; color: #e65100; }
    .flag-low { background: #e8f5e9; color: #2e7d32; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Claims Processing Assistant</h1>
<p>Automated claims review with completeness checks, medical necessity assessment, and fraud detection</p></div>""",
unsafe_allow_html=True)

sample_claims = ""
try:
    with open("examples/sample_claims.txt") as f:
        sample_claims = f.read()
except FileNotFoundError:
    pass

with st.form("claims_form"):
    claims = st.text_area("Claims to Review",
                           value=sample_claims, height=300,
                           placeholder="Paste claim details: ID, patient, diagnosis codes, procedures, amounts...")
    c1, c2 = st.columns(2)
    with c1:
        policy_context = st.selectbox("Policy Type Context",
            ["Mixed (multiple policy types)", "PPO Plans", "HMO Plans",
             "Medicare / Medicare Supplement", "Medicaid", "Workers' Compensation"])
    with c2:
        focus = st.multiselect("Review Focus",
            ["Completeness", "Medical Necessity", "Coding Accuracy",
             "Pre-Authorization", "Fraud Detection", "Policy Compliance"],
            default=["Completeness", "Medical Necessity", "Coding Accuracy", "Policy Compliance"])
    context = st.text_input("Additional Context",
        value="Routine batch review. Flag anything that needs human adjuster attention.")

    submitted = st.form_submit_button("Review Claims", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        claims=claims, policy_context=policy_context,
        focus=", ".join(focus), context=context,
    )

    with st.spinner("Reviewing claims..."):
        try:
            result = review_claims(config, api_key)
        except Exception as e:
            st.error(f"Review failed: {e}")
            st.stop()

    # Batch Summary
    batch = result.get("batch_summary", {})
    st.subheader("Batch Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Claims", batch.get("total_claims", 0))
    m2.metric("Total Billed", f"${batch.get('total_billed', 0):,.0f}")
    m3.metric("Est. Payout", f"${batch.get('estimated_payout', 0):,.0f}")
    m4.metric("Savings", f"${batch.get('savings_identified', 0):,.0f}",
              delta=f"-${batch.get('savings_identified', 0):,.0f}", delta_color="inverse")

    # Decision distribution
    fig_dec = go.Figure(go.Pie(
        labels=["Auto-Approve", "Needs Review", "Likely Deny"],
        values=[batch.get("auto_approve", 0), batch.get("needs_review", 0),
                batch.get("likely_deny", 0)],
        hole=0.4,
        marker_colors=["#4caf50", "#ff9800", "#f44336"],
    ))
    fig_dec.update_layout(title="Claim Decisions", height=300)
    st.plotly_chart(fig_dec, use_container_width=True)

    # Individual Claim Reviews
    reviews = result.get("claim_reviews", [])
    if reviews:
        st.divider()
        st.subheader(f"Claim-by-Claim Review ({len(reviews)})")

        for claim in reviews:
            rec = claim.get("recommendation", "Pend for Review")
            cls = ("approve" if "Approve" in rec and "Adjust" not in rec
                   else "deny" if "Deny" in rec else "review")
            rec_icon = "+" if cls == "approve" else "x" if cls == "deny" else "?"
            risk = claim.get("risk_score", 5)

            flags_html = ""
            for f in claim.get("flags", []):
                sev = f.get("severity", "Medium")
                f_cls = "flag-high" if sev == "High" else "flag-low" if sev == "Low" else "flag-med"
                flags_html += f'<span class="flag-chip {f_cls}">{f.get("type", "")}: {f.get("detail", "")}</span> '

            st.markdown(f"""<div class="claim-card {cls}">
                <strong>[{rec_icon}] {claim.get('claim_id', '')} — {claim.get('claimant', '')}</strong>
                <span style="float:right;"><strong>{rec}</strong> (Confidence: {claim.get('confidence', 'N/A')})</span><br/>
                Provider: {claim.get('provider', '')} |
                Billed: <strong>${claim.get('total_billed', 0):,.0f}</strong> |
                Recommended Payout: <strong>${claim.get('recommended_payout', 0):,.0f}</strong> |
                Risk: {risk}/10<br/>
                {flags_html}
            </div>""", unsafe_allow_html=True)

            with st.expander(f"Details — {claim.get('claim_id', '')}"):
                dc1, dc2 = st.columns(2)
                with dc1:
                    comp = claim.get("completeness_check", {})
                    status = "Complete" if comp.get("is_complete") else "Incomplete"
                    st.markdown(f"**Completeness:** {status} ({comp.get('documentation_quality', 'N/A')})")
                    for mi in comp.get("missing_items", []):
                        st.warning(f"Missing: {mi}")

                    mn = claim.get("medical_necessity", {})
                    mn_status = "Supported" if mn.get("is_necessary") else "Questionable"
                    st.markdown(f"**Medical Necessity:** {mn_status}")
                    st.markdown(f"*{mn.get('justification', '')}*")
                    for alt in mn.get("alternative_treatments", []):
                        st.caption(f"Alternative: {alt}")

                with dc2:
                    coding = claim.get("coding_review", {})
                    coding_status = "Accurate" if coding.get("codes_accurate") else "Issues Found"
                    st.markdown(f"**Coding:** {coding_status}")
                    for issue in coding.get("issues", []):
                        st.warning(f"Issue: {issue}")

                    policy = claim.get("policy_compliance", {})
                    pol_status = "Compliant" if policy.get("in_compliance") else "Non-compliant"
                    st.markdown(f"**Policy Compliance:** {pol_status}")
                    st.markdown(f"Pre-auth: {policy.get('pre_auth_status', 'N/A')}")
                    for v in policy.get("violations", []):
                        st.error(f"Violation: {v}")

                st.info(f"**Adjuster Notes:** {claim.get('adjuster_notes', '')}")
                st.caption(f"Member Impact: {claim.get('member_impact', '')}")

        # Summary table
        summary_df = pd.DataFrame([{
            "Claim": c.get("claim_id", ""),
            "Claimant": c.get("claimant", ""),
            "Billed": f"${c.get('total_billed', 0):,.0f}",
            "Payout": f"${c.get('recommended_payout', 0):,.0f}",
            "Decision": c.get("recommendation", ""),
            "Risk": f"{c.get('risk_score', 0)}/10",
            "Flags": len(c.get("flags", [])),
        } for c in reviews])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Trend Analysis
    trends = result.get("trend_analysis", {})
    if trends:
        st.divider()
        st.subheader("Trend Analysis")
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown("**Common Issues:**")
            for i in trends.get("common_issues", []):
                st.markdown(f"- {i}")
            st.markdown("**Fraud Indicators:**")
            for f in trends.get("fraud_indicators", []):
                st.error(f)
        with tc2:
            st.markdown("**Process Improvements:**")
            for p in trends.get("process_improvements", []):
                st.markdown(f"- {p}")
            st.markdown("**Provider Notes:**")
            for n in trends.get("provider_notes", []):
                st.info(n)

    # Export
    st.divider()
    st.download_button("Download Claims Report (JSON)", json.dumps(result, indent=2),
                       "claims_report.json", "application/json")
