from typing import Dict, Any
from agents.base_agent import BaseAgent
import streamlit as st
from datetime import datetime
from config import GOOGLE_API_KEY

class UniversityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="University Agent",
            instructions="""
            You are a curriculum analysis expert.

            Analyze the following university course data and return insights in plain English using clear bullet points.

            Include:
            - Notable course names
            - Core skills taught
            - Degree programs that match well with the content
            - Suggested job roles based on the curriculum

            Format your response with section titles and clean bullet points. Do not return any JSON or raw code.
            """,
            api_key=GOOGLE_API_KEY
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        print("🎓 University Agent: Analyzing curriculum data...")

        try:
            input_text = messages[-1]["content"]
        except Exception as e:
            print(f"[UniversityAgent Error] Invalid input: {e}")
            return {
                "formatted_output": "❌ Could not process curriculum data due to input error.",
                "timestamp": str(datetime.now().date())
            }

        # Compose full prompt and call Gemini
        response_text = self._query_gemini(input_text)

        return {
            "formatted_output": response_text.strip(),
            "timestamp": str(datetime.now().date())
        }
