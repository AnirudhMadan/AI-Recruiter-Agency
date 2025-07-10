import requests

def query_gemini_proxy(prompt: str, instructions: str = "") -> str:
    url = "https://proxy-server-m0x4.onrender.com/"  # replace with your deployed URL
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "instructions": instructions
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return res.json().get("result", "No result found.")
        else:
            return f"❌ Error {res.status_code}: {res.json()}"
    except Exception as e:
        return f"❌ Exception occurred: {str(e)}"
