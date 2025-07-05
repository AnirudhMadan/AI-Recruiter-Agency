import streamlit as st
import asyncio
from datetime import datetime
from pathlib import Path
import os
from agents.university_agent import UniversityAgent
from utils.logger import setup_logger

# Setup
logger = setup_logger()
# def format_result_as_markdown(result: dict) -> str:
#     """Convert result dict to markdown text"""
#     if not isinstance(result, dict):
#         return str(result)

#     markdown_output = ""
#     for key, value in result.items():
#         markdown_output += f"### {key}\n"
#         if isinstance(value, list):
#             for item in value:
#                 markdown_output += f"- {item}\n"
#         elif isinstance(value, dict):
#             for sub_key, sub_value in value.items():
#                 markdown_output += f"- **{sub_key}**: {sub_value}\n"
#         else:
#             markdown_output += f"{value}\n"
#         markdown_output += "\n"
#     return markdown_output
def format_result_as_markdown(result: dict, level: int = 3) -> str:
    """Convert any dict or list result to safe readable markdown"""
    markdown = ""

    if isinstance(result, dict):
        for key, value in result.items():
            markdown += f"{'#' * level} {key}\n\n"
            markdown += format_result_as_markdown(value, level + 1)
    elif isinstance(result, list):
        for item in result:
            markdown += f"- {format_result_as_markdown(item, level)}"
        markdown += "\n"
    else:
        markdown += f"{str(result)}\n\n"

    return markdown


def save_temp_file(uploaded_file) -> str:
    """Save uploaded file to a temporary path and return filepath"""
    try:
        temp_dir = Path("uploads")
        temp_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_path = temp_dir / f"university_{timestamp}_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        return str(temp_path)
    except Exception as e:
        st.error(f"Error saving uploaded file: {e}")
        logger.error("Upload save error", exc_info=True)
        return ""


async def process_university_text(text: str) -> dict:
    """Send university content to AI agent and return structured response"""
    try:
        agent = UniversityAgent()
        result = await agent.run([{"role": "user", "content": text}])
        return result
    except Exception as e:
        st.error(f"Processing Error: {e}")
        logger.error("University Agent Processing Error", exc_info=True)
        return {"error": str(e)}


def render_university_interface():
    st.title("📚 University Curriculum Analyzer")
    st.write("Upload or paste university curriculum or placement brochure to analyze its job readiness.")
    st.info("ℹ️ This data will be **optionally** used during resume analysis (if available).")

    input_option = st.radio("Choose input method:", ["Paste Text", "Upload File (.txt/.pdf)"])
    university_text = ""

    if input_option == "Paste Text":
        university_text = st.text_area("Paste Curriculum Content", height=300)
        if university_text and st.button("Analyze Curriculum"):
            with st.spinner("Analyzing curriculum..."):
                result = asyncio.run(process_university_text(university_text))
                st.subheader("📘 AI Analysis Result")
                try:
                    st.markdown(format_result_as_markdown(result))
                except Exception as e:
                    st.error("⚠️ Error displaying markdown. Showing raw JSON instead.")
                    st.json(result)

                st.session_state.university_result = result
                st.success("✅ Curriculum analysis saved for resume processing.")

    else:
        uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
        if uploaded_file and st.button("Analyze Curriculum"):
            ext = uploaded_file.name.split(".")[-1]
            try:
                if ext == "txt":
                    university_text = uploaded_file.read().decode("utf-8")
                elif ext == "pdf":
                    from pdfminer.high_level import extract_text
                    temp_path = save_temp_file(uploaded_file)
                    university_text = extract_text(temp_path)
                    os.remove(temp_path)
                else:
                    st.error("Unsupported file format.")
                    return

                with st.spinner("Analyzing uploaded curriculum..."):
                    result = asyncio.run(process_university_text(university_text))
                    st.subheader("📘 AI Analysis Result")
                    st.json(result)
                    st.session_state.university_result = result
                    st.success("✅ Curriculum analysis saved for resume processing.")

            except Exception as e:
                st.error(f"Failed to process file: {e}")
                logger.error("File processing error", exc_info=True)
