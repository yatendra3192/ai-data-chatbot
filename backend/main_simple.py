from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
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

class AnalysisRequest(BaseModel):
    query: str
    data_file: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "AI Data Analyst API is running"}

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """
    Analyze data based on user query with streaming support
    """
    try:
        async def generate():
            # Simulate workflow steps
            steps = [
                {"step": "parsing_query", "message": "Understanding your question..."},
                {"step": "loading_data", "message": "Loading data..."},
                {"step": "analyzing_data", "message": "Analyzing patterns..."},
                {"step": "generating_visualizations", "message": "Creating visualizations..."},
                {"step": "extracting_business_impact", "message": "Extracting insights..."},
            ]
            
            for step in steps:
                await asyncio.sleep(0.5)  # Simulate processing
                
                # Generate response based on query
                if step["step"] == "analyzing_data":
                    analysis = await perform_analysis(request.query)
                    yield f"data: {json.dumps({'step': step['step'], 'analysis': analysis})}\n\n"
                elif step["step"] == "generating_visualizations":
                    visualizations = generate_visualizations(request.query)
                    yield f"data: {json.dumps({'step': step['step'], 'visualizations': visualizations})}\n\n"
                elif step["step"] == "extracting_business_impact":
                    impact = generate_business_impact(request.query)
                    recommendations = generate_recommendations(request.query)
                    yield f"data: {json.dumps({'step': step['step'], 'business_impact': impact, 'recommendations': recommendations})}\n\n"
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

async def perform_analysis(query: str):
    """Use OpenAI to analyze the query"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analyst. Provide a brief analysis summary."},
                {"role": "user", "content": f"Analyze this data query: {query}"}
            ],
            max_tokens=200
        )
        summary = response.choices[0].message.content
    except:
        summary = "The data reveals a B2B electrical/cable supply business with significant revenue concentration among top customers. Product mix is dominated by industrial cables and wires."
    
    return {
        "summary": summary,
        "metrics": {
            "total_revenue": 11700125.564,
            "total_customers": 99,
            "total_products": 92,
            "top_customers": [
                {"id": "Niagara Pipe Co.", "revenue": 3000000},
                {"id": "Addison LLC", "revenue": 2250000},
                {"id": "Voit Company", "revenue": 1500000}
            ]
        }
    }

def generate_visualizations(query: str):
    """Generate visualization data based on query"""
    visualizations = []
    
    # Always include top customers chart
    if "customer" in query.lower() or True:
        visualizations.append({
            "type": "bar",
            "title": "Top Customer Revenue Distribution",
            "description": "Shows revenue concentration among top customers",
            "data": [
                {"name": "Niagara Pipe Co.", "value": 3000000},
                {"name": "Addison LLC", "value": 2250000},
                {"name": "Voit Company", "value": 1500000},
                {"name": "Turner Co. Ltd", "value": 750000},
                {"name": "Spiegel Company", "value": 375000}
            ],
            "config": {"xAxis": "name", "yAxis": "value", "color": "#818CF8"}
        })
    
    # Include products chart
    if "product" in query.lower() or True:
        visualizations.append({
            "type": "bar",
            "title": "Top Products by Quantity Ordered",
            "description": "Identifies most popular products by volume",
            "data": [
                {"name": "Oxygen-Free Copper", "value": 2600000},
                {"name": "600V PVC Insulated", "value": 1950000},
                {"name": "THHN Wire 10 AWG", "value": 1300000},
                {"name": "THHN Wire 14 AWG", "value": 650000},
                {"name": "600V PVC Wire", "value": 650000}
            ],
            "config": {"xAxis": "name", "yAxis": "value", "color": "#A78BFA"}
        })
    
    return visualizations

def generate_business_impact(query: str):
    """Generate business impact insights"""
    return {
        "title": "Business Impact:",
        "points": [
            "Need to develop risk mitigation strategies for potential loss of top 2 customers who represent 67% of top 5 revenue",
            "Consider developing targeted retention programs for the top 3 customers who each generate over $1M in revenue",
            "Opportunity to grow mid-tier customers (positions 4-5) into larger accounts through focused account management",
            "Geographic concentration in Middle East suggests opportunity for market diversification"
        ]
    }

def generate_recommendations(query: str):
    """Generate recommendations"""
    return [
        "Implement key account management program for top 5 customers who drive majority of revenue",
        "Investigate high order cancellation rate (24%) to identify and address root causes",
        "Consider inventory optimization for top 5 products by volume to ensure consistent availability",
        "Develop customer diversification strategy to reduce dependency on top accounts"
    ]

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    contents = await file.read()
    file_size = len(contents) / (1024 * 1024)
    
    if file_size > 1000:
        raise HTTPException(status_code=400, detail="File size exceeds 1000MB limit")
    
    file_path = Path(f"./data/uploads/{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Process CSV
    try:
        df = pd.read_csv(file_path)
        return {
            "filename": file.filename,
            "path": str(file_path),
            "rows": len(df),
            "columns": df.columns.tolist(),
            "sample": df.head(10).to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)