from groq import Groq

class GroqAPI:
    def __init__(self, api_url):
        self.client = Groq(
            api_url="",
        )

    def query(self, prompt_json):
        try:
            response = requests.post(self.api_url, json=prompt_json)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None

# Ejemplo de uso
api = GroqAPI("https://api.groq.com/query")
prompt = {
    "query": "your_groq_query_here",
    "variables": {
        "variable1": "value1",
        "variable2": "value2"
    }
}
result = api.query(prompt)
print(result)