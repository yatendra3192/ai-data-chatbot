import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store last query result for context
last_query_result = {}

def analyze_query_with_llm(query: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Use OpenAI to intelligently process any natural language query about the data
    """
    global last_query_result
    
    # Get data schema information
    schema_info = {
        "columns": data.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
        "shape": data.shape,
        "numeric_columns": data.select_dtypes(include=[np.number]).columns.tolist(),
        "text_columns": data.select_dtypes(include=['object']).columns.tolist(),
        "sample_values": {}
    }
    
    # Add sample values for key columns
    for col in ['customeridname', 'totalamount', 'statuscode', 'ordernumber', 'modifiedon']:
        if col in data.columns:
            non_null = data[col].dropna()
            if len(non_null) > 0:
                if data[col].dtype == 'object':
                    schema_info["sample_values"][col] = non_null.head(3).tolist()
                elif pd.api.types.is_datetime64_any_dtype(data[col]):
                    # Handle datetime/timestamp columns
                    schema_info["sample_values"][col] = non_null.head(3).astype(str).tolist()
                else:
                    # Handle numeric columns
                    try:
                        schema_info["sample_values"][col] = [float(x) if pd.notna(x) else None for x in non_null.head(3)]
                    except:
                        # Fallback to string representation if conversion fails
                        schema_info["sample_values"][col] = non_null.head(3).astype(str).tolist()
    
    # Create prompt for OpenAI
    system_prompt = """You are a data analyst AI that generates Python pandas code to answer questions about sales data.
    Given a user's question and the data schema, generate Python code that will answer their question.
    
    CRITICAL REQUIREMENT: ALWAYS GENERATE MULTIPLE APPROPRIATE VISUALIZATIONS
    
    IMPORTANT RULES:
    1. Generate ONLY executable Python pandas code
    2. The dataframe variable is called 'data'
    3. Store the final result in a variable called 'result'
    4. ALWAYS return 'visualizations' (plural) with ALL appropriate chart types for the data:
       
       For each query, think about ALL visualization types that make sense:
       - COMPARISON DATA (top X, rankings): Generate bar, pie, horizontal bar, and possibly radar
       - TIME SERIES DATA (trends, dates): Generate line, area, and bar charts
       - PROPORTIONS/PARTS OF WHOLE: Generate pie, donut, stacked bar, and treemap
       - CORRELATIONS: Generate scatter, bubble, and heatmap
       - DISTRIBUTIONS: Generate histogram, box plot, and violin plot
       - GEOGRAPHIC DATA: Generate map, choropleth if location data exists
       
    5. Intelligently select 3-6 most appropriate chart types based on:
       - Data characteristics (categorical vs continuous)
       - Number of data points (pie charts only for ≤8 items)
       - Query intent (comparison, trend, distribution, correlation)
       - Visual effectiveness (some charts work better for certain data)
    
    6. Each visualization must have:
       - Unique and descriptive title
       - Appropriate chart type
       - Same underlying data (formatted appropriately for each chart type)
       - Proper config for that chart type
    
    7. The 'data' key should be a list of dicts with appropriate keys
    8. Always handle NaN values appropriately
    9. Return results that can be directly displayed to the user
    
    ALWAYS USE THIS FORMAT - MULTIPLE VISUALIZATIONS:
    
    ```python
    # Example for "top 5 customers by revenue" - comparison data
    result = {
        'answer': 'The top 5 customers by revenue are...',
        'visualizations': [
            {
                'type': 'bar',
                'title': 'Top 5 Customers - Bar Chart',
                'data': [{'name': 'Customer A', 'value': 50000}, ...],
                'config': {'xAxis': 'name', 'yAxis': 'value', 'color': '#818CF8'}
            },
            {
                'type': 'pie',
                'title': 'Revenue Distribution - Pie Chart',
                'data': [{'name': 'Customer A', 'value': 50000}, ...],
                'config': {'yAxis': 'value'}
            },
            {
                'type': 'radar',
                'title': 'Customer Comparison - Radar View',
                'data': [{'name': 'Customer A', 'value': 50000}, ...],
                'config': {'xAxis': 'name', 'yAxis': 'value'}
            },
            {
                'type': 'area',
                'title': 'Cumulative Revenue - Area Chart',
                'data': [{'name': 'Customer A', 'value': 50000}, ...],
                'config': {'xAxis': 'name', 'yAxis': 'value', 'color': '#10B981'}
            }
        ]
    }
    
    # Example for time series/trend data
    result = {
        'answer': 'Monthly sales trend shows...',
        'visualizations': [
            {'type': 'line', 'title': 'Sales Trend - Line Chart', 'data': [...]},
            {'type': 'area', 'title': 'Cumulative Sales - Area Chart', 'data': [...]},
            {'type': 'bar', 'title': 'Monthly Sales - Bar Chart', 'data': [...]},
            {'type': 'scatter', 'title': 'Sales Distribution - Scatter Plot', 'data': [...]}
        ]
    }
    
    # Example for distribution/proportion data
    result = {
        'answer': 'Order status distribution...',
        'visualizations': [
            {'type': 'pie', 'title': 'Status Distribution - Pie Chart', 'data': [...]},
            {'type': 'bar', 'title': 'Status Counts - Bar Chart', 'data': [...]},
            {'type': 'stacked-bar', 'title': 'Status Breakdown - Stacked Bar', 'data': [...]},
            {'type': 'donut', 'title': 'Status Overview - Donut Chart', 'data': [...]}
        ]
    }
    ```
    
    NEVER return just 'visualization' (singular). ALWAYS return 'visualizations' (plural) with 3-6 appropriate chart types!
    """
    
    # Check if this is a chart conversion request
    query_lower = query.lower()
    is_chart_conversion = any(phrase in query_lower for phrase in [
        'pie chart for this', 'convert to pie', 'make it pie', 'show as pie', 'give me pie',
        'bar chart for this', 'convert to bar', 'make it bar', 'show as bar',
        'line chart for this', 'convert to line', 'make it line', 'show as line'
    ])
    
    # Handle chart conversion directly without calling OpenAI
    if is_chart_conversion and last_query_result.get('visualization'):
        last_viz = last_query_result['visualization']
        
        # Determine requested chart type
        if 'pie' in query_lower:
            chart_type = 'pie'
        elif 'line' in query_lower:
            chart_type = 'line'
        elif 'bar' in query_lower:
            chart_type = 'bar'
        else:
            chart_type = 'pie'  # default
        
        # Directly return the converted visualization
        converted_result = {
            'answer': f"Here's the same data as a {chart_type} chart:",
            'visualization': {
                'type': chart_type,
                'title': last_viz.get('title', 'Data Visualization'),
                'data': last_viz.get('data', []),
                'config': last_viz.get('config', {})
            }
        }
        # Update last_query_result with the converted version
        last_query_result.update(converted_result)
        return converted_result
    
    context_info = ""
    if is_chart_conversion and not last_query_result.get('visualization'):
        # No previous visualization to convert
        context_info = """\n    CONTEXT: User is asking for a chart conversion but there's no previous visualization.
    Generate a new visualization based on the query.
    """
    
    user_prompt = f"""
    User Question: {query}
    {context_info}
    
    Data Schema:
    - Shape: {schema_info['shape'][0]} rows, {schema_info['shape'][1]} columns
    - Columns: {', '.join(schema_info['columns'][:20])}{'...' if len(schema_info['columns']) > 20 else ''}
    - Key numeric columns: {', '.join(schema_info['numeric_columns'][:10])}
    - Key text columns: {', '.join(schema_info['text_columns'][:10])}
    - Sample values: {json.dumps(schema_info['sample_values'], indent=2)}
    
    Generate Python pandas code to answer this question. 
    
    CRITICAL: You MUST return 'visualizations' (plural) with ALL appropriate chart types for this data:
    - For comparison/ranking data: Include bar, pie, horizontal bar, and possibly radar charts
    - For time series data: Include line, area, and bar charts
    - For distributions: Include pie, bar, and histogram
    - For correlations: Include scatter plots
    
    Think about which 3-6 chart types best visualize this specific query and data.
    Each chart should have a unique, descriptive title.
    
    Remember to store the result in a variable called 'result' with 'visualizations' array.
    """
    
    try:
        # Use GPT-5 with reasoning_effort parameter
        response = client.chat.completions.create(
            model="gpt-5",  # Using GPT-5
            messages=[
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            reasoning_effort="medium",  # Options: minimal, low, medium, high
            max_completion_tokens=5000
        )
        # Extract code from GPT-5 response
        code = response.choices[0].message.content
        
        # Clean up code (remove markdown if present)
        if '```python' in code:
            code = code.split('```python')[1].split('```')[0]
        elif '```' in code:
            code = code.split('```')[1].split('```')[0]
        
        # Execute the generated code
        local_vars = {'data': data, 'pd': pd, 'np': np}
        exec(code, {}, local_vars)
        
        # Get the result
        if 'result' in local_vars:
            result = local_vars['result']
            
            # Ensure proper format
            if isinstance(result, dict):
                # The LLM should always provide 'visualizations' (plural) now
                # But handle backward compatibility if it provides 'visualization' (singular)
                if 'visualization' in result and 'visualizations' not in result:
                    # Convert single visualization to array
                    result['visualizations'] = [result['visualization']]
                    del result['visualization']
                
                # Clean all visualization data to ensure JSON serialization
                if 'visualizations' in result:
                    for viz in result['visualizations']:
                        if 'data' in viz and viz['data']:
                            cleaned_data = []
                            for item in viz['data']:
                                cleaned_item = {}
                                for key, value in item.items():
                                    # Convert non-serializable types to string
                                    if hasattr(value, 'isoformat'):
                                        cleaned_item[key] = value.isoformat()
                                    elif pd.api.types.is_datetime64_any_dtype(type(value)):
                                        cleaned_item[key] = str(value)
                                    elif isinstance(value, (pd.Timestamp, pd.Period)):
                                        cleaned_item[key] = str(value)
                                    elif pd.isna(value):
                                        cleaned_item[key] = None
                                    elif not isinstance(value, (str, int, float, bool, type(None))):
                                        cleaned_item[key] = str(value)
                                    else:
                                        cleaned_item[key] = value
                                cleaned_data.append(cleaned_item)
                            viz['data'] = cleaned_data
                
                # Generate intelligent recommendations based on the actual data
                if 'answer' in result:
                    # Get the first visualization's data for recommendations
                    rec_data = []
                    if 'visualizations' in result and result['visualizations']:
                        rec_data = result['visualizations'][0].get('data', [])
                    elif 'visualization' in result:
                        rec_data = result['visualization'].get('data', [])
                    
                    if rec_data:
                        recommendations = generate_intelligent_recommendations(query, result['answer'], rec_data)
                        result['recommendations'] = recommendations
                
                # Store for context in next query
                last_query_result = result.copy()
                return result
            else:
                # Convert simple results to proper format
                return {
                    'answer': str(result),
                    'metrics': {}
                }
        else:
            # Fallback if no result variable
            return {
                'answer': "Analysis completed but no specific result was generated.",
                'code_executed': code[:500]
            }
            
    except Exception as e:
        # If OpenAI fails or code execution fails, provide helpful error and fallback
        print(f"LLM Analysis Error: {str(e)}")
        
        # Fallback to basic analysis
        try:
            # Try to provide some basic info about the query
            if 'customer' in query.lower():
                if 'customeridname' in data.columns and 'totalamount' in data.columns:
                    top_customers = data.groupby('customeridname')['totalamount'].sum().nlargest(10)
                    return {
                        'answer': f"Top customers by revenue:\n" + '\n'.join([f"{i+1}. {c}: ${v:,.2f}" for i, (c, v) in enumerate(top_customers.items())]),
                        'visualization': {
                            'type': 'bar',
                            'title': 'Top Customers by Revenue',
                            'data': [{'name': str(c)[:40], 'value': float(v)} for c, v in top_customers.items()]
                        }
                    }
            
            # Generic response
            return {
                'answer': f"I'll analyze your question: '{query}'. The dataset has {len(data):,} rows and {len(data.columns)} columns. Please try rephrasing your question for better results.",
                'error': str(e)
            }
        except:
            return {
                'answer': f"Unable to process the query: {query}. Please try a different question.",
                'error': str(e)
            }

def generate_intelligent_recommendations(query: str, answer: str, chart_data: list) -> List[str]:
    """
    Generate intelligent recommendations based on the query results using LLM
    """
    try:
        # Prepare context from the chart data
        data_summary = ""
        if chart_data and len(chart_data) > 0:
            # Extract key insights from the data
            values = [item.get('value', 0) for item in chart_data[:10] if 'value' in item]
            names = [item.get('name', '') for item in chart_data[:10] if 'name' in item]
            
            if values:
                max_val = max(values)
                min_val = min(values)
                avg_val = sum(values) / len(values)
                data_summary = f"Max: {max_val:.2f}, Min: {min_val:.2f}, Average: {avg_val:.2f}"
                
                # Calculate concentration
                if len(values) > 1:
                    top_20_percent = int(len(values) * 0.2) or 1
                    top_20_sum = sum(sorted(values, reverse=True)[:top_20_percent])
                    total_sum = sum(values)
                    concentration = (top_20_sum / total_sum * 100) if total_sum > 0 else 0
                    data_summary += f", Top 20% concentration: {concentration:.1f}%"
        
        # Extract actual data values for more specific recommendations
        actual_data_points = ""
        if chart_data and len(chart_data) > 0:
            top_items = chart_data[:3]
            actual_data_points = "Top data points: "
            for item in top_items:
                if 'name' in item and 'value' in item:
                    actual_data_points += f"{item['name']}: {item['value']}, "
        
        prompt = f"""Based on this SPECIFIC data analysis:
Query: {query}
Answer: {answer}
Data Summary: {data_summary}
Actual Data: {actual_data_points}
Full Data Sample: {json.dumps(chart_data[:5], default=str) if chart_data else 'No data'}

Generate 4 ULTRA-SPECIFIC, actionable business recommendations that directly reference the data shown above.

CRITICAL RULES:
1. Each recommendation MUST mention specific numbers, names, or values from the data
2. If it's about customers, mention the actual customer names/values
3. If it's about geography, mention the actual states/regions and their numbers
4. If it's about revenue, mention the actual dollar amounts
5. Never use generic phrases like "high-value customers" - use actual names/values
6. Each recommendation should be different and specific to different aspects of the data

Examples of GOOD recommendations:
- "Focus retention efforts on Customer ABC Corp with $1.2M revenue representing 15% of total"
- "Expand presence in California where 60,000 customers generate 40% of revenue"
- "Address the 35% revenue gap between top performer ($500K) and average ($325K)"

Examples of BAD generic recommendations to AVOID:
- "Focus retention efforts on high-value customers"
- "Analyze customer purchase patterns"
- "Segment customers by value"

Return ONLY 4 ultra-specific recommendations as a JSON array of strings, no other text."""

        # Use GPT-5 with correct API format
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "developer", "content": "You are a data analyst providing ultra-specific, data-driven recommendations. Always reference actual numbers and names from the data."},
                {"role": "user", "content": prompt}
            ],
            reasoning_effort="high",  # High effort for detailed analysis
            max_completion_tokens=600
        )
        content = response.choices[0].message.content.strip()
        
        # Parse the response - content is already set above
        
        # Try to extract JSON array
        if content.startswith('['):
            recommendations = json.loads(content)
        else:
            # Try to find JSON array in the response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
            else:
                # Fallback to splitting by newlines
                recommendations = [line.strip('- •123456789.') for line in content.split('\n') if line.strip()][:4]
        
        # Ensure we have exactly 4 recommendations
        if len(recommendations) > 4:
            recommendations = recommendations[:4]
        elif len(recommendations) < 4:
            # Add more specific recommendations based on the data
            if chart_data and len(chart_data) > 0:
                # Generate data-specific fillers
                if names and values:
                    specific_fillers = [
                        f"Monitor {names[0]} closely as it represents {values[0]:.0f} in value",
                        f"Investigate gap between {names[0]} ({values[0]:.0f}) and average ({avg_val:.0f})",
                        f"Set target to increase average from {avg_val:.0f} to match top performer at {max_val:.0f}",
                        f"Focus on bottom performers below {min_val:.0f} threshold for improvement"
                    ]
                    recommendations.extend(specific_fillers[:(4-len(recommendations))])
            else:
                generic = [
                    "Deep dive into the specific patterns identified above",
                    "Set up tracking for the key metrics highlighted",
                    "Create action plans based on these findings",
                    "Review performance against these benchmarks monthly"
                ]
                recommendations.extend(generic[:(4-len(recommendations))])
        
        return recommendations
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        # Return context-aware fallback recommendations
        query_lower = query.lower()
        if 'customer' in query_lower:
            return [
                "Focus retention efforts on high-value customers",
                "Analyze customer purchase patterns for upselling opportunities",
                "Segment customers by value for targeted marketing",
                "Monitor customer churn indicators"
            ]
        elif 'revenue' in query_lower or 'sales' in query_lower:
            return [
                "Optimize pricing strategies based on demand patterns",
                "Identify and expand high-margin product lines",
                "Implement dynamic forecasting for better inventory management",
                "Focus on converting high-value quotes to orders"
            ]
        elif 'order' in query_lower:
            return [
                "Streamline order processing for faster fulfillment",
                "Analyze order patterns to optimize inventory levels",
                "Implement automated order status tracking",
                "Review and reduce order cancellation rates"
            ]
        else:
            return [
                "Establish KPI dashboards for real-time monitoring",
                "Implement predictive analytics for trend forecasting",
                "Automate routine data analysis tasks",
                "Create data-driven decision frameworks"
            ]

def process_data_query(query: str, data: pd.DataFrame) -> Dict[str, Any]:
    """
    Main entry point for intelligent query processing
    """
    return analyze_query_with_llm(query, data)