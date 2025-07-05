from typing import Dict, Any
from agents.base_agent import BaseAgent

class UniversityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="University Agent",
            instructions="""
            Analyze university course data and extract:
            - Course names
            - Skills taught
            - Degree program compatibility
            - Suitable job roles

            Output only structured JSON format.
            """,
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        print("🎓 University Agent: Analyzing curriculum data...")
        input_text = messages[-1]["content"]
        result = self._query_ollama(input_text)
        return self._parse_json_safely(result)
