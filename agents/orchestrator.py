from typing import Dict, Any
from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .matcher_agent import MatcherAgent
from .screener_agent import ScreenerAgent
from .recommender_agent import RecommenderAgent


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            instructions="""Coordinate the recruitment workflow and delegate tasks to specialized agents.
            Ensure proper flow of information between extraction, analysis, matching, screening, and recommendation phases.
            Maintain context and aggregate results from each stage.""",
        )
        self._setup_agents()

    def _setup_agents(self):
        """Initialize all specialized agents"""
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.matcher = MatcherAgent()
        self.screener = ScreenerAgent()
        self.recommender = RecommenderAgent()

    async def run(self, messages: list) -> Dict[str, Any]:
        """Quick single-call LLM pass"""
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)

    async def process_application(self, resume_data: Dict[str, Any], university_context: str = "") -> Dict[str, Any]:
        """Main workflow orchestrator for processing job applications"""
        print("🎯 Orchestrator: Starting application process")

        workflow_context = {
            "resume_data": resume_data,
            "university_context": university_context,
            "status": "initiated",
            "current_stage": "extraction",
        }

        try:
            # ✅ 1. Extract resume
            extracted_data = await self.extractor.run(
                [{"role": "user", "content": str(resume_data)}]
            )
            workflow_context.update(
                {"extracted_data": extracted_data, "current_stage": "analysis"}
            )

            # ✅ 2. Analyze profile
            analysis_input = {
            "extracted_resume": extracted_data,
            "university_context": university_context,
            }
            analysis_results = await self.analyzer.run(
                [{"role": "user", "content": str(analysis_input)}]
            )
            workflow_context.update(
                {"analysis_results": analysis_results, "current_stage": "matching"}
            )

            # ✅ 3. Match jobs
            matcher_input = {
            "analysis": analysis_results,
            "university_context": university_context,
            }
            job_matches = await self.matcher.run(
                [{"role": "user", "content": str(matcher_input)}]
            )
            workflow_context.update(
                {"job_matches": job_matches, "current_stage": "screening"}
            )

            # ✅ 4. Screen candidate
            screening_results = await self.screener.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {"screening_results": screening_results, "current_stage": "recommendation"}
            )

            # ✅ 5. Final recommendation
            # === Final Recommendation ===
            recommender_input = {
                "context": workflow_context,
                "university_context": university_context,
            }
            final_recommendation = await self.recommender.run(
                [{"role": "user", "content": str(recommender_input)}]
            )
            workflow_context.update(
                {"final_recommendation": final_recommendation, "status": "completed"}
            )

            return workflow_context

        except Exception as e:
            workflow_context.update({"status": "failed", "error": str(e)})
            raise
