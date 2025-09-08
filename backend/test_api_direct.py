import requests
import json

# Test direct API call
url = "http://localhost:8000/api/analyze"
payload = {
    "query": "What are the top 5 customers by total amount?"
}

response = requests.post(url, json=payload, stream=True)

print("Response headers:", dict(response.headers))
print("\n" + "="*50 + "\n")

# Parse SSE stream
for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            try:
                data = json.loads(line[6:])
                if 'visualizations' in data:
                    viz_count = len(data['visualizations'])
                    print(f"[FOUND] visualizations array with {viz_count} charts")
                    for i, viz in enumerate(data['visualizations']):
                        print(f"  Chart {i+1}: {viz.get('type')} - {viz.get('title')}")
                elif 'visualization' in data:
                    print(f"[FOUND] single visualization: {data['visualization'].get('type')}")
                elif 'step' in data:
                    print(f"[STEP] {data['step']}: {data.get('message', '')}")
                else:
                    print(f"[DATA] Keys: {list(data.keys())}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                print(f"[RAW] {line}")