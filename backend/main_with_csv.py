from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import json
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Data Analyst API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create necessary directories
Path("./data/uploads").mkdir(parents=True, exist_ok=True)
Path("./data/cache").mkdir(parents=True, exist_ok=True)

# Global variable to store loaded data
loaded_data = None
data_stats = None

def load_salesorder_csv():
    """Load the salesorder.csv file at startup"""
    global loaded_data, data_stats
    csv_path = Path("./data/uploads/salesorder.csv")
    
    if csv_path.exists():
        print(f"Loading {csv_path}...")
        try:
            # Load with sample for large files
            loaded_data = pd.read_csv(csv_path, nrows=100000)  # Load first 100k rows for performance
            
            # Calculate statistics
            data_stats = {
                "total_rows": len(loaded_data),
                "columns": loaded_data.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in loaded_data.dtypes.items()},
                "numeric_columns": loaded_data.select_dtypes(include=[np.number]).columns.tolist(),
                "text_columns": loaded_data.select_dtypes(include=['object']).columns.tolist()
            }
            
            print(f"Loaded {len(loaded_data)} rows with columns: {data_stats['columns']}")
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    return False

# Load data at startup
print("Attempting to load salesorder.csv...")
result = load_salesorder_csv()
print(f"Load result: {result}")

class AnalysisRequest(BaseModel):
    query: str
    data_file: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "AI Data Analyst API is running", "data_loaded": loaded_data is not None}

@app.get("/api/data-info")
async def get_data_info():
    """Get information about loaded data"""
    if loaded_data is None:
        return {"error": "No data loaded"}
    
    # Replace NaN values with None for JSON serialization
    sample_data = loaded_data.head(5).fillna(0).to_dict('records')
    
    return {
        "loaded": True,
        "stats": data_stats,
        "sample": sample_data
    }

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Analyze data based on user query with streaming support"""
    try:
        async def generate():
            # Use actual data if loaded
            use_real_data = loaded_data is not None
            
            steps = [
                {"step": "parsing_query", "message": "Understanding your question..."},
                {"step": "loading_data", "message": "Loading salesorder.csv data..." if use_real_data else "Loading sample data..."},
                {"step": "analyzing_data", "message": "Analyzing patterns..."},
                {"step": "generating_visualizations", "message": "Creating visualizations..."},
                {"step": "extracting_business_impact", "message": "Extracting insights..."},
            ]
            
            for step in steps:
                await asyncio.sleep(0.5)
                
                if step["step"] == "analyzing_data":
                    analysis = await perform_analysis_with_data(request.query)
                    yield f"data: {json.dumps({'step': step['step'], 'analysis': analysis})}\n\n"
                elif step["step"] == "generating_visualizations":
                    visualizations = generate_visualizations_from_data(request.query)
                    print(f"[STREAMING] About to send {len(visualizations)} visualizations to frontend")
                    stream_data = {'step': step['step'], 'visualizations': visualizations}
                    stream_json = json.dumps(stream_data)
                    print(f"[STREAMING] JSON size: {len(stream_json)} bytes")
                    yield f"data: {stream_json}\n\n"
                elif step["step"] == "extracting_business_impact":
                    # Skip business impact, just send recommendations
                    recommendations = generate_recommendations_from_data(request.query)
                    yield f"data: {json.dumps({'step': step['step'], 'recommendations': recommendations})}\n\n"
                else:
                    yield f"data: {json.dumps(step)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def perform_analysis_with_data(query: str):
    """Analyze using actual data"""
    global loaded_data
    
    if loaded_data is not None:
        # Use intelligent query processor with LLM
        from intelligent_query_processor import process_data_query
        query_result = process_data_query(query, loaded_data)
        
        if "answer" in query_result:
            # Return the direct query result
            return {
                "summary": query_result["answer"],
                "metrics": query_result.get("metrics", {})
            }
        
        # Fallback to AI analysis if no direct answer
        # Analyze real data
        numeric_cols = loaded_data.select_dtypes(include=[np.number]).columns
        
        # Calculate real statistics
        stats = {}
        for col in numeric_cols[:5]:  # Top 5 numeric columns
            stats[col] = {
                "mean": float(loaded_data[col].mean()),
                "sum": float(loaded_data[col].sum()),
                "max": float(loaded_data[col].max()),
                "min": float(loaded_data[col].min())
            }
        
        # Use OpenAI to generate insights
        try:
            data_context = f"Data has {len(loaded_data)} rows, columns: {', '.join(loaded_data.columns[:10])}. Sample stats: {stats}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data analyst. Analyze the data and provide insights."},
                    {"role": "user", "content": f"Query: {query}\n\nData context: {data_context}"}
                ],
                max_tokens=300
            )
            summary = response.choices[0].message.content
        except:
            summary = f"Analyzed {len(loaded_data)} sales orders. The data contains {len(loaded_data.columns)} columns including order details, customer information, and financial metrics."
        
        return {
            "summary": summary,
            "metrics": {
                "total_rows": len(loaded_data),
                "total_columns": len(loaded_data.columns),
                "numeric_columns": len(numeric_cols),
                "statistics": stats
            }
        }
    else:
        # Fallback to default
        return {
            "summary": "Sales order data analysis pending. Please ensure the CSV file is loaded.",
            "metrics": {
                "total_revenue": 11700125.564,
                "total_customers": 99,
                "total_products": 92
            }
        }

def generate_visualizations_from_data(query: str):
    """Generate visualizations from actual data"""
    global loaded_data
    visualizations = []
    
    if loaded_data is not None:
        # First try to get query-specific visualizations
        from intelligent_query_processor import process_data_query
        query_result = process_data_query(query, loaded_data)
        
        # Handle both single and multiple visualizations
        if "visualizations" in query_result:
            # Multiple visualizations returned
            visualizations.extend(query_result["visualizations"])
        elif "visualization" in query_result:
            # Single visualization returned
            visualizations.append(query_result["visualization"])
        
        # Convert any non-serializable objects to strings
        for viz in visualizations:
            if 'data' in viz:
                for item in viz['data']:
                    for key, value in item.items():
                        # Convert Timestamp, Period, or other non-serializable types to string
                        if hasattr(value, 'isoformat'):
                            item[key] = value.isoformat()
                        elif not isinstance(value, (str, int, float, bool, type(None))):
                            item[key] = str(value)
        
        # Return all visualizations if we have any
        if visualizations:
            print(f"Returning {len(visualizations)} visualizations from query")
            return visualizations
        
        # Default visualizations if no query-specific ones
        # Generate real visualizations from your sales data
        
        # 1. Top customers by totalamount
        if 'customeridname' in loaded_data.columns and 'totalamount' in loaded_data.columns:
            # Filter out null values and get top customers
            customer_data = loaded_data[loaded_data['customeridname'].notna() & loaded_data['totalamount'].notna()]
            top_customers = customer_data.groupby('customeridname')['totalamount'].sum().nlargest(5)
            
            visualizations.append({
                "type": "bar",
                "title": "Top Customer Revenue Distribution",
                "description": "Shows revenue concentration among top customers to identify key accounts",
                "data": [
                    {"name": str(name)[:30] if len(str(name)) > 30 else str(name), 
                     "value": float(value)}
                    for name, value in top_customers.items()
                ],
                "config": {"xAxis": "name", "yAxis": "value", "color": "#818CF8"}
            })
        
        # 2. Order status distribution
        if 'statuscode' in loaded_data.columns:
            status_counts = loaded_data['statuscode'].value_counts().head(5)
            status_map = {1: 'Active', 2: 'Submitted', 3: 'Canceled', 4: 'Fulfilled', 100: 'Invoiced'}
            
            visualizations.append({
                "type": "bar",
                "title": "Order Status Distribution",
                "description": "Distribution of order statuses",
                "data": [
                    {"name": status_map.get(int(status), f"Status {status}"), 
                     "value": int(count)}
                    for status, count in status_counts.items()
                ],
                "config": {"xAxis": "name", "yAxis": "value", "color": "#A78BFA"}
            })
        
        # Add numeric column distribution
        numeric_cols = loaded_data.select_dtypes(include=[np.number]).columns[:2]
        for col in numeric_cols:
            if col in loaded_data.columns:
                # Create histogram data
                hist, bins = np.histogram(loaded_data[col].dropna(), bins=5)
                
                visualizations.append({
                    "type": "bar",
                    "title": f"{col} Distribution",
                    "description": f"Distribution of {col} values",
                    "data": [
                        {"name": f"{bins[i]:.0f}-{bins[i+1]:.0f}", "value": int(hist[i])}
                        for i in range(len(hist))
                    ],
                    "config": {"xAxis": "name", "yAxis": "value", "color": "#A78BFA"}
                })
                break
    
    # Fallback to default if no data
    if not visualizations:
        visualizations = [
            {
                "type": "bar",
                "title": "Data Analysis Pending",
                "description": "Load your sales order data to see visualizations",
                "data": [
                    {"name": "Sample 1", "value": 3000000},
                    {"name": "Sample 2", "value": 2250000},
                    {"name": "Sample 3", "value": 1500000},
                    {"name": "Sample 4", "value": 750000},
                    {"name": "Sample 5", "value": 375000}
                ],
                "config": {"xAxis": "name", "yAxis": "value", "color": "#818CF8"}
            }
        ]
    
    return visualizations

def generate_business_impact_from_data(query: str):
    """Generate business impact from actual data"""
    global loaded_data
    
    if loaded_data is not None:
        points = []
        
        # Analyze customer concentration
        if 'customeridname' in loaded_data.columns and 'totalamount' in loaded_data.columns:
            customer_data = loaded_data[loaded_data['customeridname'].notna() & loaded_data['totalamount'].notna()]
            top_5_customers = customer_data.groupby('customeridname')['totalamount'].sum().nlargest(5)
            total_revenue = customer_data['totalamount'].sum()
            top_5_revenue_pct = (top_5_customers.sum() / total_revenue * 100) if total_revenue > 0 else 0
            
            if top_5_revenue_pct > 20:
                points.append(f"Top 5 customers represent {top_5_revenue_pct:.1f}% of total revenue - high customer concentration risk")
            
            # Specific customer insights
            top_customer = top_5_customers.index[0] if len(top_5_customers) > 0 else "Unknown"
            top_customer_pct = (top_5_customers.iloc[0] / total_revenue * 100) if len(top_5_customers) > 0 and total_revenue > 0 else 0
            if top_customer_pct > 10:
                points.append(f"{top_customer} alone accounts for {top_customer_pct:.1f}% of revenue - critical account to retain")
        
        # Analyze order fulfillment
        if 'statuscode' in loaded_data.columns:
            status_counts = loaded_data['statuscode'].value_counts()
            total_orders = len(loaded_data)
            if 3 in status_counts:  # Canceled status
                cancel_rate = status_counts[3] / total_orders * 100
                if cancel_rate > 5:
                    points.append(f"Order cancellation rate of {cancel_rate:.1f}% needs investigation to reduce revenue loss")
        
        # Add revenue insights
        if 'totalamount' in loaded_data.columns:
            avg_order_value = loaded_data['totalamount'].mean()
            points.append(f"Average order value of ${avg_order_value:,.2f} - focus on upselling to increase AOV")
        
        return {
            "title": "Business Impact:",
            "points": points[:4] if points else [
                "Analyzing 60,481 sales orders for insights",
                "Focus on customer retention for top accounts",
                "Optimize order fulfillment to reduce cancellations",
                "Identify cross-selling opportunities"
            ]
        }
    
    return {
        "title": "Business Impact:",
        "points": [
            "Sales order data loaded and ready for analysis",
            "Use natural language queries to explore your data",
            "AI will generate insights based on patterns in your data",
            "Charts will update dynamically based on your questions"
        ]
    }

def generate_recommendations_from_data(query: str):
    """Generate recommendations from actual data"""
    global loaded_data
    
    if loaded_data is not None:
        # Use intelligent query processor to get context-aware recommendations
        from intelligent_query_processor import analyze_query_with_llm
        
        try:
            # Get query-specific analysis
            query_result = analyze_query_with_llm(query, loaded_data)
            
            # Extract recommendations if available
            if "recommendations" in query_result:
                return query_result["recommendations"][:4]
            
            # Generate context-aware recommendations based on the query
            recommendations = []
            query_lower = query.lower()
            
            # Customer-related queries
            if any(word in query_lower for word in ['customer', 'client', 'buyer']):
                if 'owner' in query_lower or 'ownerid' in query_lower:
                    recommendations.extend([
                        "Analyze owner performance metrics to identify top performers",
                        "Consider implementing owner-based sales incentives",
                        "Review owner assignment distribution for workload balance",
                        "Track owner conversion rates and customer satisfaction"
                    ])
                else:
                    recommendations.extend([
                        "Focus retention efforts on high-value customers",
                        "Analyze customer purchase patterns for upselling opportunities",
                        "Segment customers by value for targeted marketing",
                        "Monitor customer churn indicators"
                    ])
            
            # Revenue/sales queries
            elif any(word in query_lower for word in ['revenue', 'sales', 'amount', 'value']):
                recommendations.extend([
                    "Identify seasonal trends in revenue patterns",
                    "Analyze product mix contribution to revenue",
                    "Focus on high-margin products and services",
                    "Optimize pricing strategies based on sales data"
                ])
            
            # Order/status queries
            elif any(word in query_lower for word in ['order', 'status', 'fulfillment']):
                recommendations.extend([
                    "Optimize order processing workflow",
                    "Reduce order cancellation rates",
                    "Improve fulfillment time metrics",
                    "Implement automated status tracking"
                ])
            
            # Product queries
            elif any(word in query_lower for word in ['product', 'item', 'sku']):
                recommendations.extend([
                    "Analyze product performance by region",
                    "Identify slow-moving inventory",
                    "Optimize product bundling strategies",
                    "Review product profitability margins"
                ])
            
            # Time-based queries
            elif any(word in query_lower for word in ['trend', 'monthly', 'yearly', 'time', 'date']):
                recommendations.extend([
                    "Implement predictive analytics for forecasting",
                    "Identify cyclical patterns in the data",
                    "Set up automated trend monitoring",
                    "Compare year-over-year performance metrics"
                ])
            
            # Default intelligent recommendations based on data
            else:
                numeric_cols = loaded_data.select_dtypes(include=[np.number]).columns
                recommendations.extend([
                    f"Explore relationships between {len(numeric_cols)} numeric variables",
                    "Use clustering to identify natural groupings in data",
                    "Implement anomaly detection for quality control",
                    "Create predictive models for business forecasting"
                ])
            
            return recommendations[:4]
            
        except Exception as e:
            # Fallback to basic recommendations
            return [
                "Perform comprehensive data quality assessment",
                "Identify key performance indicators in your data",
                "Explore correlations between business metrics",
                "Set up automated reporting dashboards"
            ]
    
    return [
        "Load your sales data to begin analysis",
        "Ask specific questions about your business metrics",
        "Explore customer and product insights",
        "Identify trends and optimization opportunities"
    ]

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file"""
    global loaded_data, data_stats
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    contents = await file.read()
    file_size = len(contents) / (1024 * 1024)
    
    if file_size > 1000:
        raise HTTPException(status_code=400, detail="File size exceeds 1000MB limit")
    
    file_path = Path(f"./data/uploads/{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Load the new file
    try:
        loaded_data = pd.read_csv(file_path, nrows=100000)  # Load first 100k rows
        data_stats = {
            "total_rows": len(loaded_data),
            "columns": loaded_data.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in loaded_data.dtypes.items()}
        }
        
        return {
            "filename": file.filename,
            "path": str(file_path),
            "rows": len(loaded_data),
            "columns": loaded_data.columns.tolist(),
            "sample": loaded_data.head(10).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "data_loaded": loaded_data is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)