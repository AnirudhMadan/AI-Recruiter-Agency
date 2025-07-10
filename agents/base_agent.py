from typing import Dict, Any
import json
import requests


class BaseAgent:
    def __init__(self, name: str, instructions: str, api_key: str):
        self.name = name
        self.instructions = instructions
        self.api_key = api_key

        # Gemini model you want to use (flash or pro)
        self.model = "gemini-pro"

    async def run(self, messages: list) -> Dict[str, Any]:
        """Default run method to be overridden by child classes"""
        raise NotImplementedError("Subclasses must implement run()")

    def _query_gemini(self, prompt: str) -> str:
        """Query Gemini model with the given prompt"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{self.instructions}\n\n{prompt}"}
                        ]
                    }
                ]
            }
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"Error: {response.status_code}\n{response.text}"

        except Exception as e:
            print(f"Error querying Gemini: {str(e)}")
            raise

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON from text, handling potential errors"""
        try:
            # Try to find JSON-like content between curly braces
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start : end + 1]
                return json.loads(json_str)
            return {"error": "No JSON content found"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON content"}
