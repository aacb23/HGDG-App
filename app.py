import streamlit as st
import pandas as pd
import json
from google import genai
from google.genai import types

# ==========================================
# 1. PAGE SETUP & PRINT STYLING
# ==========================================
st.set_page_config(layout="wide", page_title="HGDG Assessment Tool")

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
    
    # Secure API Key Input
    api_key = st.text_input("Gemini API Key", type="password", help="Get this from Google AI Studio")
    
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
# 4. AI LOGIC & REPORT GENERATION
# ==========================================
if analyze_btn:
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
        st.stop()
    if not project_text:
        st.error("Please paste a project proposal.")
        st.stop()
        
    with st.spinner("Analyzing proposal against DILG & HGDG guidelines... This takes about 10 seconds."):
        try:
            # Initialize the AI Client
            client = genai.Client(api_key=api_key)
            active_sector_rules = sector_guidelines[selected_sector]
            
            # Build the strict prompt
            final_prompt = f"""
            You are an expert evaluator for the Department of the Interior and Local Government (DILG).
            Evaluate the provided local government project proposal using the Harmonized Gender and Development Guidelines (HGDG).
            
            Evaluate against the 10 core elements of the HGDG Box 7. Assign a score of 0 (No), a partial score (Partly Yes), or the maximum score (Yes).
            
            Sector Specific Rules to Apply:
            {active_sector_rules}
            
            Additional Context:
            {reference_text}
            
            Project Proposal:
            {project_text}
            
            You MUST output your evaluation in valid JSON format with this EXACT structure:
            {{
              "elements": [
                {{
                  "element_number": 1,
                  "element_name": "Involvement of women and men in project conceptualization and design",
                  "response": "Yes / Partly yes / No",
                  "score": 2.0,
                  "result_comment": "Brief justification based on the text..."
                }}
              ],
              "total_score": 18.5,
              "interpretation": "Gender-responsive"
            }}
            """
            
            # Send to Gemini and enforce JSON format
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=final_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                ),
            )
            
            # Parse the real AI response
            data = json.loads(response.text)
            
            # --- RENDER THE REPORT ---
            st.success(f"Analysis Complete for: **{selected_sector}**")
            st.divider()
            
            st.subheader(f"Evaluation Report: {project_title}")
            st.write(f"**Sector Evaluated:** {selected_sector}")
            st.write("---")
            
            st.markdown("### Summary Checklist for the Assessment of Proposed Projects")
            df = pd.DataFrame(data["elements"])
            df = df[["element_number", "element_name", "response", "score", "result_comment"]]
            df.columns = ["No.", "Element or Requirement", "Response", "Score", "Result / Comments"]
            
            st.table(df)
            
            st.write("---")
            st.markdown("### Summary of Scores")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Total GAD Score (Max 20)", value=data["total_score"])
            with col2:
                st.metric(label="Interpretation", value=data["interpretation"])

            # Calculate Budget Attribution
            score = float(data["total_score"])
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
            
        except Exception as e:
            st.error(f"An error occurred: {e}. Please ensure your API key is correct and try again.")