from typing import Dict, Any
from .base_agent import BaseAgent
from datetime import datetime


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Education level
            4. Experience level (Junior/Mid-level/Senior)
            5. Key achievements
            6. Domain expertise

            Format the output as structured data."""
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        print("🔍 Analyzer: Analyzing candidate profile")

        try:
            payload = eval(messages[-1]["content"])
            resume_data = payload.get("extracted_resume", {})
            university_context = payload.get("university_context", "")
            structured = resume_data.get("structured_data", {})
        except Exception as e:
            print(f"[Analyzer Error] Failed to parse input: {e}")
            structured = {}

        analysis_prompt = f"""
        Analyze the candidate based on the resume data below and optionally include insights from university curriculum context.

        Return JSON in this structure:
        {{
            "technical_skills": ["skill1", "skill2"],
            "years_of_experience": number,
            "education": {{
                "level": "Bachelors/Masters/PhD",
                "field": "field of study"
            }},
            "experience_level": "Junior/Mid-level/Senior",
            "key_achievements": ["achievement1", "achievement2"],
            "domain_expertise": ["domain1", "domain2"]
        }}

        Resume structured data:
        {structured}

        University context (optional):
        {university_context}

        Return ONLY the JSON object.
        """

        response = self._query_gemini(analysis_prompt)
        parsed = self._parse_json_safely(response)

        if "error" in parsed:
            parsed = {
                "technical_skills": [],
                "years_of_experience": 0,
                "education": {"level": "Unknown", "field": "Unknown"},
                "experience_level": "Junior",
                "key_achievements": [],
                "domain_expertise": [],
            }

        return {
            "skills_analysis": parsed,
            "analysis_timestamp": str(datetime.now().date()),
            "domain_expertise": parsed.get("domain_expertise", []),
            "confidence_score": 0.85 if "error" not in parsed else 0.5,
        }
