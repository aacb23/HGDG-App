import streamlit as st
import pandas as pd
import json
import time
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE SETUP & PRINT STYLING
# ==========================================
st.set_page_config(layout="wide", page_title="DILG HGDG Assessment Tool")

hide_elements_during_print = """
    <style>
    @media print {
        [data-testid="stSidebar"] { display: none !important; }
        header { display: none !important; }
        footer { display: none !important; }
        .main .block-container { max-width: 100% !important; padding-top: 0 !important; }
    }
    </style>
"""
st.markdown(hide_elements_during_print, unsafe_allow_html=True)

st.title("HGDG & GEWE Project Assessment Tool")
st.write("Automated DILG Project Evaluation System")

# ==========================================
# 2. ENRICHED SECTOR GUIDELINES (GEWE PERMANENTLY INTEGRATED)
# ==========================================
sector_guidelines = {
    "General / Multi-Sector": "Evaluate using standard Expanded Box 7. Check for cross-cutting GEWE impact indicators.",
    "Agriculture, Fisheries and Forestry": "GEWE (E-11) Focus: Track average income of small-scale producers by sex, and the number of women farmers/fisher folks awarded with instruments of recognition or land free patents.",
    "Infrastructure": "GEWE (E-17) Focus: Track the percentage of employed women in the infrastructure sector, and proportion of women with convenient access to safe drinking water, electricity, and public transport.",
    "Disaster Risk Reduction and Management (DRRM-CCA)": "GEWE (D-10) Focus: Track the ratio of female to male persons affected by a disaster who received assistance, and the incidence of GBV/VAW in times of natural disasters.",
    "Access to Justice": "GEWE (B-6) Focus: Track the extent of recovery and reintegration of women/children survivors of GBV, and the attrition level of VAWC-related cases.",
    "Formal Labor": "GEWE (E-14) Focus: Track the Labor Force Participation Rate by sex, gender gap in wages, and incidence of gender-based violence in the workplace.",
    "Informal Economy": "GEWE (E-15) Focus: Track the share of women in informal non-agriculture employment, and the proportion of formal loans granted to women entrepreneurs.",
    "MSMEs, Trade and Industry": "GEWE (E-12) Focus: Track the proportion of firms owned by women by size, and average monthly income of women in business and entrepreneurship.",
    "Tourism": "GEWE (E-13) Focus: Track the prevalence of GBV against women tourists/workers, and the proportion of women workers reporting specific improvements in situations.",
    "Health": "GEWE (A-2) Focus: Track maternal mortality ratio, unmet need for family planning, and coverage of essential health services for disadvantaged populations.",
    "Education": "GEWE (A-1) Focus: Track completion and cohort survival rates by sex, and the proportion of reported cases of discrimination against female students/faculty resolved.",
    "Women in Bureaucracy, Politics and Governance": "GEWE (C-8) Focus: Track the proportion of seats occupied by women in local and national governing boards and decision-making bodies."
}

# ==========================================
# 3. USER INPUT (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("Project Input")
    
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("System Error: API Key is missing from Streamlit Cloud Secrets. Please add it in the App Settings.")
        st.stop()
    
    selected_sector = st.selectbox(
        "Select HGDG Sector",
        options=list(sector_guidelines.keys())
    )
    
    project_title = st.text_input("Project Title", placeholder="e.g., Rural Water Supply")
    project_text = st.text_area("Paste Project Proposal Text Here", height=300)
    
    st.subheader("Additional Context")
    reference_text = st.text_area("Paste Additional Local Memos (Optional)", height=100)
    
    analyze_btn = st.button("Generate Personalized HGDG Checklist")

# ==========================================
# 4. AI LOGIC & REPORT GENERATION
# ==========================================
if analyze_btn:
    if not api_key or not project_text:
        st.error("Please ensure the API Key is set and paste a project proposal.")
        st.stop()
        
    with st.spinner("Analyzing proposal and generating personalized GEWE assessment...
