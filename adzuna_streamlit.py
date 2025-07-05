import streamlit as st
import requests

# Adzuna API credentials (register at https://developer.adzuna.com/)
APP_ID = "ca7aba49"
APP_KEY = "da0c323b9c0f3c974ec92c41a9db4f7b"

def fetch_adzuna_jobs(query, location="India", results_per_page=10):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": query,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        st.error(f"Failed to fetch job listings: {e}")
        return []

# ------------------------
# Streamlit UI
# ------------------------

st.title("💼 Job Listings from Adzuna")

search_term = st.text_input("Search for jobs (e.g. Data Scientist)", "Machine Learning Engineer")
location = st.text_input("Location", "Bangalore")

if st.button("Search"):
    with st.spinner("Fetching jobs from Adzuna..."):
        jobs = fetch_adzuna_jobs(search_term, location)

    if not jobs:
        st.warning("No job listings found.")
    else:
        st.success(f"Showing top {len(jobs)} jobs")

        for job in jobs:
            st.subheader(job.get("title", "No Title"))
            company = job.get("company", {}).get("display_name", "Unknown")
            location = job.get("location", {}).get("display_name", "Not specified")
            salary_min = job.get("salary_min", 0)
            salary_max = job.get("salary_max", 0)
            redirect_url = job.get("redirect_url", "#")

            col1, col2 = st.columns([2, 1])
            col1.markdown(f"**Company**: {company}")
            col1.markdown(f"**Location**: {location}")
            col2.markdown(f"**Salary**: ₹{int(salary_min):,} - ₹{int(salary_max):,}")

            st.markdown(f"[🔗 View Job Posting]({redirect_url})", unsafe_allow_html=True)
            st.markdown(f"**Description:** {job.get('description', '')[:300]}...")

            st.divider()
