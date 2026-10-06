# ==========================================
# 3. USER INPUT (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("Project Input")
    
    # The app now invisibly pulls the API key from Streamlit's hidden settings
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("System Error: API Key is missing from Streamlit Cloud Secrets. Please add it in the App Settings.")
        st.stop()
    
    selected_sector = st.selectbox(
        "Select HGDG Sector",
        options=list(sector_guidelines.keys())
    )
    
    project_title = st.text_input("Project Title", placeholder="e.g., San Clemente Rural Water Supply")
    project_text = st.text_area("Paste Project Proposal Text Here", height=300)
    
    st.subheader("Additional Context")
    reference_text = st.text_area("Paste Additional Local Memos (Optional)", height=100)
    
    analyze_btn = st.button("Generate Personalized HGDG Checklist")
