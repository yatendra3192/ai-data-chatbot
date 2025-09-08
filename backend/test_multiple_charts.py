import pandas as pd
import json
from intelligent_query_processor import process_data_query

# Load the CSV data
csv_path = r"C:\Users\User\Documents\DVwithCC\salesorder.csv"
data = pd.read_csv(csv_path, nrows=1000)  # Load fewer rows for testing

# Test query
query = "What are the top 5 customers by revenue?"

# Process the query
result = process_data_query(query, data)

# Print the result
print("Query:", query)
print("\nAnswer:", result.get('answer', 'No answer'))

if 'visualizations' in result:
    print(f"\nNumber of visualizations: {len(result['visualizations'])}")
    for i, viz in enumerate(result['visualizations']):
        print(f"\nVisualization {i+1}:")
        print(f"  Type: {viz.get('type')}")
        print(f"  Title: {viz.get('title')}")
        print(f"  Data items: {len(viz.get('data', []))}")
elif 'visualization' in result:
    print("\nSingle visualization found:")
    viz = result['visualization']
    print(f"  Type: {viz.get('type')}")
    print(f"  Title: {viz.get('title')}")
    print(f"  Data items: {len(viz.get('data', []))}")
else:
    print("\nNo visualizations found")

# Save result to file for inspection
with open('test_result.json', 'w') as f:
    # Convert any remaining non-serializable objects
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(item) for item in obj]
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        elif not isinstance(obj, (str, int, float, bool, type(None))):
            return str(obj)
        return obj
    
    clean_result = clean_for_json(result)
    json.dump(clean_result, f, indent=2)
    print("\nFull result saved to test_result.json")