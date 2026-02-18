"""Enterprise AI Projects Showcase - Landing Page for 58 AI-Powered Applications."""

import streamlit as st

st.set_page_config(page_title="Enterprise AI Showcase", page_icon="🏢", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────

CATEGORIES = {
    "Healthcare": "#e53935",
    "Finance": "#1e88e5",
    "Education": "#43a047",
    "Enterprise Ops": "#6d4c41",
    "DevOps & SRE": "#f4511e",
    "Real Estate": "#8e24aa",
    "Compliance & Risk": "#00897b",
    "Productivity": "#fdd835",
    "Energy & Climate": "#00acc1",
    "GovTech": "#5e35b1",
    "Insurance": "#3949ab",
    "Marketing & Sales": "#d81b60",
    "Retail": "#ff8f00",
}

PROJECTS = [
    {
        "num": 1, "dir": "01_AI_Resume_Matcher",
        "name": "AI Resume Matcher",
        "desc": "ATS-style resume scoring against job descriptions with keyword matching, skills alignment, and compatibility analysis.",
        "cat": "Productivity", "icon": "📄",
    },
    {
        "num": 2, "dir": "02_AI_ROI_Calculator",
        "name": "AI ROI Calculator",
        "desc": "Predictive ROI analysis for transformation initiatives with actionable recommendations for change leaders.",
        "cat": "Finance", "icon": "📊",
    },
    {
        "num": 3, "dir": "03_REQUI_Track",
        "name": "REQUI Track",
        "desc": "Automated requirements extraction, classification, and contradiction detection across documents.",
        "cat": "Enterprise Ops", "icon": "📋",
    },
    {
        "num": 4, "dir": "04_Achieve_AI_Habit_Coach",
        "name": "Achieve AI - Habit Coach",
        "desc": "Personal AI habit coach with streak tracking, motivational nudges, and progress analytics.",
        "cat": "Productivity", "icon": "🎯",
    },
    {
        "num": 5, "dir": "05_Marketing_AI_Assistant",
        "name": "Marketing AI Assistant",
        "desc": "SMB marketing copilot that automates content creation, campaign ideas, and data-driven insights.",
        "cat": "Marketing & Sales", "icon": "📢",
    },
    {
        "num": 6, "dir": "06_Loan_Underwriting",
        "name": "Loan Underwriting",
        "desc": "AI-powered loan risk assessment using alternative data for faster, fairer approval decisions.",
        "cat": "Finance", "icon": "🏦",
    },
    {
        "num": 7, "dir": "07_AI_Event_Planner",
        "name": "AI Event Planner",
        "desc": "End-to-end event planning with venue research, vendor matching, budget optimization, and checklists.",
        "cat": "Productivity", "icon": "🎉",
    },
    {
        "num": 8, "dir": "08_Compliance_Audit",
        "name": "Compliance Audit Assistant",
        "desc": "Analyses policies, logs, and communications to detect compliance gaps and generate audit reports.",
        "cat": "Compliance & Risk", "icon": "🔍",
    },
    {
        "num": 9, "dir": "09_Policy_Intelligence",
        "name": "Policy Intelligence System",
        "desc": "Detects conflicting clauses across HR, IT, and compliance documents, maps them to current regulations.",
        "cat": "Compliance & Risk", "icon": "📜",
    },
    {
        "num": 10, "dir": "10_Mock_Interview_Coach",
        "name": "HireQ - Mock Interview Coach",
        "desc": "Role-specific interview simulation with adaptive difficulty, real-time evaluation, and granular feedback.",
        "cat": "Education", "icon": "🎤",
    },
    {
        "num": 11, "dir": "11_AI_Property_Search",
        "name": "AI Property Search",
        "desc": "Personalized property recommendations that understand complex queries and evolve with user preferences.",
        "cat": "Real Estate", "icon": "🏠",
    },
    {
        "num": 12, "dir": "12_Stock_Market_Analysis",
        "name": "Stock Market Analysis Agent",
        "desc": "Ticker analysis with interactive charts, pattern recognition, and buy/sell signal generation.",
        "cat": "Finance", "icon": "📈",
    },
    {
        "num": 13, "dir": "13_Medical_Documentation",
        "name": "Medical Documentation Assistant",
        "desc": "Progressive AI medical documentation from basic transcription to intelligent workflow automation.",
        "cat": "Healthcare", "icon": "🏥",
    },
    {
        "num": 14, "dir": "14_Gym_Fitness_Assistant",
        "name": "Gym & Fitness Assistant",
        "desc": "AI fitness copilot that tracks workouts, measures progress, and keeps you motivated.",
        "cat": "Healthcare", "icon": "💪",
    },
    {
        "num": 15, "dir": "15_GMAT_Prep_Coach",
        "name": "GMAT Prep Coach",
        "desc": "Adaptive GMAT preparation with weakness diagnosis, targeted practice, and study time optimization.",
        "cat": "Education", "icon": "🎓",
    },
    {
        "num": 16, "dir": "16_Mental_Health_Companion",
        "name": "Mental Health Companion",
        "desc": "Safe AI mental health support with vetted therapy content, memory, and multi-agent guardrails.",
        "cat": "Healthcare", "icon": "🧠",
    },
    {
        "num": 17, "dir": "17_VC_Pitch_Generator",
        "name": "Pitch Perfect - VC Pitch Generator",
        "desc": "Personalized investor pitch decks mapped to portfolio themes and investor thesis.",
        "cat": "Finance", "icon": "🚀",
    },
    {
        "num": 18, "dir": "18_Billing_Compliance",
        "name": "LuminaClaims - Billing Compliance",
        "desc": "Billing integrity copilot that reviews time logs, checks compliance, and flags exceptions.",
        "cat": "Finance", "icon": "💰",
    },
    {
        "num": 19, "dir": "19_Retail_Pricing",
        "name": "PriceWise AI - Retail Pricing",
        "desc": "Real-time pricing optimization monitoring sales, competitor prices, and inventory across channels.",
        "cat": "Retail", "icon": "🏷️",
    },
    {
        "num": 20, "dir": "20_Incident_Triage",
        "name": "Incident Triage Assistant",
        "desc": "Correlates alerts from multiple systems, summarizes root causes, and recommends remediation steps.",
        "cat": "DevOps & SRE", "icon": "🚨",
    },
    {
        "num": 21, "dir": "21_Learning_Path_Generator",
        "name": "Learning Path Generator",
        "desc": "Personalized study plans that adapt to pace, strengths, and engagement for maximum learning outcomes.",
        "cat": "Education", "icon": "📚",
    },
    {
        "num": 22, "dir": "22_CareCompass",
        "name": "CareCompass",
        "desc": "Healthcare navigation with automated coverage queries, cost estimation, and appointment booking.",
        "cat": "Healthcare", "icon": "🧭",
    },
    {
        "num": 23, "dir": "23_Claims_Processing",
        "name": "Claims Processing Assistant",
        "desc": "Automates Section 75 and chargeback claims from intake to resolution with human-in-the-loop.",
        "cat": "Finance", "icon": "📝",
    },
    {
        "num": 24, "dir": "24_AI_Mortgage_Consultant",
        "name": "MoJo - AI Mortgage Consultant",
        "desc": "Research assistant correlating financial data, real estate market, and recommended mortgage products.",
        "cat": "Real Estate", "icon": "🏘️",
    },
    {
        "num": 25, "dir": "25_Wellness_Nutrition",
        "name": "NutriNext - Wellness Platform",
        "desc": "Biomarker-driven nutritional analysis detecting deficiencies and recommending supplements.",
        "cat": "Healthcare", "icon": "🥗",
    },
    {
        "num": 26, "dir": "26_Smart_Course_Generator",
        "name": "AI Contenta - Course Generator",
        "desc": "Automated course content creation with aligned assessments adapted to learner needs.",
        "cat": "Education", "icon": "🎒",
    },
    {
        "num": 27, "dir": "27_AI_Risk_Shield",
        "name": "AI Risk Shield",
        "desc": "GenAI compliance assistant scanning sanctions, blacklists, and PEPs for risk classification.",
        "cat": "Compliance & Risk", "icon": "🛡️",
    },
    {
        "num": 28, "dir": "28_Visa_Application_Agent",
        "name": "Visa Application Agent",
        "desc": "B1/B2 visa DS-160 guidance, structured interview prep, and consulate process navigation.",
        "cat": "Productivity", "icon": "✈️",
    },
    {
        "num": 29, "dir": "29_vCISO",
        "name": "vCISO",
        "desc": "Enterprise-grade cybersecurity guidance at SMB scale covering hygiene, compliance, and incident response.",
        "cat": "Compliance & Risk", "icon": "🔐",
    },
    {
        "num": 30, "dir": "30_AI_Spend_Monitor",
        "name": "Heimdall - AI Spend Monitor",
        "desc": "FinOps billing anomaly detection with vendor analysis and automated resolution workflows.",
        "cat": "Finance", "icon": "👁️",
    },
    {
        "num": 31, "dir": "31_Due_Diligence_Generator",
        "name": "Due Diligence Generator",
        "desc": "M&A technology due diligence with automated scoring, questionnaires, and valuation impact analysis.",
        "cat": "Finance", "icon": "🔬",
    },
    {
        "num": 32, "dir": "32_Medical_Procedure_Prep",
        "name": "Preppy - Medical Procedure Prep",
        "desc": "Pre-procedure patient guidance with anxiety management, preparation checklists, and plain-language explanations.",
        "cat": "Healthcare", "icon": "💊",
    },
    {
        "num": 33, "dir": "33_Sports_Stats_QA",
        "name": "SportsMuse - Sports Stats Q&A",
        "desc": "Natural language sports statistics platform with interactive charts, comparisons, and trivia.",
        "cat": "Productivity", "icon": "⚽",
    },
    {
        "num": 34, "dir": "34_Lease_Management",
        "name": "LeaseIQ - Lease Management",
        "desc": "Automated lease abstraction with IFRS 16/ASC 842 compliance and critical date tracking.",
        "cat": "Real Estate", "icon": "📑",
    },
    {
        "num": 35, "dir": "35_Executive_Briefing",
        "name": "Executive Briefing Writer",
        "desc": "Data-driven C-suite briefings aggregating performance metrics, market shifts, and team highlights.",
        "cat": "Enterprise Ops", "icon": "📰",
    },
    {
        "num": 36, "dir": "36_Conversational_Assessment",
        "name": "MasterEd - Conversational Assessment",
        "desc": "Socratic dialogue evaluation testing deeper cognitive skills beyond surface-level answers.",
        "cat": "Education", "icon": "💬",
    },
    {
        "num": 37, "dir": "37_Infra_Code_Generator",
        "name": "InfraAgent - IaC Generator",
        "desc": "Natural language to production-ready Terraform and CloudFormation following enterprise standards.",
        "cat": "DevOps & SRE", "icon": "🏗️",
    },
    {
        "num": 38, "dir": "38_Contract_Assistant",
        "name": "Athena - Contract Assistant",
        "desc": "Federal solicitation analysis with compliance checking, proposal strategy, and win probability scoring.",
        "cat": "GovTech", "icon": "📎",
    },
    {
        "num": 39, "dir": "39_Customer_Insights",
        "name": "CUE - Customer Insights Engine",
        "desc": "Unified customer intelligence from CRM, tickets, transcripts, and surveys for evidence-based decisions.",
        "cat": "Marketing & Sales", "icon": "👥",
    },
    {
        "num": 40, "dir": "40_AWS_Compliance",
        "name": "AWSentinel - AWS Compliance",
        "desc": "Automated AWS config scoring against CIS/SOC2 benchmarks with auto-remediation guidance.",
        "cat": "DevOps & SRE", "icon": "☁️",
    },
    {
        "num": 41, "dir": "41_SmartSchool_Reviser",
        "name": "SmartSchool Reviser",
        "desc": "Transforms school newsletters into personalized revision activities, quizzes, and study schedules.",
        "cat": "Education", "icon": "📝",
    },
    {
        "num": 42, "dir": "42_Concept_Mastery_Grader",
        "name": "Concept Mastery Grader",
        "desc": "Process-based grading that evaluates conceptual understanding, not just final answers, with AI detection.",
        "cat": "Education", "icon": "✅",
    },
    {
        "num": 43, "dir": "43_Enterprise_Architecture",
        "name": "EA4All - Enterprise Architecture",
        "desc": "TOGAF-based architecture blueprints mapping business, application, data, and technology layers.",
        "cat": "Enterprise Ops", "icon": "🏛️",
    },
    {
        "num": 44, "dir": "44_POS_Recommendation",
        "name": "PosPal - POS Recommendation",
        "desc": "POS system comparison for SMB merchants with cost analysis and implementation guidance.",
        "cat": "Retail", "icon": "💳",
    },
    {
        "num": 45, "dir": "45_Venture_Research",
        "name": "VentureScope - Venture Research",
        "desc": "Startup deal screening and investment research briefs aligned with fund thesis.",
        "cat": "Finance", "icon": "🔭",
    },
    {
        "num": 46, "dir": "46_Ops_Assistant",
        "name": "OpsAgent - Operations Assistant",
        "desc": "Shared platform operations planning for databases, ETL, reporting with compliance and automation analysis.",
        "cat": "Enterprise Ops", "icon": "⚙️",
    },
    {
        "num": 47, "dir": "47_Smart_Risk_Shield",
        "name": "Smart Risk Shield",
        "desc": "KYC/AML sanctions and PEP screening with adverse media analysis and risk scoring radar.",
        "cat": "Compliance & Risk", "icon": "🛡️",
    },
    {
        "num": 48, "dir": "48_Chaos_Agent",
        "name": "ChaosAgent",
        "desc": "AI-powered Kubernetes chaos engineering with natural language failure scenarios and resilience insights.",
        "cat": "DevOps & SRE", "icon": "💥",
    },
    {
        "num": 49, "dir": "49_Clinical_Consent",
        "name": "ConsentAI",
        "desc": "Transforms dense clinical trial consent forms into interactive Q&A and accessible patient summaries.",
        "cat": "Healthcare", "icon": "🧪",
    },
    {
        "num": 50, "dir": "50_Software_Factory",
        "name": "BlueprintAI - Software Factory",
        "desc": "Converts high-level business concepts into enterprise-grade technical blueprints and architecture docs.",
        "cat": "Enterprise Ops", "icon": "🏭",
    },
    {
        "num": 51, "dir": "51_AI_Insurance",
        "name": "AI-nsurance",
        "desc": "Automated insurance claims processing with document sorting, coverage analysis, and fraud detection.",
        "cat": "Insurance", "icon": "🏢",
    },
    {
        "num": 52, "dir": "52_Grid_Connection",
        "name": "GridFlow",
        "desc": "Evaluates power grid interconnection for renewable plants and data centers with queue and cost analysis.",
        "cat": "Energy & Climate", "icon": "⚡",
    },
    {
        "num": 53, "dir": "53_Calibrate",
        "name": "Calibrate",
        "desc": "AI job search leverage tool mapping strengths, aspirations, and market positioning to optimal roles.",
        "cat": "Productivity", "icon": "🧭",
    },
    {
        "num": 54, "dir": "54_Pricing_Strategy",
        "name": "PriceWise - Pricing Strategy",
        "desc": "Strategic retail pricing with elasticity analysis, competitive simulation, and revenue forecasting.",
        "cat": "Retail", "icon": "📉",
    },
    {
        "num": 55, "dir": "55_Patient_Advocate",
        "name": "PatientEdge - Health Advocate",
        "desc": "Explains prescriptions, finds cost-effective alternatives, and coordinates care to reduce patient costs.",
        "cat": "Healthcare", "icon": "❤️",
    },
    {
        "num": 56, "dir": "56_Medical_Claim_Review",
        "name": "ClaimLens - Claim Review",
        "desc": "Insurer-side medical claim review with coding accuracy checks, fraud detection, and payment calculation.",
        "cat": "Insurance", "icon": "🔎",
    },
    {
        "num": 57, "dir": "57_RegTech",
        "name": "RegWatch - RegTech Intelligence",
        "desc": "Regulatory change tracking with gap analysis, compliance roadmap, and cross-framework mapping.",
        "cat": "Compliance & Risk", "icon": "⚖️",
    },
    {
        "num": 58, "dir": "58_CityPlan_AI",
        "name": "CityPlanAI",
        "desc": "Zoning application review linking submissions with parcel data and rules for compliance memos.",
        "cat": "GovTech", "icon": "🏙️",
    },
]


# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .main .block-container { max-width: 1200px; padding-top: 1rem; }

    .hero-section {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
        animation: shimmer 8s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(5%, 5%); }
    }
    .hero-section h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
    }
    .hero-section .subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        position: relative;
    }
    .hero-section .stat-row {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 1.5rem;
        position: relative;
    }
    .hero-section .stat-item {
        text-align: center;
    }
    .hero-section .stat-num {
        font-size: 2rem;
        font-weight: 800;
        color: #e2e8f0;
    }
    .hero-section .stat-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .category-pill {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        color: white;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .project-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .project-card:hover {
        border-color: #a78bfa;
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.15);
        transform: translateY(-2px);
    }
    .project-card .card-num {
        font-size: 0.7rem;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 1px;
    }
    .project-card .card-icon {
        font-size: 1.8rem;
        margin: 0.3rem 0;
    }
    .project-card .card-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.2rem 0 0.4rem 0;
        line-height: 1.3;
    }
    .project-card .card-desc {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.5;
    }
    .project-card .card-dir {
        font-size: 0.65rem;
        color: #94a3b8;
        font-family: monospace;
        margin-top: 0.6rem;
        padding-top: 0.5rem;
        border-top: 1px solid #f1f5f9;
    }

    .filter-section {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }

    .stats-bar {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    .stats-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.3rem 0.6rem;
        font-size: 0.75rem;
        color: #475569;
    }
    .stats-chip .chip-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .stats-chip .chip-count {
        font-weight: 700;
        color: #1e293b;
    }

    .howto-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
        border: 1px solid #86efac;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .howto-box h3 {
        margin: 0 0 0.8rem 0;
        color: #166534;
        font-family: 'Inter', sans-serif;
    }
    .howto-box code {
        background: #166534;
        color: #f0fdf4;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .howto-box .step {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        margin-bottom: 0.6rem;
    }
    .howto-box .step-num {
        background: #166534;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .howto-box .step-text {
        color: #1e293b;
        font-size: 0.9rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────

cat_count = len(set(p["cat"] for p in PROJECTS))

st.markdown(f"""
<div class="hero-section">
    <h1>Enterprise AI Projects Showcase</h1>
    <p class="subtitle">A curated collection of AI-powered enterprise applications built with
    Claude &amp; Streamlit</p>
    <div class="stat-row">
        <div class="stat-item">
            <div class="stat-num">{len(PROJECTS)}</div>
            <div class="stat-label">Projects</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">{cat_count}</div>
            <div class="stat-label">Categories</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">100%</div>
            <div class="stat-label">AI-Powered</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── How to Run ────────────────────────────────────────────────────────────────

with st.expander("How do I run these apps?", expanded=False):
    st.markdown("""
    <div class="howto-box">
        <h3>Running Any Project</h3>
        <p style="color:#475569; font-size:0.9rem; margin-bottom:1rem;">
            Each project is a standalone Streamlit app powered by Claude (Anthropic).
            You'll need Python 3.10+, an Anthropic API key, and the project source code.
        </p>
        <div class="step">
            <span class="step-num">1</span>
            <span class="step-text">
                <strong>Clone the repo</strong> and navigate to a project folder<br/>
                <code>cd 01_AI_Resume_Matcher</code>
            </span>
        </div>
        <div class="step">
            <span class="step-num">2</span>
            <span class="step-text">
                <strong>Create a virtual environment</strong> and install dependencies<br/>
                <code>python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt</code>
            </span>
        </div>
        <div class="step">
            <span class="step-num">3</span>
            <span class="step-text">
                <strong>Add your API key</strong> &mdash; copy <code>.env.example</code> to <code>.env</code> and paste your Anthropic API key, or enter it in the app sidebar<br/>
                <code>cp .env.example .env && nano .env</code>
            </span>
        </div>
        <div class="step">
            <span class="step-num">4</span>
            <span class="step-text">
                <strong>Launch the app</strong><br/>
                <code>streamlit run app.py</code>
            </span>
        </div>
        <p style="color:#475569; font-size:0.85rem; margin-top:1rem; margin-bottom:0;">
            The app opens at <code>http://localhost:8501</code>. Each project comes pre-filled with
            realistic sample data so you can test immediately.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Tech Stack (all 58 projects):**
    - **UI:** Streamlit
    - **AI:** Anthropic Claude Sonnet 4.5
    - **Charts:** Plotly + Pandas
    - **Pattern:** Structured JSON output from LLM, parsed and rendered as interactive dashboards
    """)

# ── Category Stats Bar ───────────────────────────────────────────────────────

cat_counts = {}
for p in PROJECTS:
    cat_counts[p["cat"]] = cat_counts.get(p["cat"], 0) + 1
sorted_cats = sorted(cat_counts.items(), key=lambda x: -x[1])

chips_html = ""
for cat, count in sorted_cats:
    color = CATEGORIES.get(cat, "#666")
    chips_html += (f'<span class="stats-chip">'
                   f'<span class="chip-dot" style="background:{color}"></span>'
                   f'{cat} <span class="chip-count">{count}</span></span>')

st.markdown(f'<div class="stats-bar">{chips_html}</div>', unsafe_allow_html=True)


# ── Filters ──────────────────────────────────────────────────────────────────

fc1, fc2 = st.columns([3, 1])
with fc1:
    search = st.text_input("Search projects", placeholder="Type to filter by name or description...")
with fc2:
    cat_filter = st.selectbox("Category", ["All"] + [c[0] for c in sorted_cats])

# Apply filters
filtered = PROJECTS
if search:
    q = search.lower()
    filtered = [p for p in filtered if q in p["name"].lower() or q in p["desc"].lower()]
if cat_filter != "All":
    filtered = [p for p in filtered if p["cat"] == cat_filter]

st.caption(f"Showing **{len(filtered)}** of {len(PROJECTS)} projects")


# ── Project Grid ─────────────────────────────────────────────────────────────

COLS_PER_ROW = 3
rows = [filtered[i:i + COLS_PER_ROW] for i in range(0, len(filtered), COLS_PER_ROW)]

for row in rows:
    cols = st.columns(COLS_PER_ROW)
    for idx, proj in enumerate(row):
        color = CATEGORIES.get(proj["cat"], "#666")
        with cols[idx]:
            st.markdown(f"""
            <div class="project-card">
                <span class="card-num">#{proj["num"]:02d}</span>
                <span class="category-pill" style="background:{color}; float:right;">{proj["cat"]}</span>
                <div class="card-icon">{proj["icon"]}</div>
                <div class="card-title">{proj["name"]}</div>
                <div class="card-desc">{proj["desc"]}</div>
                <div class="card-dir">
                    <code>cd {proj["dir"]} && streamlit run app.py</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
    # Spacer between rows
    st.markdown("<div style='height: 0.8rem'></div>", unsafe_allow_html=True)


# ── Footer ───────────────────────────────────────────────────────────────────

st.divider()
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.8rem; padding:1rem 0;">
    <strong>Enterprise AI Projects Showcase</strong><br/>
    Built with Claude (Anthropic) &amp; Streamlit<br/><br/>
    <a href="https://github.com/HighviewOne/enterprise-ai-showcase" target="_blank"
       style="color:#a78bfa; text-decoration:none; font-weight:600;">
       View on GitHub
    </a>
</div>
""", unsafe_allow_html=True)
