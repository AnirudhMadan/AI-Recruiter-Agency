# integrated_app.py

import streamlit as st
import asyncio
import os
import requests
from pathlib import Path
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent
from utils.logger import setup_logger
from utils.exceptions import ResumeProcessingError
from university_app import render_university_interface
from domain_job_search_demo import run_domain_job_search  # 👈 new import

# =============================
# CONFIGURE STREAMLIT PAGE
# =============================
st.set_page_config(
    page_title="AI Recruiter Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================
# SETUP LOGGER
# =============================
logger = setup_logger()

# =============================
# CUSTOM CSS
# =============================
st.markdown(
    """
    <style>
        .stProgress .st-bo {
            background-color: #00a0dc;
        }
        .success-text {
            color: #00c853;
        }
        .warning-text {
            color: #ffd700;
        }
        .error-text {
            color: #ff5252;
        }
        .st-emotion-cache-1v0mbdj.e115fcil1 {
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================
# MAIN NAVIGATION FUNCTION
# =============================
def main():
    with st.sidebar:
        st.image("https://img.icons8.com/resume", width=50)
        st.title("AI Recruiter Agency")
        selected = option_menu(
            menu_title="Navigation",
            options=["Upload Resume", "University Curriculum", "Job Search", "About","Research Papers"],
            icons=["cloud-upload", "book", "search", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Upload Resume":
        st.header("📄 Resume Analysis")
        st.write("Upload a resume to get AI-powered insights and job matches.")

        # Fetch university context if any
        university_context = ""
        if "university_result" in st.session_state:
            university_context = str(st.session_state["university_result"])
            st.info("📘 University curriculum data will be included in this analysis.")
        else:
            st.warning("📘 No university curriculum uploaded. You can still proceed.")

        uploaded_file = st.file_uploader("Choose a PDF resume file", type=["pdf"], help="Upload a PDF resume to analyze")

        if uploaded_file:
            try:
                with st.spinner("Saving uploaded file..."):
                    file_path = save_uploaded_file(uploaded_file)

                st.info("Resume uploaded successfully! Processing...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.text("Analyzing resume...")
                    progress_bar.progress(25)

                    result = asyncio.run(process_resume(file_path, university_context))

                    if result["status"] == "completed":
                        progress_bar.progress(100)
                        status_text.text("Analysis complete!")

                        tab1, tab3, tab4 = st.tabs(["📊 Analysis", "🎯 Screening", "💡 Recommendation"])

                        with tab1:
                            st.subheader("Skills Analysis")
                            st.write(result["analysis_results"]["skills_analysis"])
                            st.metric("Confidence Score", f"{result['analysis_results']['confidence_score']:.0%}")

                        with tab3:
                            st.subheader("Screening Results")
                            st.metric("Screening Score", f"{result['screening_results']['screening_score']}%")
                            st.write(result["screening_results"]["screening_report"])

                        with tab4:
                            st.subheader("Final Recommendation")
                            st.info(result["final_recommendation"]["final_recommendation"], icon="💡")

                        output_dir = Path("results")
                        output_dir.mkdir(exist_ok=True)
                        output_file = output_dir / f"analysis_output.txt"
                        with open(output_file, "w") as f:
                            f.write(str(result))
                        st.success(f"Results saved to: {output_file}")

                    else:
                        st.error(f"Process failed at stage: {result['current_stage']}\nError: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    st.error(f"Error processing resume: {str(e)}")
                    logger.error(f"Processing error: {str(e)}", exc_info=True)

                finally:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error removing temporary file: {str(e)}")

            except Exception as e:
                st.error(f"Error handling file upload: {str(e)}")
                logger.error(f"Upload error: {str(e)}", exc_info=True)

    elif selected == "Job Search":
        run_domain_job_search()

    elif selected == "University Curriculum":
        render_university_interface()

    elif selected == "About":
        st.header("About AI Recruiter Agency")
        st.write(
            """
        Welcome to AI Recruiter Agency, a cutting-edge recruitment analysis system powered by:

        - **Ollama (llama3.2)**: Advanced language model for natural language processing
        - **Swarm Framework**: Coordinated AI agents for specialized tasks
        - **Streamlit**: Modern web interface for easy interaction

        Our system uses specialized AI agents to:
        1. 📄 Extract information from resumes
        2. 🔍 Analyze candidate profiles
        3. 🎯 Match with suitable positions
        4. 👥 Screen candidates
        5. 💡 Provide detailed recommendations
        """
        )

    elif selected == "Research Papers":
        st.header("📚 Research Papers Referenced")
        st.write("This project is inspired by recent research in multi-agent systems, LLM orchestration, and AI-powered recruitment tools.")

        papers = [
            {
                "title": "LLM‑Powered Swarms: A New Frontier or a Conceptual Stretch? (2025)",
                "desc": "Critically examines the use of large language models (LLMs) as agents within swarm systems.",
                "url": "https://arxiv.org/abs/2506.14496",
                "points": [
                    "✅ This paper explores how LLM agents can simulate swarm behaviors and evaluates trade-offs in decentralization, coordination, and performance.",
                    "🔗 This directly relates to my project where I use modular LLM agents like Extractor and Matcher, coordinated by an OrchestratorAgent, to simulate swarm-like task delegation."
                ]
            },
            {
                "title": "GPTSwarm: Language Agents as Optimizable Graphs (2024)",
                "desc": "Proposes a formal graph-based swarm architecture using LLMs as nodes and task-routing edges.",
                "url": "https://arxiv.org/html/2402.16823",
                "points": [
                    "✅ This paper introduces learnable communication paths between LLM agents for better multi-agent coordination.",
                    "🔗 My project could evolve by adopting a similar graph-based approach to route tasks between agents dynamically based on context."
                ]
            },
            {
                "title": "A Deep Learning Approach for Resume Parsing (2021)",
                "desc": "Presents a neural network-based method for extracting structured information from resumes.",
                "url": "https://rjpn.org/ijcspub/papers/IJCSP24B1154.pdf",
                "points": [
                    "✅ The paper describes deep learning methods for extracting data from resumes using NER techniques.",
                    "🔗 I use a similar method in my ExtractorAgent to pull out skills, education, and experience from PDF resumes."
                ]
            },
            {
                "title": "Learning Effective Representations for Person‑Job Fit (2020)",
                "desc": "Explores neural embedding techniques for assessing candidate-job compatibility.",
                "url": "https://arxiv.org/abs/2006.07017",
                "points": [
                    "✅ This research shows how to use embeddings and attention mechanisms to measure resume-job fit.",
                    "🔗 I use the same idea in my MatcherAgent to assess how well a candidate fits a specific job role."
                ]
            },
            {
                "title": "Fairness in AI‑Driven Recruitment: Challenges, Metrics, Methods (2024)",
                "desc": "Surveys fairness concerns in AI recruitment systems and proposes metrics for bias mitigation.",
                "url": "https://arxiv.org/abs/2405.19699",
                "points": [
                    "✅ It highlights algorithmic bias in hiring systems and explores ways to detect and reduce it.",
                    "🔗 This is important for my ScreenerAgent and recommendation system to ensure fair and unbiased decision-making."
                ]
            }
        ]

        for paper in papers:
            st.markdown(f"### [{paper['title']}]({paper['url']})")
            st.markdown(f"*{paper['desc']}*")
            for point in paper["points"]:
                st.markdown(f"- {point}")
            st.markdown("---")


# =============================
# UTILITY FUNCTIONS
# =============================
def save_uploaded_file(uploaded_file) -> str:
    try:
        save_dir = Path("uploads")
        save_dir.mkdir(exist_ok=True)
        file_path = save_dir / f"resume_uploaded_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(file_path)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        raise

def fetch_adzuna_jobs(query, location="India", results_per_page=10):
    from utils.constants import APP_ID, APP_KEY
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
        st.error(f"Error fetching jobs from Adzuna: {e}")
        return []

async def process_resume(file_path: str, university_context: str = "") -> dict:
    try:
        orchestrator = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "submission_timestamp": "2025-7-5",  # Static fallback
        }
        return await orchestrator.process_application(resume_data, university_context)
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise

if __name__ == "__main__":
    main()
