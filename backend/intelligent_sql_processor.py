"""
Intelligent SQL Query Processor using GPT-5
Generates SQL queries instead of pandas code for better performance
"""
import pandas as pd
import numpy as np
import json
from openai import OpenAI
import os
from typing import Dict, Any, List
import pyodbc
from database.sql_config import db_config

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_database_schema():
    """Get the database schema for the LLM context"""
    return """
    Database Schema:
    
    1. salesorder table (424,363 rows):
       - Id (PRIMARY KEY)
       - customeridname: Customer name
       - totalamount: Order total amount
       - statuscode: Order status (1=Active, 2=Submitted, 3=Canceled, 4=Fulfilled, 100=Invoiced)
       - modifiedon: Last modified date
       - billto_city: Billing city
       - billto_country: Billing country
       - ordernumber: Order number
    
    2. quote table (224,928 rows):
       - Id (PRIMARY KEY)
       - name: Quote name
       - totalamount: Quote total amount
       - statuscode: Quote status
       - customeridname: Customer name
       - modifiedon: Last modified date
       - quotenumber: Quote number
    
    3. quotedetail table (1,242,875 rows):
       - Id (PRIMARY KEY)
       - quoteid: Foreign key to quote table
       - productidname: Product name
       - quantity: Quantity ordered
       - priceperunit: Price per unit
       - extendedamount: Extended amount (quantity * price)
       - producttypecode: Product type code
    
    Available indexes for optimization:
    - IX_salesorder_customer, IX_salesorder_amount, IX_salesorder_date
    - IX_quote_customer, IX_quote_amount, IX_quote_date
    - IX_quotedetail_quote, IX_quotedetail_product
    """

def process_sql_query(query: str) -> Dict[str, Any]:
    """Process natural language query and generate SQL with visualizations"""
    
    schema_info = get_database_schema()
    
    system_prompt = f"""You are an expert SQL Server analyst. Generate SQL queries and data visualizations.

{schema_info}

Important Instructions:
1. Generate efficient SQL Server queries (T-SQL syntax)
2. Use appropriate JOINs when needed
3. Always limit results appropriately (TOP clause for SQL Server)
4. Generate 3-5 different visualization types for the data
5. Return results in the exact JSON format specified

Output Format:
{{
    "sql_query": "Your SQL query here",
    "answer": "Natural language answer to the question",
    "visualizations": [
        {{
            "type": "bar|pie|line|area|scatter|radar",
            "title": "Descriptive title",
            "sql_for_chart": "SQL query specifically for this chart's data",
            "chart_config": {{
                "xAxis": "column_name",
                "yAxis": "column_name",
                "color": "#color_code"
            }}
        }}
    ],
    "recommendations": ["insight1", "insight2", "insight3"]
}}
"""
    
    user_prompt = f"User Query: {query}\n\nGenerate SQL queries and multiple visualizations."
    
    try:
        # Use GPT-5 to generate SQL
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            reasoning_effort="medium",
            max_completion_tokens=3000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Execute SQL queries and format results
        conn = db_config.get_connection()
        
        # Execute main query
        main_df = pd.read_sql_query(result['sql_query'], conn)
        
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
                        elif hasattr(value, 'isoformat'):
                            item[key] = value.isoformat()
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
        
        # Format the answer with actual data
        if len(main_df) > 0:
            answer = result['answer']
            # Add actual data points to answer
            if 'top' in query.lower():
                top_results = main_df.head(10).to_string(index=False)
                answer += f"\n\nActual results:\n{top_results}"
        else:
            answer = "No data found for this query."
        
        return {
            'answer': answer,
            'visualizations': visualizations,
            'recommendations': result.get('recommendations', []),
            'sql_query': result['sql_query'],
            'row_count': len(main_df)
        }
        
    except Exception as e:
        print(f"Error processing SQL query: {e}")
        return {
            'answer': f"Error processing query: {str(e)}",
            'visualizations': [],
            'recommendations': [],
            'error': str(e)
        }

def get_database_stats():
    """Get current database statistics"""
    try:
        conn = db_config.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        tables = ['salesorder', 'quote', 'quotedetail']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            # Get table size
            cursor.execute(f"""
                SELECT 
                    SUM(a.total_pages) * 8 / 1024.0 as size_mb
                FROM sys.tables t
                INNER JOIN sys.indexes i ON t.object_id = i.object_id
                INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                WHERE t.name = '{table}'
                GROUP BY t.name
            """)
            
            size_result = cursor.fetchone()
            size_mb = size_result[0] if size_result else 0
            
            stats[table] = {
                'row_count': count,
                'size_mb': round(size_mb, 2)
            }
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}

def test_sql_connection():
    """Test SQL Server connection and return status"""
    try:
        if db_config.test_connection():
            stats = get_database_stats()
            return {
                'connected': True,
                'database': db_config.database,
                'server': db_config.server,
                'stats': stats
            }
        else:
            return {
                'connected': False,
                'error': 'Failed to connect to SQL Server'
            }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e)
        }