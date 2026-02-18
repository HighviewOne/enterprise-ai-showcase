"""CityPlanAI - Zoning Insight Agent - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.zoning_engine import analyze_zoning

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #283593 0%, #1565c0 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #90caf9; margin: 0; }
    .rec-approve { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .rec-deny { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .rec-conditions { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .rec-review { background: #e3f2fd; border: 2px solid #1565c0; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .bulk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .bulk-compliant { border-left: 4px solid #4caf50; }
    .bulk-noncompliant { border-left: 4px solid #f44336; }
    .bulk-waiver { border-left: 4px solid #ff9800; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**CityPlanAI** reviews zoning applications against land-use regulations "
            "and generates comprehensive compliance memos with recommendations.")

st.markdown("""<div class="hero"><h1>CityPlanAI</h1>
<p>AI-powered zoning compliance analysis and land-use application review</p></div>""",
unsafe_allow_html=True)

with st.form("zoning_form"):
    application_details = st.text_area("Zoning Application Details", height=200,
        value="Parcel ID: Block 1067, Lot 23 (Manhattan)\n"
              "Address: 245 West 14th Street, New York, NY 10011\n"
              "Lot Size: 15,000 SF (100ft x 150ft)\n"
              "Applicant: Chelsea Gateway Development LLC\n\n"
              "Proposed Development:\n"
              "- 12-story mixed-use building (148 feet total height)\n"
              "- Ground floor: 8,500 SF retail (restaurant and neighborhood retail)\n"
              "- Floors 2-12: 95 residential units (mix of studios, 1BR, 2BR)\n"
              "  - 24 units (25%) designated affordable at 80% AMI\n"
              "- Total floor area: 120,000 SF\n"
              "- Proposed FAR: 8.0\n"
              "- Cellar: 45-space parking garage, bike storage for 95 bikes\n"
              "- Rooftop: Common terrace with garden, solar panels\n"
              "- Rear yard: 30-foot setback with landscaped courtyard\n"
              "- Building materials: Brick and glass facade with setbacks at floors 8 and 11")

    c1, c2 = st.columns(2)
    with c1:
        zoning_designation = st.text_area("Current Zoning Designation", height=120,
            value="C4-4A (General Commercial District)\n\n"
                  "C4-4A is a contextual commercial zoning district in NYC that allows:\n"
                  "- Commercial uses (Use Groups 5-9, 11-12)\n"
                  "- Residential uses (equivalent to R7A)\n"
                  "- Community facility uses (Use Groups 3-4)\n"
                  "- Maximum FAR: 4.0 commercial / 4.6 residential (5.01 with Inclusionary Housing)\n"
                  "- Maximum building height: 80 feet (95 feet with qualifying ground floor)\n"
                  "- Required rear yard: 30 feet\n"
                  "- No parking requirement for residential under 15 units in Transit Zone")

        applicant_info = st.text_area("Applicant Information", height=100,
            value="Applicant: Chelsea Gateway Development LLC\n"
                  "Principal: Marcus Chen, Managing Partner\n"
                  "Architect: Foster + Partners (NYC office)\n"
                  "Attorney: Fried, Frank, Harris, Shriver & Jacobson LLP\n"
                  "Previous projects: 3 mixed-use developments in Brooklyn (approved 2021-2023)")

    with c2:
        proposed_changes = st.text_area("Proposed Changes / Variances Requested", height=120,
            value="Variances Requested:\n"
                  "1. Height Variance: Requesting 148 ft where 95 ft maximum allowed\n"
                  "   (53 ft / 56% deviation)\n"
                  "2. FAR Variance: Requesting 8.0 FAR where 5.01 maximum allowed with\n"
                  "   Inclusionary Housing bonus (2.99 / 60% deviation)\n"
                  "3. Applicant argues unique lot configuration and adjacency to\n"
                  "   high-rise district (C6-3A to the north) justifies additional bulk\n"
                  "4. Offering 25% affordable units (above 20% MIH requirement) as\n"
                  "   community benefit in exchange for bulk relief")

        location_context = st.text_area("Location Context", height=100,
            value="Location: Chelsea neighborhood, Manhattan\n"
                  "- Adjacent to C6-3A district (allows FAR 12.0, towers to 300+ ft)\n"
                  "- 2 blocks from High Line park\n"
                  "- Within Chelsea Historic District (partial - western boundary)\n"
                  "- Transit: A/C/E/L/1/2/3 subway lines within 3 blocks\n"
                  "- Surrounding context: Mix of 4-6 story buildings and newer 15-20 story towers\n"
                  "- Notable nearby: Google NYC HQ, Chelsea Market, The Standard Hotel")

    submitted = st.form_submit_button("Analyze Application", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(application_details=application_details,
                  zoning_designation=zoning_designation,
                  proposed_changes=proposed_changes,
                  applicant_info=applicant_info,
                  location_context=location_context)

    with st.spinner("Analyzing zoning application and regulations..."):
        try:
            result = analyze_zoning(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Application Summary
    app_sum = result.get("application_summary", {})
    st.subheader("Application Summary")
    am1, am2, am3, am4 = st.columns(4)
    am1.metric("Parcel", app_sum.get("parcel_id", ""))
    am2.metric("Application Type", app_sum.get("application_type", ""))
    am3.metric("Current Zoning", app_sum.get("current_zoning", ""))
    km = app_sum.get("key_metrics", {})
    am4.metric("Proposed FAR", km.get("proposed_far", "N/A"))

    # Recommendation
    rec = result.get("recommendation", {})
    decision = rec.get("decision", "Further Review Required")
    if "Approve with" in decision:
        r_cls = "rec-conditions"
    elif "Approve" in decision:
        r_cls = "rec-approve"
    elif "Deny" in decision:
        r_cls = "rec-deny"
    else:
        r_cls = "rec-review"
    st.markdown(f'<div class="{r_cls}"><span style="font-size:1.5rem;font-weight:bold">'
                f'{decision}</span> (Confidence: {rec.get("confidence", "")})<br/>'
                f'{rec.get("rationale", "")}</div>', unsafe_allow_html=True)

    # Zoning Compliance Overview
    zc = result.get("zoning_compliance", {})
    if zc:
        st.divider()
        st.subheader("Zoning Compliance Overview")
        zc1, zc2 = st.columns(2)
        with zc1:
            st.markdown(f"**Overall Status:** {zc.get('overall_status', '')}")
            st.markdown(f"**Proposed Use Status:** {zc.get('proposed_use_status', '')}")
            st.markdown(f"**District Description:** {zc.get('zoning_district_description', '')}")
        with zc2:
            if zc.get("permitted_uses"):
                st.markdown("**Permitted Uses:**")
                for u in zc["permitted_uses"][:5]:
                    st.markdown(f"- {u}")

    # Bulk Regulations - Plotly compliance checklist
    bulk = result.get("bulk_regulations", [])
    if bulk:
        st.divider()
        st.subheader("Bulk Regulations Compliance")

        regs = [b.get("regulation", "")[:30] for b in bulk]
        statuses = [b.get("status", "Unknown") for b in bulk]
        status_map = {"Compliant": 1, "Non-Compliant": -1, "Waiver Needed": 0}
        vals = [status_map.get(s, 0) for s in statuses]
        colors = ["#4caf50" if s == "Compliant" else "#f44336" if s == "Non-Compliant"
                  else "#ff9800" for s in statuses]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=regs, y=[1]*len(regs), text=statuses, textposition="auto",
            marker_color=colors, name="Status"
        ))
        fig.update_layout(
            title="Compliance Checklist by Regulation Category",
            yaxis=dict(showticklabels=False, range=[0, 1.5]),
            height=350, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bulk detail table
        bulk_df = pd.DataFrame([{
            "Regulation": b.get("regulation", ""),
            "Allowed": b.get("allowed", ""),
            "Proposed": b.get("proposed", ""),
            "Status": b.get("status", ""),
            "Deviation": b.get("deviation", ""),
        } for b in bulk])
        st.dataframe(bulk_df, use_container_width=True, hide_index=True)

    # Use Group Analysis & Variance Assessment side by side
    uc1, uc2 = st.columns(2)
    use_group = result.get("use_group_analysis", {})
    if use_group:
        with uc1:
            st.divider()
            st.subheader("Use Group Analysis")
            st.markdown(f"**Mixed-Use Compatibility:** {use_group.get('mixed_use_compatibility', '')}")
            if use_group.get("conflicts"):
                st.markdown("**Conflicts:**")
                for c in use_group["conflicts"]:
                    st.warning(c)
            if use_group.get("proposed_use_groups"):
                st.markdown("**Proposed Use Groups:**")
                for u in use_group["proposed_use_groups"]:
                    st.markdown(f"- {u}")

    variance = result.get("variance_assessment", {})
    if variance:
        with uc2:
            st.divider()
            st.subheader("Variance Assessment")
            st.markdown(f"**Variance Needed:** {'Yes' if variance.get('variance_needed') else 'No'}")
            st.markdown(f"**Type:** {variance.get('variance_type', '')}")
            st.markdown(f"**Likelihood of Approval:** {variance.get('likelihood_of_approval', '')}")
            st.markdown(f"**Hardship Argument:** {variance.get('hardship_argument', '')}")
            for v in variance.get("variances_required", []):
                with st.expander(f"Variance: {v.get('item', '')}"):
                    st.markdown(f"**Relief Requested:** {v.get('requested_relief', '')}")
                    st.markdown(f"**Justification Strength:** {v.get('justification_strength', '')}")
                    st.markdown(f"**Analysis:** {v.get('analysis', '')}")

    # Environmental Review
    env = result.get("environmental_review", {})
    if env:
        st.divider()
        st.subheader("Environmental Review")
        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown(f"**Review Required:** {'Yes' if env.get('review_required') else 'No'}")
            st.markdown(f"**Review Type:** {env.get('review_type', '')}")
            st.markdown(f"**Estimated Timeline:** {env.get('estimated_timeline', '')}")
        with ec2:
            if env.get("key_environmental_concerns"):
                st.markdown("**Key Concerns:**")
                for c in env["key_environmental_concerns"]:
                    st.markdown(f"- {c}")
            if env.get("required_studies"):
                st.markdown("**Required Studies:**")
                for s in env["required_studies"]:
                    st.markdown(f"- {s}")

    # Community Impact
    community = result.get("community_impact", {})
    if community:
        st.divider()
        st.subheader("Community Impact")
        ci1, ci2 = st.columns(2)
        with ci1:
            st.markdown(f"**Traffic:** {community.get('traffic_impact', '')}")
            st.markdown(f"**Shadows:** {community.get('shadow_analysis', '')}")
            st.markdown(f"**Infrastructure:** {community.get('infrastructure_capacity', '')}")
        with ci2:
            st.markdown(f"**Neighborhood Character:** {community.get('neighborhood_character', '')}")
            st.markdown(f"**Public Benefit:** {community.get('public_benefit', '')}")
            st.markdown(f"**Displacement Risk:** {community.get('displacement_risk', '')}")

    # Landmark Considerations
    landmark = result.get("landmark_considerations", {})
    if landmark:
        st.divider()
        st.subheader("Landmark Considerations")
        st.markdown(f"**In Historic District:** {'Yes' if landmark.get('in_historic_district') else 'No'}")
        st.markdown(f"**Landmark Proximity:** {landmark.get('landmark_proximity', '')}")
        st.markdown(f"**Commission Review Required:** {landmark.get('landmark_commission_review', '')}")
        st.markdown(f"**Impact on Historic Resources:** {landmark.get('impact_on_historic_resources', '')}")

    # Conditions
    conditions = result.get("conditions", [])
    if conditions:
        st.divider()
        st.subheader("Conditions of Approval")
        cond_df = pd.DataFrame([{
            "Condition": c.get("condition", ""),
            "Category": c.get("category", ""),
            "Rationale": c.get("rationale", ""),
        } for c in conditions])
        st.dataframe(cond_df, use_container_width=True, hide_index=True)

    # Comparable Precedents
    precedents = result.get("comparable_precedents", [])
    if precedents:
        st.divider()
        st.subheader("Comparable Precedents")
        prec_df = pd.DataFrame([{
            "Case": p.get("case", ""),
            "Location": p.get("location", ""),
            "Outcome": p.get("outcome", ""),
            "Relevance": p.get("relevance", ""),
        } for p in precedents])
        st.dataframe(prec_df, use_container_width=True, hide_index=True)

    # Public Hearing Preparation
    hearing = result.get("public_hearing_preparation", {})
    if hearing:
        st.divider()
        st.subheader("Public Hearing Preparation")
        objections = hearing.get("likely_objections", [])
        if objections:
            st.markdown("**Likely Objections & Responses:**")
            for o in objections:
                with st.expander(o.get("objection", "")):
                    st.markdown(f"**Response Strategy:** {o.get('response_strategy', '')}")
                    st.markdown(f"**Supporting Evidence:** {o.get('supporting_evidence', '')}")
        if hearing.get("community_benefits_to_highlight"):
            st.markdown("**Community Benefits to Highlight:**")
            for b in hearing["community_benefits_to_highlight"]:
                st.markdown(f"- {b}")
        if hearing.get("stakeholder_engagement"):
            st.markdown(f"**Stakeholder Engagement:** {hearing['stakeholder_engagement']}")

    # Key Strengths & Concerns
    if rec.get("key_strengths") or rec.get("key_concerns"):
        st.divider()
        sc1, sc2 = st.columns(2)
        with sc1:
            if rec.get("key_strengths"):
                st.subheader("Key Strengths")
                for s in rec["key_strengths"]:
                    st.success(s)
        with sc2:
            if rec.get("key_concerns"):
                st.subheader("Key Concerns")
                for c in rec["key_concerns"]:
                    st.warning(c)

    st.divider()
    st.download_button("Download Zoning Memo (JSON)", json.dumps(result, indent=2),
                       "zoning_memo.json", "application/json")
