"""Smart AI Risk Shield - KYC/AML Sanctions & PEP Screening - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.risk_engine import screen_customer

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #b71c1c 0%, #880e4f 50%, #4a148c 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffcdd2; margin: 0; }
    .approve-box { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .reject-box { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .escalate-box { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .edd-box { background: #e3f2fd; border: 2px solid #1565c0; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-low { border-left: 4px solid #4caf50; }
    .sanction-hit { background: #ffebee; border: 2px solid #f44336; border-radius: 8px;
        padding: 0.8rem; margin-bottom: 0.4rem; }
    .sanction-clear { background: #e8f5e9; border: 1px solid #4caf50; border-radius: 8px;
        padding: 0.5rem; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Smart Risk Shield** screens customers against sanctions lists, PEP databases, "
            "and adverse media to produce evidence-based risk classifications for KYC/AML compliance.")

st.markdown("""<div class="hero"><h1>Smart Risk Shield</h1>
<p>AI-powered KYC/AML sanctions screening and risk classification</p></div>""",
unsafe_allow_html=True)

with st.form("risk_form"):
    customer_profile = st.text_area("Customer Profile", height=250,
        value="Name: Viktor Petrov\n"
              "Date of Birth: 15 March 1968\n"
              "Nationality: Russian Federation\n"
              "Passport: 72 4583921 (issued Moscow, 2019)\n"
              "Current Residence: Dubai, UAE\n\n"
              "Background:\n"
              "- Former Deputy Minister of Energy, Russian Federation (2008-2015)\n"
              "- Board member, Gazprom subsidiary GazEnergoTrade (2015-2020)\n"
              "- Current director of Caspian Minerals Holdings Ltd (registered BVI)\n"
              "- Also director of Petrov Family Trust (Jersey)\n"
              "- Known associate of Arkady Rotenberg (sanctioned individual)\n\n"
              "Declared net worth: $45M\n"
              "Source of wealth: Energy sector consulting and investments\n\n"
              "Banking history:\n"
              "- Previously banked with Deutsche Bank (account closed 2019)\n"
              "- Current accounts at Emirates NBD (personal) and Mashreq Bank (corporate)\n"
              "- Reports monthly wire transfers of $200K-$500K between Dubai and Cyprus\n"
              "- Recent $2.8M property purchase in London (via BVI holding company)")

    c1, c2 = st.columns(2)
    with c1:
        business_relationship = st.selectbox("Business Relationship Type",
            ["Private Banking", "Corporate Banking", "Trade Finance",
             "Wealth Management", "Correspondent Banking", "Retail Banking"],
            index=0)
        products_services = st.multiselect("Products / Services Requested",
            ["Current Account", "Savings Account", "Investment Portfolio",
             "Wire Transfers", "Trade Finance / LC", "Custody Services",
             "Foreign Exchange", "Lending / Credit", "Trust Services"],
            default=["Current Account", "Investment Portfolio", "Wire Transfers",
                     "Foreign Exchange"])
    with c2:
        transaction_volume = st.selectbox("Expected Monthly Transaction Volume",
            ["< $50K", "$50K - $250K", "$250K - $1M", "$1M - $5M", "> $5M"],
            index=2)
        source_of_funds = st.text_input("Declared Source of Funds",
            value="Energy sector consulting fees and investment returns from Caspian region holdings")
        jurisdiction = st.selectbox("Your Institution's Jurisdiction",
            ["United Kingdom", "United States", "European Union", "Switzerland",
             "UAE / DIFC", "Singapore", "Hong Kong", "Cayman Islands"],
            index=0)

    submitted = st.form_submit_button("Screen Customer", type="primary",
                                       use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        customer_profile=customer_profile,
        business_relationship=business_relationship,
        products_services=", ".join(products_services),
        transaction_volume=transaction_volume,
        source_of_funds=source_of_funds,
        jurisdiction=jurisdiction,
    )

    with st.spinner("Screening customer against sanctions, PEP, and adverse media databases..."):
        try:
            result = screen_customer(config, api_key)
        except Exception as e:
            st.error(f"Screening failed: {e}")
            st.stop()

    # Customer Summary
    summary = result.get("customer_summary", {})
    st.subheader("Customer Summary")
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric("Entity Type", summary.get("entity_type", ""))
    sm2.metric("Risk Classification", summary.get("risk_classification", ""))
    sm3.metric("Confidence", f"{summary.get('confidence_score', 0)}%")
    sm4.metric("Nationality", summary.get("nationality", ""))

    # Decision Banner
    rec = result.get("recommendation", {})
    decision = rec.get("decision", "Escalate to MLRO")
    d_cls = ("approve-box" if "Approve" in decision and "EDD" not in decision
             else "reject-box" if decision == "Reject"
             else "edd-box" if "EDD" in decision
             else "escalate-box")
    st.markdown(f'<div class="{d_cls}"><span style="font-size:1.5rem;font-weight:bold">'
               f'{decision}</span><br/>'
               f'{summary.get("one_liner", "")}</div>', unsafe_allow_html=True)

    # Sanctions Screening
    sanctions = result.get("sanctions_screening", {})
    if sanctions:
        st.divider()
        st.subheader("Sanctions Screening")
        sc1, sc2 = st.columns(2)
        with sc1:
            for list_name, key in [("OFAC SDN", "ofac_sdn"), ("EU Sanctions", "eu_sanctions"),
                                    ("UN Sanctions", "un_sanctions"), ("UK Sanctions", "uk_sanctions")]:
                entry = sanctions.get(key, {})
                is_match = entry.get("match", False)
                cls = "sanction-hit" if is_match else "sanction-clear"
                icon = "MATCH" if is_match else "CLEAR"
                st.markdown(f'<div class="{cls}"><strong>{list_name}:</strong> {icon} — '
                           f'{entry.get("details", "")}</div>', unsafe_allow_html=True)

        with sc2:
            fuzzy = sanctions.get("fuzzy_matches", [])
            if fuzzy:
                st.markdown("**Fuzzy / Near Matches:**")
                for f in fuzzy:
                    st.warning(f"**{f.get('name_variant', '')}** ({f.get('list', '')}) — "
                              f"Similarity: {f.get('similarity_score', 0)}% — "
                              f"{f.get('assessment', '')}")
            other = sanctions.get("other_lists", [])
            if other:
                for o in other:
                    cls = "sanction-hit" if o.get("match") else "sanction-clear"
                    icon = "MATCH" if o.get("match") else "CLEAR"
                    st.markdown(f'<div class="{cls}"><strong>{o.get("list_name", "")}:</strong> '
                               f'{icon} — {o.get("details", "")}</div>', unsafe_allow_html=True)

    # PEP Screening & Country Risk side by side
    pc1, pc2 = st.columns(2)
    pep = result.get("pep_screening", {})
    if pep:
        with pc1:
            st.divider()
            st.subheader("PEP Screening")
            pep_status = "PEP IDENTIFIED" if pep.get("is_pep") else "Not a PEP"
            color = "#f44336" if pep.get("is_pep") else "#4caf50"
            st.markdown(f"**Status:** <span style='color:{color};font-weight:bold'>{pep_status}</span>",
                       unsafe_allow_html=True)
            if pep.get("is_pep"):
                st.markdown(f"**Level:** {pep.get('pep_level', '')}")
                st.markdown(f"**Position:** {pep.get('position', '')}")
                st.markdown(f"**Country:** {pep.get('country', '')}")
            st.markdown(f"**Risk Implications:** {pep.get('risk_implications', '')}")
            rca = pep.get("relatives_and_associates", [])
            if rca:
                st.markdown("**Relatives & Close Associates:**")
                rca_df = pd.DataFrame([{
                    "Name": r.get("name", ""),
                    "Relationship": r.get("relationship", ""),
                    "Status": r.get("pep_status", ""),
                } for r in rca])
                st.dataframe(rca_df, use_container_width=True, hide_index=True)

    country = result.get("country_risk", {})
    if country:
        with pc2:
            st.divider()
            st.subheader("Country / Geographic Risk")
            st.markdown(f"**Residence Risk:** {country.get('residence_country_risk', '')}")
            st.markdown(f"**Nationality Risk:** {country.get('nationality_risk', '')}")
            st.markdown(f"**FATF Status:** {country.get('fatf_status', '')}")
            st.markdown(f"**CPI Score:** {country.get('cpi_score', '')}")
            st.markdown(f"**Tax Haven:** {'Yes' if country.get('tax_haven_flag') else 'No'}")
            hrj = country.get("high_risk_jurisdictions", [])
            if hrj:
                st.markdown(f"**High-Risk Jurisdictions:** {', '.join(hrj)}")

    # Risk Scoring Radar Chart
    scoring = result.get("risk_scoring", {})
    if scoring:
        st.divider()
        st.subheader(f"Risk Scoring (Overall: {scoring.get('overall_risk_score', 0)}/100)")
        categories = ["Identity", "Geographic", "Product/Service", "Transaction",
                      "PEP", "Sanctions", "Adverse Media"]
        values = [scoring.get("identity_risk", 0), scoring.get("geographic_risk", 0),
                  scoring.get("product_service_risk", 0), scoring.get("transaction_risk", 0),
                  scoring.get("pep_risk", 0), scoring.get("sanctions_risk", 0),
                  scoring.get("adverse_media_risk", 0)]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(244, 67, 54, 0.2)",
            line=dict(color="#f44336", width=2),
            name="Risk Score",
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            height=400,
            title="Risk Factor Breakdown",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Adverse Media
    media = result.get("adverse_media", [])
    if media:
        st.divider()
        st.subheader("Adverse Media Findings")
        for m in media:
            sev = m.get("severity", "Medium").lower()
            cls = f"risk-{sev}" if sev in ("high", "medium", "low") else "risk-high"
            st.markdown(
                f'<div class="risk-card {cls}">'
                f'<strong>{m.get("headline", "")}</strong><br/>'
                f'Source: {m.get("source_type", "")} | Severity: {m.get("severity", "")} | '
                f'Relevance: {m.get("relevance", "")}<br/>'
                f'{m.get("details", "")}</div>',
                unsafe_allow_html=True,
            )

    # Transaction Risk Indicators
    tx_risks = result.get("transaction_risk_indicators", [])
    if tx_risks:
        st.divider()
        st.subheader("Transaction Risk Indicators")
        tx_df = pd.DataFrame([{
            "Indicator": t.get("indicator", ""),
            "Category": t.get("category", ""),
            "Severity": t.get("severity", ""),
            "Explanation": t.get("explanation", ""),
        } for t in tx_risks])
        st.dataframe(tx_df, use_container_width=True, hide_index=True)

    # Beneficial Ownership
    bo = result.get("beneficial_ownership", {})
    if bo:
        st.divider()
        st.subheader("Beneficial Ownership")
        st.markdown(f"**Transparency:** {bo.get('transparency', '')}")
        st.markdown(f"**Complex Structures:** {'Yes' if bo.get('complex_structures') else 'No'}")
        st.markdown(f"**Shell Company Risk:** {bo.get('shell_company_risk', '')}")
        st.markdown(f"**Nominee Arrangements:** {'Yes' if bo.get('nominee_arrangements') else 'No'}")
        ubos = bo.get("ultimate_beneficial_owners", [])
        if ubos:
            ubo_df = pd.DataFrame([{
                "Name": u.get("name", ""),
                "Ownership %": u.get("ownership_pct", 0),
                "Risk Level": u.get("risk_level", ""),
                "Notes": u.get("notes", ""),
            } for u in ubos])
            st.dataframe(ubo_df, use_container_width=True, hide_index=True)

    # EDD Requirements
    edd = result.get("edd_requirements", [])
    if edd:
        st.divider()
        st.subheader("Enhanced Due Diligence Requirements")
        for e in edd:
            pri = e.get("priority", "Medium").lower()
            cls = f"risk-{'high' if pri == 'critical' else pri}"
            st.markdown(
                f'<div class="risk-card {cls}">'
                f'<strong>{e.get("requirement", "")}</strong><br/>'
                f'Priority: {e.get("priority", "")} | Owner: {e.get("responsible_party", "")} | '
                f'Deadline: {e.get("deadline", "")}</div>',
                unsafe_allow_html=True,
            )

    # Recommendation
    if rec:
        st.divider()
        st.subheader("Recommendation")
        st.info(rec.get("rationale", ""))
        st.markdown(f"**Monitoring Level:** {rec.get('monitoring_level', '')}")
        st.markdown(f"**Review Frequency:** {rec.get('review_frequency', '')}")
        st.markdown(f"**SAR Filing:** {rec.get('sar_filing', '')}")
        if rec.get("conditions"):
            st.markdown("**Conditions:**")
            for c in rec["conditions"]:
                st.markdown(f"- {c}")

    st.divider()
    st.download_button("Download Screening Report (JSON)", json.dumps(result, indent=2),
                       "screening_report.json", "application/json")
