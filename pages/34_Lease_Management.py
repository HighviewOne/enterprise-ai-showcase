"""Lease Management - E2E Automated Leasing - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.lease_engine import analyze_leases

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #37474f 0%, #546e7a 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .lease-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem;
        border-left: 4px solid #1565c0; }
    .date-urgent { background: #ffebee; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.4rem;
        border-left: 4px solid #c62828; }
    .date-normal { background: #e3f2fd; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.4rem;
        border-left: 4px solid #1565c0; }
    .comp-pass { color: #4caf50; font-weight: bold; }
    .comp-fail { color: #f44336; font-weight: bold; }
    .comp-review { color: #ff9800; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**LeaseIQ** extracts key data from lease documents, calculates IFRS 16/ASC 842 "
            "obligations, and manages critical dates across your portfolio.")

st.markdown("""<div class="hero"><h1>LeaseIQ - Smart Lease Management</h1>
<p>AI-powered lease abstraction, compliance analysis, and portfolio management</p></div>""",
unsafe_allow_html=True)

with st.form("lease_form"):
    lease_data = st.text_area("Lease Documents / Portfolio Data", height=300,
        value="=== LEASE #1 - HQ OFFICE ===\n"
              "Lessee: GlobalTech Solutions Inc.\n"
              "Lessor: Meridian Properties LLC\n"
              "Property: Suite 400-410, 200 Innovation Drive, San Jose, CA 95134\n"
              "Type: Office (12,000 sq ft)\n"
              "Commencement: January 1, 2023\n"
              "Expiration: December 31, 2027 (5-year term)\n"
              "Base Rent: $42,000/month (Year 1), 3% annual escalation\n"
              "Security Deposit: $84,000\n"
              "Renewal: Two 3-year options at market rate\n"
              "Termination: After Year 3 with 6-month notice + 4 months penalty\n"
              "Obligations: Tenant pays pro-rata share of CAM, insurance, property taxes (NNN)\n"
              "TI Allowance: $240,000 amortized over lease term\n\n"
              "=== LEASE #2 - WAREHOUSE ===\n"
              "Lessee: GlobalTech Solutions Inc.\n"
              "Lessor: Industrial Partners REIT\n"
              "Property: Building C, 500 Logistics Blvd, Fremont, CA 94538\n"
              "Type: Industrial/Warehouse (25,000 sq ft)\n"
              "Commencement: July 1, 2022\n"
              "Expiration: June 30, 2025 [EXPIRING SOON]\n"
              "Base Rent: $28,500/month, fixed\n"
              "Security Deposit: $57,000\n"
              "Renewal: One 2-year option, must exercise by Jan 1, 2025\n"
              "Obligations: Tenant responsible for interior maintenance, lessor handles roof/structure\n\n"
              "=== LEASE #3 - EQUIPMENT ===\n"
              "Lessee: GlobalTech Solutions Inc.\n"
              "Lessor: TechLease Financial Corp.\n"
              "Equipment: 50x Dell Precision Workstations + 3 HP Enterprise Servers\n"
              "Commencement: March 1, 2024\n"
              "Expiration: February 28, 2027 (3-year term)\n"
              "Monthly Payment: $8,200\n"
              "Purchase Option: Fair market value at end of term\n"
              "Maintenance: Included in lease payments\n"
              "Insurance: Lessee responsible\n")

    c1, c2 = st.columns(2)
    with c1:
        company = st.text_input("Company Name", value="GlobalTech Solutions Inc.")
        standard = st.selectbox("Accounting Standard",
            ["IFRS 16", "ASC 842", "Both"])
    with c2:
        discount_rate = st.number_input("Discount Rate (%)", value=5.0, step=0.5)
        focus = st.text_input("Analysis Focus",
            value="Critical date management, upcoming expirations, IFRS 16 compliance gaps")

    submitted = st.form_submit_button("Analyse Leases", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        lease_data=lease_data, company=company, standard=standard,
        discount_rate=discount_rate, focus=focus,
    )

    with st.spinner("Analysing lease portfolio..."):
        try:
            result = analyze_leases(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Portfolio Summary
    summary = result.get("portfolio_summary", {})
    st.subheader("Portfolio Summary")
    pm1, pm2, pm3, pm4 = st.columns(4)
    pm1.metric("Total Leases", summary.get("total_leases", 0))
    pm2.metric("Annual Obligation", summary.get("total_annual_obligation", "$0"))
    pm3.metric("Expiring (12 mo)", summary.get("upcoming_expirations", 0))
    pm4.metric("Key Finding", "See below")
    st.info(summary.get("key_finding", ""))

    # Lease Abstractions
    leases = result.get("lease_abstractions", [])
    if leases:
        st.divider()
        st.subheader(f"Lease Abstractions ({len(leases)})")

        sum_df = pd.DataFrame([{
            "Lease": l.get("lease_id", ""),
            "Type": l.get("lease_type", ""),
            "Property": l.get("property_address", "")[:40],
            "Classification": l.get("classification", ""),
            "Monthly Rent": l.get("base_rent", ""),
            "Expires": l.get("expiration_date", ""),
            "Term": f"{l.get('term_months', '')} mo",
        } for l in leases])
        st.dataframe(sum_df, use_container_width=True, hide_index=True)

        for l in leases:
            st.markdown(f'<div class="lease-card"><strong>{l.get("lease_id", "")}</strong> — '
                       f'{l.get("lease_type", "")} | {l.get("classification", "")}<br/>'
                       f'{l.get("property_address", "")}</div>', unsafe_allow_html=True)
            with st.expander(f"Full Details — {l.get('lease_id', '')}"):
                dc1, dc2 = st.columns(2)
                with dc1:
                    st.markdown(f"**Lessee:** {l.get('tenant_lessee', '')}")
                    st.markdown(f"**Lessor:** {l.get('landlord_lessor', '')}")
                    st.markdown(f"**Term:** {l.get('commencement_date', '')} to {l.get('expiration_date', '')}")
                    st.markdown(f"**Base Rent:** {l.get('base_rent', '')}")
                    st.markdown(f"**Annual Rent:** {l.get('annual_rent', '')}")
                    st.markdown(f"**Escalation:** {l.get('escalation_clause', 'None')}")
                with dc2:
                    st.markdown(f"**Security Deposit:** {l.get('security_deposit', '')}")
                    st.markdown(f"**Renewal:** {l.get('renewal_options', 'None')}")
                    st.markdown(f"**Termination:** {l.get('termination_clause', 'None')}")
                    st.markdown(f"**Compliance:** {l.get('compliance_notes', '')}")

                if l.get("key_obligations"):
                    st.markdown("**Key Obligations:**")
                    for o in l["key_obligations"]:
                        st.markdown(f"- {o}")
                if l.get("risks"):
                    for r in l["risks"]:
                        st.warning(r)

    # Financial Analysis
    fin = result.get("financial_analysis", {})
    if fin:
        st.divider()
        st.subheader("Financial Analysis")
        fc1, fc2, fc3 = st.columns(3)
        fc1.metric("Total Commitment", fin.get("total_commitment", ""))
        fc2.metric("Lease Liability (PV)", fin.get("lease_liability_estimate", ""))
        fc3.metric("ROU Asset", fin.get("right_of_use_asset", ""))

        annual = fin.get("annual_breakdown", [])
        if annual:
            fig_fin = go.Figure(go.Bar(
                x=[a.get("year", "") for a in annual],
                y=[float(str(a.get("obligation", "0")).replace("$", "").replace(",", ""))
                   for a in annual],
                marker_color="#1565c0",
                text=[a.get("obligation", "") for a in annual],
                textposition="outside",
            ))
            fig_fin.update_layout(title="Annual Lease Obligations", height=300)
            st.plotly_chart(fig_fin, use_container_width=True)

    # Critical Dates
    dates = result.get("critical_dates_calendar", [])
    if dates:
        st.divider()
        st.subheader("Critical Dates Calendar")
        for d in sorted(dates, key=lambda x: x.get("date", "")):
            pri = d.get("priority", "Medium")
            cls = "date-urgent" if pri == "High" else "date-normal"
            st.markdown(f'<div class="{cls}"><strong>{d.get("date", "")}</strong> — '
                       f'{d.get("lease_id", "")}: {d.get("event", "")} [{pri}]</div>',
                       unsafe_allow_html=True)

    # Compliance Checklist
    comp = result.get("compliance_checklist", [])
    if comp:
        st.divider()
        st.subheader("Compliance Checklist")
        for c in comp:
            status = c.get("status", "Review Needed")
            cls = "comp-pass" if status == "Compliant" else "comp-fail" if status == "Gap" else "comp-review"
            st.markdown(f'<span class="{cls}">[{status}]</span> **{c.get("requirement", "")}** '
                       f'({c.get("standard", "")})', unsafe_allow_html=True)
            if c.get("action"):
                st.caption(f"Action: {c['action']}")

    # Recommendations
    recs = result.get("recommendations", [])
    if recs:
        st.divider()
        st.subheader("Recommendations")
        for r in recs:
            pri = r.get("priority", "Medium")
            icon = "🔴" if pri == "High" else "🟡" if pri == "Medium" else "🟢"
            st.markdown(f"{icon} **{r.get('recommendation', '')}**")
            st.caption(r.get("impact", ""))

    st.divider()
    st.download_button("Download Lease Report (JSON)", json.dumps(result, indent=2),
                       "lease_analysis.json", "application/json")
