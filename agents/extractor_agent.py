from typing import Dict, Any
from pdfminer.high_level import extract_text  # pip install pdfminer.six
from .base_agent import BaseAgent


class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Extractor",
            instructions="""Extract and structure information from resumes.
            Focus on: personal info, work experience, education, skills, and certifications.
            Provide output in a clear, structured format as JSON only."""
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Process the resume and extract information"""
        print("📄 Extractor: Processing resume")

        resume_data = eval(messages[-1]["content"])

        # Extract raw text from PDF file path or fallback
        if resume_data.get("file_path"):
            raw_text = extract_text(resume_data["file_path"])
        else:
            raw_text = resume_data.get("text", "")

        # 🧠 Build structured prompt for Gemini
        prompt = f"""
        You are a resume parser. Extract the following fields from the text:

        - Full Name
        - Contact Info (email and phone)
        - Education (degree, field, institution, dates)
        - Work Experience (title, company, dates, responsibilities)
        - Technical and Soft Skills
        - Certifications (if any)

        Text to analyze:
        {raw_text}

        Return the result as a JSON object.
        """

        response = self._query_gemini(prompt)
        structured = self._parse_json_safely(response)

        return {
            "raw_text": raw_text,
            "structured_data": structured,
            "extraction_status": "completed"
        }
