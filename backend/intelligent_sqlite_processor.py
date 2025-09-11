"""
Intelligent SQLite Query Processor using GPT-5
Generates SQL queries for better performance on large datasets
Updated to use GPT-5 with new responses API
"""
import pandas as pd
import numpy as np
import json
from openai import OpenAI
import os
from typing import Dict, Any, List
import sqlite3
from datetime import datetime
import time

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("[WARNING] OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is not set")
    
client = OpenAI(api_key=api_key)
print(f"[INFO] OpenAI client initialized with API key: ...{api_key[-4:] if api_key else 'None'}")

# SQLite database path
DB_PATH = "database/crm_analytics.db"

def get_database_schema():
    """Get the database schema for the LLM context"""
    return """
    Database Schema (SQLite):
    
    1. salesorder table (60,481 rows):
       - Id (TEXT PRIMARY KEY)
       - customeridname: Customer name
       - totalamount: Order total amount (REAL)
       - statuscode: Order status (INTEGER)
       - modifiedon: Last modified date (TEXT)
       - billto_city: Billing city
       - billto_country: Billing country
       - ordernumber: Order number
    
    2. quote table (141,461 rows):
       - Id (TEXT PRIMARY KEY)
       - name: Quote name
       - totalamount: Quote total amount (REAL)
       - statuscode: Quote status (INTEGER)
       - customeridname: Customer name
       - modifiedon: Last modified date (TEXT)
       - quotenumber: Quote number
    
    3. quotedetail table (580,000 rows):
       - Id (TEXT PRIMARY KEY)
       - quoteid: Foreign key to quote table
       - productidname: Product name
       - quantity: Quantity ordered (REAL)
       - priceperunit: Price per unit (REAL)
       - extendedamount: Extended amount (REAL)
       - producttypecode: Product type code (INTEGER)
    
    SQLite Date Functions:
    - Use strftime('%Y-%m', modifiedon) for month extraction
    - Use strftime('%Y', modifiedon) for year extraction
    - Use date(modifiedon) for date comparisons
    
    Available indexes for optimization:
    - Customer name indexes on salesorder and quote tables
    - Amount indexes on all tables
    - Date indexes on salesorder and quote tables
    - Product and quote indexes on quotedetail table
    """

def process_sqlite_query(query: str, use_high_reasoning: bool = False) -> Dict[str, Any]:
    """Process natural language query and generate SQL with visualizations
    
    Args:
        query: Natural language query from user
        use_high_reasoning: If True, uses GPT-5 with high reasoning for complex queries
    """
    
    start_time = time.time()
    
    # Determine reasoning effort based on query complexity
    reasoning_effort = "high" if use_high_reasoning or "complex" in query.lower() else "medium"
    
    schema_info = get_database_schema()
    
    system_prompt = f"""You are an expert SQLite analyst. Generate SQL queries and data visualizations.

{schema_info}

Important Instructions:
1. Generate efficient SQLite queries (use LIMIT, not TOP)
2. Use appropriate JOINs when needed
3. Always limit results appropriately (LIMIT clause for SQLite)
4. Generate 4-5 different visualization types for the data
5. Return results in the exact JSON format specified
6. Use SQLite date functions (strftime) for date operations
7. For pie and doughnut charts, ensure data has 'name' and 'value' columns
8. When showing top N items, create bar, pie, and doughnut charts using the same data
9. IMPORTANT: Your answer MUST include the actual names/values from query results (e.g., "The top client is Acme Corp with $1.2M in revenue")

Output Format:
{{
    "sql_query": "Your SQL query here",
    "answer": "Natural language answer that includes specific names and values from the results",
    "visualizations": [
        {{
            "type": "bar|pie|doughnut|line|area|scatter|radar",
            "title": "Descriptive title",
            "sql_for_chart": "SQL query specifically for this chart's data (must include column aliases matching xAxis/yAxis)",
            "chart_config": {{
                "xAxis": "name",  // For pie/doughnut use "name" 
                "yAxis": "value", // For pie/doughnut use "value"
                "color": "#818CF8"
            }}
        }}
    ],
    "recommendations": ["insight1", "insight2", "insight3"]
}}
"""
    
    user_prompt = f"User Query: {query}\n\nGenerate SQL queries and multiple visualizations."
    
    try:
        # Try GPT-5 with new responses API
        response = None
        max_retries = 2
        retry_count = 0
        
        # Combine system and user prompts for GPT-5
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        while retry_count < max_retries and response is None:
            try:
                print(f"[API] Attempting GPT-5 call (attempt {retry_count + 1}/{max_retries})")
                response = client.responses.create(
                    model="gpt-5",
                    input=combined_prompt,
                    reasoning={
                        "effort": reasoning_effort  # Dynamic based on query complexity
                    },
                    text={
                        "verbosity": "medium"  # Medium verbosity for detailed SQL and visualizations
                    }
                )
                print("[API] GPT-5 call successful")
            except Exception as e:
                print(f"[API] GPT-5 attempt {retry_count + 1} failed: {str(e)[:200]}")
                retry_count += 1
                if retry_count >= max_retries:
                    # Fallback to GPT-4 with chat completions
                    print("[API] All GPT-5 attempts failed, trying GPT-4")
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.3,
                            max_tokens=3000,
                            timeout=30
                        )
                        print("[API] GPT-4 fallback successful")
                        # Mark this as a chat completion response for later handling
                        response._is_chat_completion = True
                    except Exception as e2:
                        print(f"[API] GPT-4 also failed: {str(e2)[:200]}")
                        # Final fallback to GPT-3.5
                        try:
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                temperature=0.3,
                                max_tokens=3000,
                                timeout=30
                            )
                            print("[API] GPT-3.5 fallback successful")
                            response._is_chat_completion = True
                        except Exception as e3:
                            print(f"[API] All models failed. Last error: {str(e3)[:200]}")
                            raise Exception(f"All models (GPT-5, GPT-4, GPT-3.5) failed. Last error: {str(e3)}")
                else:
                    time.sleep(1)  # Wait 1 second before retry
        
        # Get response content based on API type
        if hasattr(response, '_is_chat_completion') and response._is_chat_completion:
            # Handle chat completion response (GPT-4/GPT-3.5 fallback)
            if not response or not response.choices or not response.choices[0].message.content:
                raise ValueError("API returned empty response")
            raw_content = response.choices[0].message.content.strip()
        else:
            # Handle GPT-5 responses API
            if not response or not hasattr(response, 'output_text'):
                raise ValueError("GPT-5 API returned empty response")
            raw_content = response.output_text.strip()
            
        print(f"[DEBUG] Raw API response length: {len(raw_content)}")
        
        if not raw_content:
            raise ValueError("API returned empty content")
        
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse extracted JSON: {e}")
                print(f"[ERROR] Extracted content: {json_match.group()[:500]}...")
                raise ValueError(f"Invalid JSON in API response: {e}")
        else:
            try:
                result = json.loads(raw_content)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse raw response as JSON: {e}")
                print(f"[ERROR] Raw content: {raw_content[:500]}...")
                raise ValueError(f"API did not return valid JSON: {e}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(DB_PATH)
        
        # Execute main query
        print(f"[MAIN QUERY] Executing: {result['sql_query']}")
        main_df = pd.read_sql_query(result['sql_query'], conn)
        print(f"[MAIN QUERY] Got {len(main_df)} rows")
        
        # Execute visualization queries and format data
        visualizations = []
        for viz in result.get('visualizations', []):
            try:
                # Execute SQL for this specific visualization
                viz_df = pd.read_sql_query(viz['sql_for_chart'], conn)
                
                # Format data for frontend
                chart_data = viz_df.to_dict('records')
                
                # Clean up data types
                for item in chart_data:
                    for key, value in item.items():
                        if pd.isna(value):
                            item[key] = None
                        elif isinstance(value, (pd.Timestamp, datetime)):
                            item[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
                        elif not isinstance(value, (str, int, float, bool, type(None))):
                            item[key] = str(value)
                
                visualizations.append({
                    'type': viz['type'],
                    'title': viz['title'],
                    'data': chart_data,
                    'config': viz.get('chart_config', {})
                })
                
            except Exception as e:
                print(f"Error executing chart SQL: {e}")
        
        conn.close()
        
        # Now that we have the actual data, ask the LLM to generate a proper answer
        text_summary = ""
        if len(main_df) > 0:
            # Convert dataframe to a readable format for the LLM
            data_summary = main_df.head(10).to_dict('records')
            
            # Create a new prompt with the actual data for brief answer
            answer_prompt = f"""
            User asked: {query}
            
            The SQL query returned this data:
            {json.dumps(data_summary, indent=2)}
            
            Please provide a natural language answer that includes the specific names and values from the data.
            Be concise and direct. Include the actual client names, product names, or values as appropriate.
            """
            
            # Create a second prompt for detailed text summary
            text_summary_prompt = f"""
            User asked: {query}
            
            The SQL query returned this data:
            {json.dumps(data_summary, indent=2)}
            
            Please format this data into a clear, readable text summary that lists all the details.
            Format it like this:
            
            For order data, use:
            1. Order ID: [ID] | Customer: [Name] | Amount: $[Amount] | Status: [Status] | Date: [Date]
            2. Order ID: [ID] | Customer: [Name] | Amount: $[Amount] | Status: [Status] | Date: [Date]
            
            For product data, use:
            1. Product: [Name] | Quantity: [Qty] | Revenue: $[Amount]
            
            For customer data, use:
            1. Customer: [Name] | Total Revenue: $[Amount] | Orders: [Count]
            
            Include all rows from the data provided. Format numbers with commas for thousands.
            """
            
            try:
                # Ask the LLM to generate an answer based on the actual data
                answer_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a data analyst. Provide clear, concise answers using the actual data provided."},
                        {"role": "user", "content": answer_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                answer = answer_response.choices[0].message.content
                
                # Generate detailed text summary
                text_summary_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a data formatter. Format the data into a clear, readable text list with all details."},
                        {"role": "user", "content": text_summary_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                text_summary = text_summary_response.choices[0].message.content
                
            except Exception as e:
                print(f"[ERROR] Failed to generate answer with data: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to original answer
                answer = result.get('answer', 'No answer provided')
                text_summary = ""
        else:
            answer = "No data found for this query."
            text_summary = ""
        
        # Convert DataFrame to list of dictionaries for table view
        table_data = []
        if len(main_df) > 0:
            # Clean up data types for JSON serialization
            for _, row in main_df.iterrows():
                record = {}
                for col, val in row.items():
                    if pd.isna(val):
                        record[col] = None
                    elif isinstance(val, (np.integer, np.floating)):
                        record[col] = float(val) if pd.api.types.is_float_dtype(type(val)) else int(val)
                    elif isinstance(val, np.bool_):
                        record[col] = bool(val)
                    else:
                        record[col] = str(val)
                table_data.append(record)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Return the formatted answer (not the original LLM answer)
        return {
            'answer': answer,  # This now contains our formatted answer with actual client name
            'text_summary': text_summary,  # New field with detailed text data
            'visualizations': visualizations,
            'recommendations': result.get('recommendations', []),
            'sql_query': result['sql_query'],
            'table_data': table_data,  # Add table data for display
            'row_count': len(main_df),
            'execution_time': round(execution_time, 3)
        }
        
    except Exception as e:
        print(f"Error processing SQLite query: {e}")
        return {
            'answer': f"Error processing query: {str(e)}",
            'text_summary': '',
            'visualizations': [],
            'recommendations': [],
            'sql_query': '',
            'table_data': [],
            'row_count': 0,
            'execution_time': 0,
            'error': str(e)
        }

def get_database_stats():
    """Get current database statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        stats = {}
        tables = ['salesorder', 'quote', 'quotedetail']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            # Get table size (approximate)
            cursor.execute(f"SELECT SUM(length(Id)) FROM {table} LIMIT 1000")
            sample_size = cursor.fetchone()[0] or 0
            estimated_size_mb = (sample_size * count / 1000) / (1024 * 1024)
            
            stats[table] = {
                'row_count': count,
                'estimated_size_mb': round(estimated_size_mb, 2)
            }
        
        # Get database file size
        import os
        if os.path.exists(DB_PATH):
            db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
            stats['database_size_mb'] = round(db_size_mb, 2)
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}

def test_sqlite_connection():
    """Test SQLite connection and return status"""
    try:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            stats = get_database_stats()
            return {
                'connected': True,
                'database': 'SQLite (crm_analytics.db)',
                'tables': [t[0] for t in tables],
                'stats': stats
            }
        else:
            return {
                'connected': False,
                'error': f'Database file not found: {DB_PATH}'
            }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e)
        }

# Test function for standalone execution
if __name__ == "__main__":
    print("Testing SQLite connection...")
    status = test_sqlite_connection()
    print(json.dumps(status, indent=2))
    
    if status['connected']:
        print("\nTesting sample query...")
        result = process_sqlite_query("What are the top 5 customers by revenue?")
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Visualizations generated: {len(result['visualizations'])}")
        print(f"Recommendations: {result['recommendations']}")