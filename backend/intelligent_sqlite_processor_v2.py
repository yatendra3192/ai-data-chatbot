"""
Improved SQLite Query Processor with robust JSON parsing and error handling
"""
import pandas as pd
import numpy as np
import json
import re
from openai import OpenAI
import os
from typing import Dict, Any, List, Optional
import sqlite3
from datetime import datetime
import traceback

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# SQLite database path
DB_PATH = "database/crm_analytics.db"

def extract_json_from_text(text: str) -> Optional[Dict]:
    """Extract JSON from text that might contain markdown or other formatting"""
    # Try to find JSON block in markdown code blocks
    json_patterns = [
        r'```json\s*(.*?)\s*```',  # JSON in markdown code block
        r'```\s*(.*?)\s*```',       # Generic code block
        r'\{.*\}',                   # Raw JSON object
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                # Clean up the match
                cleaned = match.strip()
                # Try to parse as JSON
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue
    
    # Last resort: try to parse the entire text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def get_database_schema():
    """Get the database schema for the LLM context with accurate column information"""
    return """
    Database Schema (SQLite) - ACTUAL AVAILABLE COLUMNS:
    
    1. salesorder table (60,481 rows) - Orders/Sales Data:
       AVAILABLE COLUMNS:
       - Id (TEXT PRIMARY KEY): Sales Order ID (unique identifier)
       - ordernumber: Order Number (e.g., ORD-30741-T8V7) - Main order identifier
       - customeridname: Customer Name - Full customer name
       - totalamount: Total Amount (REAL) - Complete order amount including tax
       - totaltax: Total Tax (REAL) - Tax amount for the order ✓ NOW AVAILABLE
       - createdon: Order creation date (TEXT) - When order was created ✓ NOW AVAILABLE
       - statuscode: Order Status (INTEGER) - Order status code
       - modifiedon: Modified On (TEXT) - Last modification date
       - billto_city: Billing City - Customer's billing city
       - billto_country: Billing Country - Customer's billing country/region
       
       COLUMN MEANINGS FROM DATA DICTIONARY:
       - statuscode: Order processing status (active/inactive/completed)
       - totalamount: Complete order value including all charges and tax
       - totaltax: Total tax charged on the order
       - ordernumber: Primary business identifier for orders
       - customeridname: Full name of the customer/account
       
       NOTE: Tax information is NOW AVAILABLE. Use 'totaltax' column for tax amounts.
    
    2. quote table (141,461 rows) - Quote/Proposal Data:
       AVAILABLE COLUMNS:
       - Id (TEXT PRIMARY KEY): Record ID - Unique quote identifier
       - quotenumber: Quote Number - Primary business identifier for quotes
       - name: Quote Name - Title/description of the quote
       - customeridname: Customer Name - Full customer/account name
       - totalamount: Total Amount (REAL) - Complete quote value including all charges
       - statuscode: Quote Status (INTEGER) - Quote processing status
       - modifiedon: Modified On (TEXT) - Last modification date
       
       COLUMN MEANINGS FROM DATA DICTIONARY:
       - statuscode: Quote processing state (draft/active/won/lost)
       - totalamount: Complete quote value including line items
       - quotenumber: Primary identifier used in business operations
       - name: Descriptive title for the quote
       - customeridname: Full name of customer/account
       
       NOTE: Tax, discount, and other financial columns are NOT in current database.
    
    3. quotedetail table (1,237,446 rows) - Quote Line Items:
       AVAILABLE COLUMNS:
       - Id (TEXT PRIMARY KEY): Record ID - Unique line item identifier
       - quoteid: Quote ID - Links to parent quote (foreign key to quote table)
       - productidname: Product Name - Name of product/service being quoted
       - quantity: Quantity (REAL) - Number of units being quoted
       - priceperunit: Price Per Unit (REAL) - Unit price for the product/service
       - extendedamount: Extended Amount (REAL) - Line total (quantity × price)
       - producttypecode: Product Type (INTEGER) - Category/type of product
       
       COLUMN MEANINGS FROM DATA DICTIONARY:
       - quoteid: Foreign key linking line items to parent quote
       - productidname: Full name of the product or service
       - quantity: Number of units ordered for this line item
       - priceperunit: Unit price before any discounts
       - extendedamount: Total amount for this line item (quantity × unit price)
       - producttypecode: Classification code for product type
       
       NOTE: Tax, discount columns are NOT in current database.
    
    IMPORTANT NOTES:
    - Tax information IS AVAILABLE in salesorder table (totaltax column)
    - The totalamount field contains the complete amount including tax
    - Order ID: Use 'ordernumber' field (e.g., ORD-30741-T8V7)
    - Quote ID: Use 'quotenumber' field for business reference
    - SQLite date functions: strftime('%Y-%m', modifiedon) for year-month
    - Use LIMIT for SQLite (not TOP like SQL Server)
    - All amounts are in REAL (floating point) format
    - JOINs: Can join quote and quotedetail tables on quote.Id = quotedetail.quoteid
    """

def validate_and_fix_sql(sql: str) -> str:
    """Validate and fix common SQL issues"""
    # Remove any markdown formatting
    sql = re.sub(r'```sql?\s*', '', sql)
    sql = re.sub(r'```\s*$', '', sql)
    
    # Fix common issues
    sql = sql.strip()
    
    # Ensure it ends with semicolon
    if not sql.endswith(';'):
        sql += ';'
    
    return sql

def execute_safe_query(conn: sqlite3.Connection, sql: str, limit: int = 1000) -> pd.DataFrame:
    """Execute SQL query with safety checks"""
    try:
        # Add LIMIT if not present (safety measure)
        if 'LIMIT' not in sql.upper():
            sql = sql.rstrip(';') + f' LIMIT {limit};'
        
        # Execute query
        df = pd.read_sql_query(sql, conn)
        return df
    except Exception as e:
        print(f"Query execution error: {e}")
        print(f"SQL: {sql}")
        raise

def process_sqlite_query(query: str) -> Dict[str, Any]:
    """Process natural language query with improved error handling"""
    
    schema_info = get_database_schema()
    
    system_prompt = f"""You are an expert SQLite data analyst. Generate SQL queries and visualizations.

{schema_info}

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON - no explanations before or after
2. Use SQLite syntax (LIMIT not TOP, strftime for dates)
3. Generate 3-5 different chart types
4. Each visualization needs its own optimized SQL query
5. Keep queries efficient with appropriate LIMIT clauses

You MUST return JSON in exactly this format:
{{
    "sql_query": "Main SQL query for the data",
    "answer": "Natural language answer to the question",
    "visualizations": [
        {{
            "type": "bar",
            "title": "Chart Title",
            "sql_for_chart": "SELECT column1, SUM(column2) as value FROM table GROUP BY column1 LIMIT 10",
            "chart_config": {{
                "xAxis": "column1",
                "yAxis": "value",
                "color": "#8884d8"
            }}
        }}
    ],
    "recommendations": ["insight1", "insight2", "insight3"]
}}

Return ONLY the JSON object, nothing else."""
    
    user_prompt = f"Query: {query}\n\nGenerate SQL and visualizations. Return ONLY JSON."
    
    try:
        # Initialize default response
        default_response = {
            'answer': 'Processing your query...',
            'visualizations': [],
            'recommendations': [],
            'sql_query': '',
            'row_count': 0,
            'execution_time': 0
        }
        
        start_time = datetime.now()
        
        # Get LLM response
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}  # Force JSON response
            )
        except Exception as e:
            print(f"GPT-4 failed, trying GPT-3.5: {e}")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",  # Use JSON mode capable model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
        
        # Parse response
        raw_content = response.choices[0].message.content
        print(f"LLM Response length: {len(raw_content)} chars")
        
        # Extract JSON from response
        result = extract_json_from_text(raw_content)
        
        if not result:
            raise ValueError("Could not parse JSON from LLM response")
        
        # Validate required fields
        if 'sql_query' not in result:
            raise ValueError("Missing sql_query in response")
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        
        try:
            # Clean and execute main query
            main_sql = validate_and_fix_sql(result['sql_query'])
            main_df = execute_safe_query(conn, main_sql)
            
            print(f"Main query returned {len(main_df)} rows")
            
            # Process visualizations
            visualizations = []
            for i, viz in enumerate(result.get('visualizations', [])[:5]):  # Limit to 5 charts
                try:
                    if 'sql_for_chart' not in viz:
                        continue
                    
                    # Execute visualization query
                    viz_sql = validate_and_fix_sql(viz['sql_for_chart'])
                    viz_df = execute_safe_query(conn, viz_sql, limit=50)  # Limit chart data
                    
                    print(f"Chart {i+1} query returned {len(viz_df)} rows")
                    
                    # Convert to chart-friendly format
                    chart_data = []
                    for _, row in viz_df.iterrows():
                        item = {}
                        for col, val in row.items():
                            if pd.isna(val):
                                item[col] = None
                            elif isinstance(val, (pd.Timestamp, datetime)):
                                item[col] = str(val)
                            elif isinstance(val, (np.integer, np.floating)):
                                item[col] = float(val)
                            else:
                                item[col] = val
                        chart_data.append(item)
                    
                    # Build visualization object
                    visualization = {
                        'type': viz.get('type', 'bar'),
                        'title': viz.get('title', f'Chart {i+1}'),
                        'data': chart_data,
                        'config': viz.get('chart_config', {
                            'xAxis': viz_df.columns[0] if len(viz_df.columns) > 0 else 'x',
                            'yAxis': viz_df.columns[1] if len(viz_df.columns) > 1 else 'y',
                            'color': viz.get('chart_config', {}).get('color', '#8884d8')
                        })
                    }
                    visualizations.append(visualization)
                    
                except Exception as e:
                    print(f"Error processing visualization {i+1}: {e}")
                    continue
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Format answer with data insights
            answer = result.get('answer', 'Query completed successfully.')
            if len(main_df) > 0:
                if len(main_df) <= 10:
                    # Include actual results for small datasets
                    answer += f"\n\nFound {len(main_df)} results."
                else:
                    answer += f"\n\nFound {len(main_df)} total results (showing top entries)."
            
            # Generate detailed text summary with second LLM call
            text_summary = ""
            if len(main_df) > 0:
                # Convert top rows to JSON for LLM
                data_for_summary = main_df.head(10).to_dict('records')
                
                # Clean up data types for JSON serialization
                for record in data_for_summary:
                    for key, value in record.items():
                        if pd.isna(value):
                            record[key] = None
                        elif isinstance(value, (pd.Timestamp, datetime)):
                            record[key] = str(value)
                        elif isinstance(value, (np.integer, np.floating)):
                            record[key] = float(value)
                
                text_summary_prompt = f"""
                User asked: {query}
                
                The SQL query returned this data (top 10 rows):
                {json.dumps(data_for_summary, indent=2)}
                
                Please format this data into a clear, detailed text summary.
                Include ALL the specific values from the data in a readable list format.
                
                Format guidelines:
                - For orders: "Order ID: [ID] | Customer: [Name] | Amount: $[Amount formatted with commas] | Status: [Code] | Date: [Date]"
                - For products: "Product: [Name] | Quantity: [Qty] | Revenue: $[Amount formatted with commas]"  
                - For customers: "Customer: [Name] | Total: $[Amount formatted with commas] | Orders: [Count]"
                - For time-based data: "Period: [Date/Month] | Value: $[Amount formatted with commas]"
                
                List ALL rows from the data provided, numbered 1, 2, 3, etc.
                Format numbers with commas for thousands (e.g., $1,234,567).
                Be precise and include all data fields available.
                """
                
                try:
                    # Make second LLM call for detailed text formatting
                    text_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a data formatter. Format data into clear, detailed text lists. Include ALL specific values."},
                            {"role": "user", "content": text_summary_prompt}
                        ],
                        temperature=0.1,
                        max_tokens=1500
                    )
                    text_summary = text_response.choices[0].message.content
                    print(f"Generated text summary with {len(text_summary)} characters")
                except Exception as e:
                    print(f"Failed to generate text summary: {e}")
                    text_summary = ""
            
            # Build final response
            return {
                'answer': answer,
                'text_summary': text_summary,  # New field with detailed text data
                'visualizations': visualizations,
                'recommendations': result.get('recommendations', []),
                'sql_query': main_sql,
                'row_count': len(main_df),
                'execution_time': round(execution_time, 2),
                'success': True
            }
            
        finally:
            conn.close()
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error in process_sqlite_query: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'answer': f"I encountered an error processing your query: {error_msg}",
            'visualizations': [],
            'recommendations': [
                "Try rephrasing your question",
                "Use simpler queries like 'Show top 5 customers'",
                "Check if the data exists for your query"
            ],
            'sql_query': '',
            'row_count': 0,
            'execution_time': 0,
            'success': False,
            'error': error_msg
        }

def test_sqlite_connection() -> Dict[str, Any]:
    """Test database connection and return stats"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get table stats
        stats = {}
        tables = ['salesorder', 'quote', 'quotedetail']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = {
                'row_count': count,
                'estimated_size_mb': count * 0.001  # Rough estimate
            }
        
        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0] / (1024 * 1024)  # Convert to MB
        stats['database_size_mb'] = round(db_size, 2)
        
        conn.close()
        
        return {
            'connected': True,
            'stats': stats
        }
        
    except Exception as e:
        return {
            'connected': False,
            'error': str(e)
        }

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    result = test_sqlite_connection()
    if result['connected']:
        return result['stats']
    return {}

# Export the improved processor
process_query = process_sqlite_query