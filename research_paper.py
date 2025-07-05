import streamlit as st

# ================================
# Streamlit Page Setup
# ================================
st.set_page_config(page_title="📚 Research Papers", layout="wide")

st.title("📖 Research Papers Referenced")
st.write("This project is inspired by recent research in multi-agent systems, LLM orchestration, and AI-powered recruitment tools.")

# ================================
# List of Research Papers
# ================================
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

# ================================
# Display Papers
# ================================
for paper in papers:
    st.markdown(f"### [{paper['title']}]({paper['url']})")
    st.markdown(f"*{paper['desc']}*")
    for point in paper["points"]:
        st.markdown(f"- {point}")
    st.markdown("---")
