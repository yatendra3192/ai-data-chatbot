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

# Data dictionary mappings for salesorder table
STATUS_CODE_MAPPING = {
    0: "New", 1: "In Progress", 2: "Pending", 3: "Complete", 4: "Partial",
    5: "Invoiced", 6: "Cancelled", 7: "Active", 8: "Confirmed",
    9: "Packing Slip", 10: "Picked", 11: "Partially Picked",
    12: "Partially Packed", 13: "Shipped", 14: "Partially Shipped",
    15: "Partially Invoiced", 16: "Draft"
}

STATE_CODE_MAPPING = {
    0: "Active", 1: "Closed", 2: "Draft", 4: "On Hold"
}

PRIORITY_CODE_MAPPING = {
    0: "Low", 1: "Normal", 2: "High", 3: "Urgent"
}

SHIPPING_METHOD_MAPPING = {
    0: "Air", 1: "Road", 2: "Sea", 3: "UPS", 4: "Postal Mail",
    5: "Full Load", 6: "Will Call", 7: "NA"
}

# Quote table mappings
QUOTE_STATE_MAPPING = {
    0: "Draft", 1: "Active", 2: "In Review", 3: "Won", 4: "Lost", 5: "Closed"
}

QUOTE_STATUS_MAPPING = {
    0: "New", 1: "In Progress", 2: "Submitted", 3: "Revised",
    4: "Accepted", 5: "Cancelled", 6: "Closed"
}

QUOTE_APPROVAL_MAPPING = {
    0: "Pending", 1: "Approved", 2: "Rejected"
}

PROBABILITY_MAPPING = {
    0: "Low", 1: "Medium", 2: "High"
}

FEASIBLE_MAPPING = {
    0: "No", 1: "Yes"
}

FREIGHT_TERMS_MAPPING = {
    0: "FOB", 1: "CIF", 2: "EXW"
}

PAYMENT_TERMS_MAPPING = {
    0: "Net 30", 1: "Net 60", 2: "Due on Receipt"
}

ORDER_TYPE_MAPPING = {
    0: "Standard", 1: "Return", 2: "Service"
}

PROFITABILITY_MAPPING = {
    0: "Not Profitable", 1: "Profitable"
}

QUOTE_SHIPPING_METHOD_MAPPING = {
    0: "Air", 1: "Road", 2: "Sea", 3: "Courier"
}

def get_database_schema():
    """Get the database schema for the LLM context"""
    return """
    Database Schema (SQLite):
    
    CRITICAL: The shippingmethodcode column EXISTS in salesorder table! Use it directly!
    
    1. salesorder table (60,481 rows) - DETAILED COLUMN DICTIONARY:
       Core Fields:
       - Id (TEXT PRIMARY KEY): Sales Order ID
       - ordernumber: Order Number (unique identifier)
       - name: Order Name/Description
       - description: Order Description
       
       Status Fields (IMPORTANT - Use these mappings):
       - statecode: Order State (0=Active, 1=Closed, 2=Draft, 4=On hold)
       - statuscode: Order Status
         * 0=New, 1=In Progress, 2=Pending, 3=Complete, 4=Partial
         * 5=Invoiced, 6=Cancelled, 7=Active, 8=Confirmed
         * 9=Packing Slip, 10=Picked, 11=Partially Picked
         * 12=Partially Packed, 13=Shipped, 14=Partially Shipped
         * 15=Partially Invoiced, 16=Draft
       
       Customer Information:
       - customerid: Customer ID
       - customeridname: Customer Name (use this for customer analysis)
       - eht_custponumber: Customer PO Number
       - new_customerreferenceorder: Customer Reference Order
       
       Financial Fields:
       - totalamount: Total Order Amount
       - totalamount_base: Total Amount (Base Currency)
       - totallineitemamount: Total Line Item Amount
       
       Shipping Information (IMPORTANT - Column exists!):
       - shippingmethodcode: Shipping Method Code
         * 0=Air, 1=Road, 2=Sea, 3=UPS, 4=Postal Mail
         * 5=Full Load, 6=Will Call, 7=NA
         USE THIS COLUMN DIRECTLY - DO NOT use CASE statements to simulate it!
       - totaldiscountamount: Total Discount Amount
       - totaltax: Total Tax
       - totalamountlessfreight: Total Amount Less Freight
       
       Shipping Information:
       - shippingmethodcode: Shipping Method (0=Air, 1=Road, 2=Sea, 3=UPS, 4=Postal Mail, 5=Full Load, 6=Will Call, 7=NA)
       - shipto_city: Shipping City
       - shipto_country: Shipping Country
       - shipto_stateorprovince: Shipping State/Province
       - shipto_postalcode: Shipping Postal Code
       - requestdeliveryby: Requested Delivery Date
       
       Billing Information:
       - billto_city: Billing City
       - billto_country: Billing Country
       - billto_postalcode: Billing Postal Code
       
       Order Details:
       - prioritycode: Order Priority (0=Low, 1=Normal, 2=High, 3=Urgent)
       - quoteid: Related Quote ID
       - quoteidname: Related Quote Name
       - opportunityid: Related Opportunity ID
       - opportunityidname: Related Opportunity Name
       
       Dates:
       - modifiedon: Last Modified Date
       - SinkCreatedOn: Record Created Date
       - SinkModifiedOn: Record Modified Date
       
       Other Important Fields:
       - eht_projectname: Project Name
       - exchangerate: Exchange Rate
       - transactioncurrencyidname: Transaction Currency Name
    
    2. quote table (141,461 rows) - DETAILED COLUMN DICTIONARY:
       Core Fields:
       - Id (TEXT PRIMARY KEY): Quote Record ID
       - quotenumber: Quote Number (unique identifier)
       - name: Quote Name
       - description: Quote Description
       - quoteid: Quote ID
       
       Status Fields (IMPORTANT - Use these mappings):
       - statecode: Quote State
         * 0=Draft, 1=Active, 2=In Review, 3=Won, 4=Lost, 5=Closed
       - statuscode: Quote Status
         * 0=New, 1=In Progress, 2=Submitted, 3=Revised
         * 4=Accepted, 5=Cancelled, 6=Closed
       
       Customer Information:
       - customerid: Customer ID
       - customeridname: Customer Name (use this for customer analysis)
       - new_customerreference: Customer Reference
       - eht_custponumber: Customer PO Number
       
       Financial Fields:
       - totalamount: Total Quote Amount
       - totalamount_base: Total Amount (Base Currency)
       - totallineitemamount: Total Line Item Amount
       - totaldiscountamount: Total Discount Amount
       - totaltax: Total Tax
       - totalamountlessfreight: Total Amount Less Freight
       - ehe_totalcost: Total Cost
       - ehe_totalmargin: Total Margin
       - msdyn_grossmargin: Gross Margin
       - msdyn_estimatedquotemargin: Estimated Quote Margin
       
       Approval & Probability Fields:
       - ehe_quoteapprovalstatus: Quote Approval Status (0=Pending, 1=Approved, 2=Rejected)
       - ehe_brandmanagerapprovalstatus: Brand Manager Approval (0=Pending, 1=Approved, 2=Rejected)
       - eht_probability: Probability (0=Low, 1=Medium, 2=High)
       - msdyn_feasible: Feasibility Status (0=No, 1=Yes)
       
       Shipping & Terms:
       - shippingmethodcode: Shipping Method (0=Air, 1=Road, 2=Sea, 3=Courier)
       - freighttermscode: Freight Terms (0=FOB, 1=CIF, 2=EXW)
       - paymenttermscode: Payment Terms (0=Net 30, 1=Net 60, 2=Due on Receipt)
       - shipto_city: Shipping City
       - ehe_shiptocity: Shipping City (EHE)
       - ehe_billtocountry: Billing Country
       - ehe_shiptpcountry: Shipping Country
       - willcall: Will Call (0=No, 1=Yes)
       
       Business Fields:
       - msdyn_ordertype: Order Type (0=Standard, 1=Return, 2=Service)
       - msdyn_profitability: Profitability (0=Not Profitable, 1=Profitable)
       - ehe_closeaswon: Close as Won (0=No, 1=Yes)
       - opportunityid: Related Opportunity ID
       - opportunityidname: Related Opportunity Name
       
       Dates:
       - modifiedon: Last Modified Date
       - closedon: Closed On Date
       - effectivefrom: Effective From Date
       - effectiveto: Effective To Date
       - requestdeliveryby: Requested Delivery Date
       - new_expectedclosedata: Expected Close Date
       - SinkCreatedOn: Record Created Date
       - SinkModifiedOn: Record Modified Date
       
       Other Important Fields:
       - eht_projectname: Project Name
       - owneridname: Owner Name
       - exchangerate: Exchange Rate
       - transactioncurrencyidname: Transaction Currency Name
       - revisionnumber: Revision Number
    
    3. quotedetail table (1,237,446 rows):
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
    
    IMPORTANT Query Guidelines:
    - When asked about order status, use the statuscode mappings above
    - For customer analysis, use customeridname field
    - For financial analysis, use totalamount field
    - For shipping analysis, use shippingmethodcode with mappings
    - For priority analysis, use prioritycode with mappings
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
9. IMPORTANT: Your answer MUST include the actual names/values from query results
10. USE CASE statements to decode status/priority codes for human-readable output:
    Example: CASE statuscode 
             WHEN 0 THEN 'New' 
             WHEN 1 THEN 'In Progress' 
             WHEN 3 THEN 'Complete'
             WHEN 6 THEN 'Cancelled' 
             ELSE 'Other' END as status_name
11. For shipping method analysis, use this EXACT pattern:
    CORRECT: SELECT 
               CASE shippingmethodcode 
                 WHEN 0 THEN 'Air' WHEN 1 THEN 'Road' WHEN 2 THEN 'Sea' 
                 WHEN 3 THEN 'UPS' WHEN 4 THEN 'Postal Mail' WHEN 5 THEN 'Full Load'
                 WHEN 6 THEN 'Will Call' WHEN 7 THEN 'NA' ELSE 'Unknown'
               END as shipping_method,
               COUNT(*) as count
             FROM salesorder 
             GROUP BY shippingmethodcode
    WRONG: Creating CTEs with VALUES clauses or complex JOINs
12. The shippingmethodcode column EXISTS! Never try to work around it!
13. For Quote table analysis, use appropriate CASE statements:
    - Quote State: CASE statecode WHEN 0 THEN 'Draft' WHEN 1 THEN 'Active' WHEN 2 THEN 'In Review' WHEN 3 THEN 'Won' WHEN 4 THEN 'Lost' WHEN 5 THEN 'Closed' END
    - Quote Status: CASE statuscode WHEN 0 THEN 'New' WHEN 1 THEN 'In Progress' WHEN 2 THEN 'Submitted' WHEN 3 THEN 'Revised' WHEN 4 THEN 'Accepted' WHEN 5 THEN 'Cancelled' WHEN 6 THEN 'Closed' END
    - Approval Status: CASE ehe_quoteapprovalstatus WHEN 0 THEN 'Pending' WHEN 1 THEN 'Approved' WHEN 2 THEN 'Rejected' END
    - Probability: CASE eht_probability WHEN 0 THEN 'Low' WHEN 1 THEN 'Medium' WHEN 2 THEN 'High' END
    - Profitability: CASE msdyn_profitability WHEN 0 THEN 'Not Profitable' WHEN 1 THEN 'Profitable' END

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
                chart_sql = viz.get('sql_for_chart', '')
                print(f"[CHART SQL] Executing: {chart_sql}")
                
                # Check if the SQL query is valid
                if not chart_sql or chart_sql.strip() == '':
                    print(f"[WARNING] Empty chart SQL for visualization: {viz.get('title', 'Unknown')}")
                    continue
                    
                viz_df = pd.read_sql_query(chart_sql, conn)
                print(f"[CHART SQL] Got {len(viz_df)} rows for chart: {viz.get('title', 'Unknown')}")
                
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
                print(f"[ERROR] Error executing chart SQL for '{viz.get('title', 'Unknown')}': {e}")
                print(f"[ERROR] Failed SQL was: {viz.get('sql_for_chart', 'No SQL provided')}")
                # Continue with other visualizations instead of failing completely
                continue
        
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
        print(f"Recommendations: {result['recommendations']}")# Trigger reload

 
