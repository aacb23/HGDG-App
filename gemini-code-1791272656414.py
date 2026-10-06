import streamlit as st
import pandas as pd
import json
import tempfile
import os
import time
import google.generativeai as genai

# ==========================================
# 1. PAGE SETUP & PRINT STYLING
# ==========================================
st.set_page_config(layout="wide", page_title="HGDG & GEWE Assessment Tool")

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
st.write("Automated Assessment Tool integrated with GEWE Indicators")

# ==========================================
# 2. ENRICHED SECTOR GUIDELINES (GEWE INTEGRATED)
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
    
    api_key = st.text_input("Gemini API Key", type="password")
    
    selected_sector = st.selectbox(
        "Select HGDG Sector",
        options=list(sector_guidelines.keys())
    )
    
    project_title = st.text_input("Project Title")
    project_text = st.text_area("Paste Project Proposal Text Here", height=200)
    
    st.subheader("NotebookLM / Reference Uploader")
    uploaded_files = st.file_uploader(
        "Upload GEWE Volumes or Local Ordinances", 
        type=["pdf", "txt"], 
        accept_multiple_files=True,
        help="The AI will read these documents as its knowledge base to score the proposal."
    )
    
    reference_text = st.text_area("Paste Additional Short Context (Optional)", height=100)
    
    analyze_btn = st.button("Generate HGDG Checklist")

# ==========================================
# 4. AI LOGIC & REPORT GENERATION
# ==========================================
if analyze_btn:
    if not api_key or not project_text:
        st.error("Please enter your Gemini API Key and paste a project proposal.")
        st.stop()
        
    with st.spinner("Reading GEWE Indicators and analyzing proposal..."):
        try:
            # Connect to the stable Generative AI library
            genai.configure(api_key=api_key)
            active_sector_rules = sector_guidelines[selected_sector]
            
            # Process Uploaded Files
            gemini_uploaded_files = []
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_extension = ".pdf" if uploaded_file.name.endswith(".pdf") else ".txt"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                        temp_file.write(uploaded_file.read())
                        temp_path = temp_file.name
                    
                    st.toast(f"Uploading and processing {uploaded_file.name}...")
                    g_file = genai.upload_file(path=temp_path)
                    
                    # Wait for the AI to finish processing the PDF
                    while g_file.state.name == "PROCESSING":
                        time.sleep(2)
                        g_file = genai.get_file(g_file.name)
                        
                    gemini_uploaded_files.append(g_file)
                    os.remove(temp_path)
            
            # The Enriched GEWE System Prompt
            final_prompt = f"""
            You are an expert evaluator for the Department of the Interior and Local Government (DILG).
            Evaluate the provided local government project proposal using the Harmonized Gender and Development Guidelines (HGDG) Expanded Box 7.
            
            CRITICAL INSTRUCTION FOR GEWE INTEGRATION:
            You must actively cross-reference the proposal's monitoring and evaluation framework against the Gender Equality and Women's Empowerment (GEWE) Indicators.
            Specifically, check if the proposal contains measurable targets that align with the GEWE Impact, Outcome 1, and Outcome 2 indicators for the selected sector.
            If the user uploaded GEWE indicator documents, use them to validate the proposal's metrics.
            
            Sector Specific HGDG & GEWE Rules to Apply:
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
                  "result_comment": "Brief justification... Note if GEWE indicators were properly utilized."
                }}
              ],
              "total_score": 18.5,
              "interpretation": "Gender-responsive"
            }}
            """
            
            ai_contents = gemini_uploaded_files + [final_prompt]
            
            # Generate the response using Gemini 1.5 Flash
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                ai_contents,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
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