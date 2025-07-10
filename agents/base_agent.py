from typing import Dict, Any
import json
from utils.gemini_client import query_gemini_proxy  # ✅ Add this import


class BaseAgent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions

    async def run(self, messages: list) -> Dict[str, Any]:
        """Default run method to be overridden by child classes"""
        raise NotImplementedError("Subclasses must implement run()")

    def _query_gemini(self, prompt: str) -> str:
        """Use Gemini proxy to generate response from prompt"""
        try:
            return query_gemini_proxy(prompt=prompt, instructions=self.instructions)
        except Exception as e:
            print(f"Error querying Gemini Proxy: {str(e)}")
            return f"Proxy Error: {str(e)}"

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON from text, handling potential errors"""
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start : end + 1]
                return json.loads(json_str)
            return {"error": "No JSON content found"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON content"}
