import streamlit as st
import pandas as pd
import json

# ==========================================
# 1. PAGE SETUP & PRINT STYLING
# ==========================================
st.set_page_config(layout="wide", page_title="HGDG Assessment Tool")

# This CSS hides the sidebar and menus when you print (Ctrl+P / Cmd+P)
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

st.title("HGDG Project Design Checklist (Expanded Box 7)")
st.write("Automated Assessment Tool for Local Government Units")

# ==========================================
# 2. SECTOR GUIDELINES DICTIONARY
# ==========================================
sector_guidelines = {
    "General / Multi-Sector": "Evaluate using the standard Expanded Box 7 guidelines.",
    "Agriculture and Agrarian Reform": "Focus on access to agricultural inputs (seeds, credit, land titles) for women. Verify if extension services target female farmers.",
    "Natural Resource Management": "Focus on women's access to and control over forest, water, and marine resources, and participation in environmental management.",
    "Infrastructure": "Focus strictly on physical welfare, access to the facility, and employment generated. Verify mitigating strategies for displacement.",
    "Private Sector Development": "Evaluate support for women-owned enterprises, access to non-loan resources, and market linkages.",
    "Education": "Assess school participation rates by sex, gender-sensitive curricula, and female leadership in the education sector.",
    "Health": "Focus on maternal health, reproductive health services, and the gender-sensitive delivery of quality health programs.",
    "Housing and Settlement": "Evaluate women's access to housing units, deeds/titles, and participation in homeowner associations.",
    "Women in Areas under Armed Conflict": "Assess gender-responsive services in refugee camps, security from violence, and participation in peace negotiations.",
    "Justice": "Focus on women's access to legal services, handling of violence against women (VAW) cases, and gender-sensitivity of legal personnel.",
    "Information and Communication Technologies (ICT)": "Assess women's access to ICT training, tech employment, and gender-responsive digital content.",
    "Microfinance": "Evaluate women's access to loans, financial literacy training, and actual control over loan usage.",
    "Labor and Employment": "Focus on equal opportunity employment, workplace safety, anti-sexual harassment mechanisms, and leadership roles.",
    "Child Labor": "Assess interventions targeting girl and boy child laborers, rehabilitation, and education access.",
    "Migration": "Evaluate protection mechanisms for female migrants, safe remittance channels, and reintegration programs.",
    "Funding Facilities": "Assess the integration of GAD criteria in the evaluation and selection of projects for facility funding.",
    "Disaster Risk Reduction and Management (DRRM)": "Focus on gender-specific vulnerabilities, women's participation in DRRM councils, and gender-responsive relief.",
    "Energy": "Evaluate women's access to energy resources, participation in rural electrification, and related livelihood impacts.",
    "Fisheries": "Assess women's roles in pre- and post-harvest fishing activities, access to fishing tech, and coastal resource management.",
    "Tourism": "Focus on women's employment in tourism, protection from exploitation, and support for women-led cultural enterprises.",
    "Development Planning": "Assess the integration of gender analysis into local/regional development plans and GAD budget allocations."
}

# ==========================================
# 3. USER INPUT (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("Project Input")
    
    selected_sector = st.selectbox(
        "Select HGDG Sector",
        options=list(sector_guidelines.keys())
    )
    
    project_title = st.text_input("Project Title")
    project_text = st.text_area("Paste Project Proposal Text Here", height=250)
    
    st.subheader("Additional Context")
    reference_text = st.text_area("Paste Additional Local Memos/Ordinances (Optional)", height=150)
    
    analyze_btn = st.button("Generate HGDG Checklist")

# ==========================================
# 4. REPORT GENERATION & OUTPUT
# ==========================================
if analyze_btn and project_text:
    
    # 4a. Logic prep for the future AI connection
    active_sector_rules = sector_guidelines[selected_sector]
    
    # We display a quick success message (this won't show up on the printed page)
    st.success(f"Successfully loaded specific guidelines for: **{selected_sector}**")
    st.divider()
    
    # 4b. Mock LLM JSON Response (This layout perfectly maps to the Box 7 requirements)
    mock_llm_json = """
    {
      "elements": [
        {"element_number": 1, "element_name": "Involvement of women and men in project conceptualization and design", "response": "Yes", "score": 2.0, "result_comment": "Consultations included both male and female stakeholders."},
        {"element_number": 2, "element_name": "Collection of sex-disaggregated data and gender-related information at the planning stage", "response": "Partly yes", "score": 1.0, "result_comment": "Some demographic data included, but lacks detailed gender constraints analysis."},
        {"element_number": 3, "element_name": "Conduct of gender analysis and identification of gender issues at the project identification stage", "response": "Yes", "score": 2.0, "result_comment": "Clear identification of gender gaps based on the proposal text."},
        {"element_number": 4, "element_name": "Presence of gender equality goals, outcomes, and outputs", "response": "Yes", "score": 2.0, "result_comment": "Specific goals mapped to women's empowerment."},
        {"element_number": 5, "element_name": "Presence of activities and interventions that match the gender issues identified", "response": "Yes", "score": 2.0, "result_comment": "Activities specifically target identified gender gaps."},
        {"element_number": 6, "element_name": "Gender analysis of the likely impact of the designed project", "response": "Partly yes", "score": 1.34, "result_comment": "Analyzed positive impacts but missed potential negative impact mitigation."},
        {"element_number": 7, "element_name": "Presence of monitoring targets and indicators", "response": "Yes", "score": 2.0, "result_comment": "Specific, time-bound targets included."},
        {"element_number": 8, "element_name": "Provision for the collection of sex-disaggregated data in the M&E plan", "response": "Yes", "score": 2.0, "result_comment": "M&E explicitly requires sex-disaggregated tracking."},
        {"element_number": 9, "element_name": "Commitment of resources to address gender issues", "response": "Yes", "score": 2.0, "result_comment": "GAD budget allocation meets the standard requirements."},
        {"element_number": 10, "element_name": "Inclusion of plans to coordinate/relate with the agency's GAD efforts", "response": "Yes", "score": 2.0, "result_comment": "Aligned with the broader municipal GAD action plan."}
      ],
      "total_score": 18.34,
      "interpretation": "Proposed project is gender-responsive"
    }
    """
    
    data = json.loads(mock_llm_json)
    
    # 4c. Printable Report Header
    st.subheader(f"Evaluation Report: {project_title}")
    st.write(f"**Sector Evaluated:** {selected_sector}")
    st.write("---")
    
    # 4d. Render the Box 7 Table
    st.markdown("### Summary Checklist for the Assessment of Proposed Projects")
    df = pd.DataFrame(data["elements"])
    df = df[["element_number", "element_name", "response", "score", "result_comment"]]
    df.columns = ["No.", "Element or Requirement", "Response", "Score", "Result / Comments"]
    
    st.table(df)
    
    # 4e. Render the Summary Scores & Budget Attribution
    st.write("---")
    st.markdown("### Summary of Scores")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total GAD Score (Max 20)", value=data["total_score"])
    with col2:
        st.metric(label="Interpretation", value=data["interpretation"])

    # Calculate GAD Budget Attribution
    score = data["total_score"]
    if score < 4.0:
        attribution = "0%"
    elif 4.0 <= score <= 7.9:
        attribution = "25%"
    elif 8.0 <= score <= 14.9:
        attribution = "50%"
    elif 15.0 <= score <= 19.9:
        attribution = "75%"
    else:
        attribution = "100%"
        
    st.info(f"**GAD Budget Attribution:** {attribution} of the total project cost.")