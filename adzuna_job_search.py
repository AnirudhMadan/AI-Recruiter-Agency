import requests

# Replace with your Adzuna credentials
APP_ID = 'ca7aba49'
APP_KEY = 'da0c323b9c0f3c974ec92c41a9db4f7b'

# Job search parameters
country = 'in'  # 'in' = India
search_term = 'data scientist'
location = 'Bangalore'
results_per_page = 5

# Construct the API endpoint
url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

params = {
    'app_id': APP_ID,
    'app_key': APP_KEY,
    'what': search_term,
    'where': location,
    'results_per_page': results_per_page,
    'content-type': 'application/json'
}

response = requests.get(url, params=params)

if response.status_code == 200:
    jobs = response.json().get("results", [])
    print(f"\nFound {len(jobs)} job listings for '{search_term}' in {location}:\n")

    for i, job in enumerate(jobs, 1):
        print(f"🔹 Job {i}")
        print(f"Title     : {job.get('title')}")
        print(f"Company   : {job.get('company', {}).get('display_name')}")
        print(f"Location  : {job.get('location', {}).get('display_name')}")
        print(f"Salary    : {job.get('salary_min')} - {job.get('salary_max')}")
        print(f"URL       : {job.get('redirect_url')}")
        print("-" * 50)

else:
    print("❌ Failed to fetch job data:", response.status_code, response.text)
