import streamlit as st
import asyncio
import json
import requests
from io import BytesIO
from pdfminer.high_level import extract_text

from agents.analyzer_agent import AnalyzerAgent
from agents.matcher_agent import MatcherAgent

# ================================
# CONFIGURE ADZUNA API CREDENTIALS
# ================================
APP_ID = "ca7aba49"
APP_KEY = "da0c323b9c0f3c974ec92c41a9db4f7b"
COUNTRY = "in"

# =========================
# HELPER: Extract text from PDF
# =========================
def extract_text_from_pdf(file: BytesIO) -> str:
    try:
        return extract_text(file).strip()
    except Exception as e:
        st.error(f"❌ Failed to extract text from PDF: {e}")
        return ""

# =========================
# HELPER: Fetch jobs from Adzuna
# =========================
def fetch_jobs_from_adzuna(keywords, location="India", results_per_page=5):
    search_term = " ".join(keywords)
    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": search_term,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        st.error(f"❌ Failed to fetch jobs from Adzuna: {e}")
        return []

# =========================
# MAIN ENTRY FUNCTION
# =========================
def run_domain_job_search():
    #st.set_page_config(page_title="📄 Domain Job Search Demo", layout="wide")
    st.title("📄 Upload Resume PDF + Get Domain & Skill Based Job Matches")

    uploaded_file = st.file_uploader("Upload your resume (PDF only):", type=["pdf"])

    if uploaded_file:
        with st.spinner("🔍 Extracting text from PDF..."):
            raw_text = extract_text_from_pdf(uploaded_file)

        if raw_text:
            st.success("✅ Text extracted from resume!")
            st.text_area("🔍 Resume Text Preview", raw_text[:1000] + "...", height=200)

            # === Run Analyzer only ONCE
            if "analysis_result" not in st.session_state:
                with st.spinner("🧠 Analyzing resume..."):
                    analyzer = AnalyzerAgent()
                    messages = [{"role": "user", "content": json.dumps({"extracted_resume": {"structured_data": raw_text}})}]
                    st.session_state.analysis_result = asyncio.run(analyzer.run(messages))

            st.subheader("📊 Resume Insights")
            st.json(st.session_state.analysis_result)

            # === Extract once and reuse
            if "skills" not in st.session_state:
                st.session_state.skills = st.session_state.analysis_result.get("skills_analysis", {}).get("technical_skills", [])

            if "domains" not in st.session_state:
                st.session_state.domains = st.session_state.analysis_result.get("skills_analysis", {}).get("domain_expertise", [])

            # === Dropdown Search
            st.subheader("🎛️ Find Jobs by Domain + Skills")
            with st.expander("🔎 Advanced Search Filters", expanded=False):
                selected_domains = st.multiselect("🌐 Select Domain Expertise", options=st.session_state.domains, key="domain_select")
                selected_skills = st.multiselect("🧠 Select Technical Skills", options=st.session_state.skills, key="skill_select")

                if st.button("🔍 Search Combined Domains + Skills", key="combined_search"):
                    combined_keywords = selected_domains + selected_skills
                    if not combined_keywords:
                        st.warning("Please select at least one skill or domain.")
                    else:
                        st.session_state["combined_keywords"] = combined_keywords
                        st.session_state["combined_jobs"] = fetch_jobs_from_adzuna(combined_keywords)

            # === Render results if available
            if "combined_keywords" in st.session_state and "combined_jobs" in st.session_state:
                st.subheader(f"🔍 Results for: {', '.join(st.session_state['combined_keywords'])}")
                jobs = st.session_state["combined_jobs"]
                if not jobs:
                    st.warning("No job postings found for the selected criteria.")
                else:
                    for job in jobs:
                        st.markdown(f"### {job.get('title', 'No Title')}")
                        st.markdown(f"**Company:** {job.get('company', {}).get('display_name', 'Unknown')}")
                        st.markdown(f"📍 Location: {job.get('location', {}).get('display_name', 'N/A')}")
                        st.markdown(f"💰 Salary: ₹{int(job.get('salary_min', 0)):,} - ₹{int(job.get('salary_max', 0)):,}")
                        st.markdown(f"[🔗 View Job Posting]({job.get('redirect_url', '#')})", unsafe_allow_html=True)
                        st.divider()

            # === Manual Search
            st.subheader("🔎 Manual Adzuna Job Search")
            search_term = st.text_input("Enter job keyword (e.g., Data Analyst)", "Machine Learning")
            location_input = st.text_input("Location", "India")
            if st.button("Search Adzuna"):
                with st.spinner("Fetching jobs from Adzuna..."):
                    jobs = fetch_jobs_from_adzuna([search_term], location=location_input)
                    if not jobs:
                        st.warning("No results found.")
                    else:
                        for job in jobs:
                            st.markdown(f"### {job.get('title', 'No Title')}")
                            st.markdown(f"**Company:** {job.get('company', {}).get('display_name', 'Unknown')}")
                            st.markdown(f"📍 Location: {job.get('location', {}).get('display_name', 'N/A')}")
                            st.markdown(f"💰 Salary: ₹{int(job.get('salary_min', 0)):,} - ₹{int(job.get('salary_max', 0)):,}")
                            st.markdown(f"[🔗 View Job Posting]({job.get('redirect_url', '#')})", unsafe_allow_html=True)
                            st.markdown(f"📝 Description: {job.get('description', '')[:300]}...")
                            st.divider()
