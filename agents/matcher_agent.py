import json
import requests
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime

# Mapping skill keywords to recommended roles
RECOMMENDED_ROLE_MAP = {
    "Machine Learning": "Machine Learning Engineer",
    "Cloud Computing":"Cloud Data Scientist",
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
    """Maps skills to predefined job roles."""
    roles = set()
    for skill in skills:
        skill_lower = skill.lower()
        for key, role in RECOMMENDED_ROLE_MAP.items():
            if key in skill_lower:
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

        # Extract relevant fields
        skills = skills_analysis.get("technical_skills", [])
        experience_level = skills_analysis.get("experience_level", "Mid-level")
        education_field = analysis_results.get("education", {}).get("field", "")
        achievements = analysis_results.get("key_achievements", [])
        domains = analysis_results.get("domain_expertise", [])

        if not isinstance(skills, list):
            skills = []

        if experience_level not in ["Junior", "Mid-level", "Senior"]:
            experience_level = "Mid-level"

        # Compile keywords
        keywords = skills + domains + achievements + [education_field]
        keywords = [kw for kw in keywords if isinstance(kw, str)]
        print(f"🔍 Search keywords used: {keywords}")

        # Recommend roles based on all keywords
        recommended_roles_list = recommend_roles(keywords)
        print(f"💡 Recommended Roles: {recommended_roles_list}")

        # === Search for matched jobs ===
        matching_jobs = self.fetch_jobs_from_adzuna(skills, results_per_page=20)
        scored_jobs = []

        print("📝 Raw matching_jobs before scoring:")
        for job in matching_jobs:
            print(f"- {job.get('title')} | {job.get('description', '')[:100]}")
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
        if not scored_jobs:
            print("⚠️ No high match score jobs found. Falling back to top 5 Adzuna results.")
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


        # === Job listings for recommended roles ===
        role_job_map = {}
        for role in recommended_roles_list:
            print(f"🔍 Fetching jobs for role: {role}")
            role_jobs = self.fetch_jobs_from_adzuna([role], results_per_page=5)
            formatted_jobs = []
            for job in role_jobs:
                formatted_jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name", "N/A"),
                    "location": job.get("location", {}).get("display_name", "Unknown"),
                    "salary_range": f"{job.get('salary_min', 0)} - {job.get('salary_max', 0)}",
                    "url": job.get("redirect_url"),
                })
            role_job_map[role] = formatted_jobs

        # === Domain-based job listings ===
        domain_job_map = {}
        for domain in domains:
            jobs = self.fetch_jobs_for_domain(domain)
            domain_job_map[domain] = jobs

        # ✅ Return combined result
        return {
            "matched_jobs": scored_jobs[:10],
            "recommended_roles": role_job_map,
            "domain_expertise": domains,
            "domain_jobs": domain_job_map,  # 🔥 For domain button UI
            "match_timestamp": "2024-03-14",
            "number_of_matches": len(scored_jobs),
        }

    def fetch_jobs_from_adzuna(self, keywords: List[str], results_per_page: int = 10) -> List[Dict[str, Any]]:
        """Query Adzuna API for jobs using provided keywords."""
        search_term = " ".join(keywords)
        url = f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/1"
        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_app_key,
            "what": search_term,
            "results_per_page": results_per_page,
            "content-type": "application/json",
        }

        print(f"📤 Querying Adzuna for: {search_term}")
        print(f"📎 URL: {url}")
        print(f"📎 Params: {params}")

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"❌ Error calling Adzuna API: {e}")
            return []

    def fetch_jobs_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Wrapper to search jobs based on a domain value."""
        print(f"🌐 Searching Adzuna for domain: {domain}")
        return self.fetch_jobs_from_adzuna([domain], results_per_page=5)

    def _empty_result(self) -> Dict[str, Any]:
        """Helper to return empty fallback data."""
        return {
            "matched_jobs": [],
            "recommended_roles": {},
            "domain_expertise": [],
            "domain_jobs": {},
            "match_timestamp": "2025-5-7",
            "number_of_matches": 0,
        }
