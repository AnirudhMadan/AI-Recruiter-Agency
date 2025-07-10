from typing import Dict, Any
from datetime import datetime
from .base_agent import BaseAgent


class ScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Screener",
            instructions="""Screen candidates based on the following:
            - Qualification alignment
            - Experience relevance
            - Skill match percentage
            - Cultural fit indicators
            - Red flags or concerns

            Provide a comprehensive but concise screening report in plain text.
            Mention if anything is missing or uncertain in the candidate's profile."""
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Screen the candidate using Gemini"""
        print("👥 Screener: Conducting initial screening")

        try:
            workflow_context = eval(messages[-1]["content"])
            prompt = f"Candidate Profile Data:\n{workflow_context}"
        except Exception as e:
            print(f"[Screener Error] Invalid input: {e}")
            return {
                "screening_report": "Could not screen candidate due to input error.",
                "screening_timestamp": str(datetime.now().date()),
                "screening_score": 0
            }

        # Use Gemini via proxy
        screening_results = self._query_gemini(prompt)

        return {
            "screening_report": screening_results.strip(),
            "screening_timestamp": str(datetime.now().date()),
            "screening_score": 85  # Optional: compute dynamically later
        }
