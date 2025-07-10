from typing import Dict, Any
from .base_agent import BaseAgent
import os
from dotenv import load_dotenv
from config import GOOGLE_API_KEY

# Load environment variables
load_dotenv()

class ProfileEnhancerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Profile Enhancer",
            instructions="Enhance the candidate's resume into a professional summary paragraph using the extracted structured info.",
            api_key=GOOGLE_API_KEY
        )

    def enhance(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        experience_items = extracted_info.get("experience", [])
        total_experience_years = sum(item.get("years", 0) for item in experience_items)

        name = extracted_info.get("name", "The candidate")
        skills = ", ".join(extracted_info.get("skills", []))
        roles = ", ".join(set(item.get("role", "") for item in experience_items if item.get("role")))

        structured_summary_prompt = f"""
        Candidate Name: {name}
        Total Experience: {total_experience_years} years
        Roles: {roles}
        Skills: {skills}

        Write a 2-3 sentence professional summary highlighting their strengths, experience, and skills.
        """

        summary = self._query_gemini(structured_summary_prompt)

        return {
            **extracted_info,
            "summary": summary.strip()
        }
