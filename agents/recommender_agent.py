from typing import Dict, Any
from datetime import datetime
from .base_agent import BaseAgent
import streamlit as st
from config import GOOGLE_API_KEY

class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions="""Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results

            Your response should offer:
            - Clear next steps
            - Personalized insights based on the profile
            - Any missing elements (skills, qualifications)
            Return the recommendations in a well-structured paragraph.""",
            api_key=GOOGLE_API_KEY
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Generate final recommendations using Gemini"""
        print("💡 Recommender: Generating final recommendations")

        try:
            # Safely evaluate and stringify the input context
            workflow_context = eval(messages[-1]["content"])
            prompt = f"Candidate Data:\n{workflow_context}"
        except Exception as e:
            print(f"[Recommender Error] Invalid input: {e}")
            return {
                "final_recommendation": "Could not generate recommendation due to invalid input.",
                "recommendation_timestamp": str(datetime.now().date()),
                "confidence_level": "low"
            }

        # Query Gemini
        recommendation = self._query_gemini(prompt)

        return {
            "final_recommendation": recommendation.strip(),
            "recommendation_timestamp": str(datetime.now().date()),
            "confidence_level": "high"
        }
