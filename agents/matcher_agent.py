import json
import os
import requests
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime
from dotenv import load_dotenv
from config import GOOGLE_API_KEY

# Load environment
load_dotenv()

# Mapping skill keywords to recommended roles
RECOMMENDED_ROLE_MAP = {
    "Machine Learning": "Machine Learning Engineer",
    "Cloud Computing": "Cloud Data Scientist",
    "Statistics": "Data Scientist",
    "Sql": "Data Analyst",
    "Tableau": "BI Analyst",
    "Predictive Modeling": "AI Specialist",
    "React": "Frontend Developer",
    "Javascript": "Web Developer",
    "Python": "Python Developer",
    "Cloud": "Cloud Engineer",
    "Kubernetes": "DevOps Engineer",
    "Aws": "Cloud Engineer",
}


def recommend_roles(skills: List[str]) -> List[str]:
    roles = set()
    for skill in skills:
        skill_lower = skill.lower()
        for key, role in RECOMMENDED_ROLE_MAP.items():
            if key.lower() in skill_lower:
                roles.add(role)
    return list(roles)[:5]


class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions="""Match candidate profiles with job positions.
            Consider: skills match, experience level, location preferences.
            Provide detailed reasoning and compatibility scores.
            Return matches in JSON format with title, match_score, and location fields.""",
            api_key=GOOGLE_API_KEY # ✅ Gemini API key
        )
        self.adzuna_app_id = ""  # Fill in your Adzuna app_id
        self.adzuna_app_key = ""  # Fill in your Adzuna app_key
        self.country = "in"

    async def run(self, messages: list) -> Dict[str, Any]:
        print("🎯 Matcher: Finding suitable job matches")

        try:
            content = messages[-1].get("content", "{}").replace("'", '"')
            analysis_results = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing analysis results: {e}")
            return self._empty_result()

        skills_analysis = analysis_results.get("skills_analysis", {})
        if not skills_analysis:
            print("⚠️ No skills analysis provided.")
            return self._empty_result()

        skills = skills_analysis.get("technical_skills", [])
        experience_level = skills_analysis.get("experience_level", "Mid-level")
        education_field = analysis_results.get("education", {}).get("field", "")
        achievements = analysis_results.get("key_achievements", [])
        domains = analysis_results.get("domain_expertise", [])

        if not isinstance(skills, list):
            skills = []

        if experience_level not in ["Junior", "Mid-level", "Senior"]:
            experience_level = "Mid-level"

        keywords = skills + domains + achievements + [education_field]
        keywords = [kw for kw in keywords if isinstance(kw, str)]
        print(f"🔍 Search keywords used: {keywords}")

        # Use Gemini to recommend roles (instead of local rule-based mapping)
        gemini_prompt = f"""
        Based on the following candidate keywords, experience level, and domains, recommend 3-5 ideal job roles.

        Keywords: {keywords}
        Experience Level: {experience_level}
        Domains: {domains}

        Return JSON like:
        {{
            "recommended_roles": ["Job Role 1", "Job Role 2", ...]
        }}
        """
        gemini_response = self._query_gemini(gemini_prompt)
        parsed_roles = self._parse_json_safely(gemini_response)

        recommended_roles_list = parsed_roles.get("recommended_roles", recommend_roles(keywords))
        print(f"💡 Recommended Roles: {recommended_roles_list}")

        matching_jobs = self.fetch_jobs_from_adzuna(skills, results_per_page=20)
        scored_jobs = []

        for job in matching_jobs:
            description_text = (job.get("title", "") + " " + job.get("description", "")).lower()
            required_skills = set(map(str.lower, skills))
            overlap = sum(1 for skill in required_skills if skill in description_text)
            match_score = int((overlap / len(required_skills)) * 100) if required_skills else 0

            scored_jobs.append({
                "title": job.get("title"),
                "company": job.get("company", {}).get("display_name", "N/A"),
                "location": job.get("location", {}).get("display_name", "Unknown"),
                "salary_range": f"{job.get('salary_min', 0)} - {job.get('salary_max', 0)}",
                "match_score": f"{match_score}%",
                "url": job.get("redirect_url"),
            })

        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)

        # Fallback jobs if nothing scored
        if not scored_jobs:
            fallback_jobs = self.fetch_jobs_from_adzuna(skills, results_per_page=5)
            for job in fallback_jobs:
                scored_jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name", "N/A"),
                    "location": job.get("location", {}).get("display_name", "Unknown"),
                    "salary_range": f"{job.get('salary_min', 0)} - {job.get('salary_max', 0)}",
                    "match_score": "Fallback",
                    "url": job.get("redirect_url"),
                })

        # Role-wise recommendations
        role_job_map = {}
        for role in recommended_roles_list:
            print(f"🔍 Fetching jobs for role: {role}")
            role_jobs = self.fetch_jobs_from_adzuna([role], results_per_page=5)
            role_job_map[role] = [
                {
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name", "N/A"),
                    "location": job.get("location", {}).get("display_name", "Unknown"),
                    "salary_range": f"{job.get('salary_min', 0)} - {job.get('salary_max', 0)}",
                    "url": job.get("redirect_url"),
                }
                for job in role_jobs
            ]

        domain_job_map = {}
        for domain in domains:
            jobs = self.fetch_jobs_for_domain(domain)
            domain_job_map[domain] = jobs

        return {
            "matched_jobs": scored_jobs[:10],
            "recommended_roles": role_job_map,
            "domain_expertise": domains,
            "domain_jobs": domain_job_map,
            "match_timestamp": str(datetime.now().date()),
            "number_of_matches": len(scored_jobs),
        }

    def fetch_jobs_from_adzuna(self, keywords: List[str], results_per_page: int = 10) -> List[Dict[str, Any]]:
        search_term = " ".join(keywords)
        url = f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/1"
        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_app_key,
            "what": search_term,
            "results_per_page": results_per_page,
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"❌ Error calling Adzuna API: {e}")
            return []

    def fetch_jobs_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        return self.fetch_jobs_from_adzuna([domain], results_per_page=5)

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "matched_jobs": [],
            "recommended_roles": {},
            "domain_expertise": [],
            "domain_jobs": {},
            "match_timestamp": str(datetime.now().date()),
            "number_of_matches": 0,
        }
