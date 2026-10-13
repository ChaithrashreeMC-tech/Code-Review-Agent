# agents/graphs/analyst/nodes/analyze.py
from openai import OpenAI

def analyze_data_node(state: dict) -> dict:
    # VIOLATION: Constructing vendor client directly inside node with hardcoded_provider
    client = OpenAI(api_key="sk-test-secret-key-12345")
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": state["query"]}]
    )
    return {"analysis": res.choices[0].message.content}

