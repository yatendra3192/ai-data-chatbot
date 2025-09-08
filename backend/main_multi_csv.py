from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json
import asyncio
from typing import Optional, Dict, Any
import os
from datetime import datetime

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    query: str
    data_file: Optional[str] = None
    datasets: Optional[list] = None  # Allow specifying which datasets to query

# Global variables for loaded data
loaded_datasets = {}
data_stats = {}

def load_csv_efficiently(file_path: str, name: str, row_limit: int = 100000):
    """Load CSV with memory optimization for large files"""
    try:
        print(f"Loading {name} from {file_path}...")
        
        # First, get the total number of rows
        total_rows = sum(1 for line in open(file_path, 'r', encoding='utf-8', errors='ignore')) - 1
        
        if total_rows > row_limit:
            print(f"{name}: {total_rows} rows found, loading first {row_limit} rows for performance")
            df = pd.read_csv(file_path, nrows=row_limit, low_memory=False)
        else:
            df = pd.read_csv(file_path, low_memory=False)
        
        print(f"Loaded {len(df)} rows from {name}")
        return df, total_rows
    except Exception as e:
        print(f"Error loading {name}: {e}")
        return None, 0

# Load all datasets on startup
@app.on_event("startup")
async def startup_event():
    """Load all CRM CSV files on startup"""
    global loaded_datasets, data_stats
    
    datasets_config = {
        'salesorder': r"C:\Users\User\Documents\DVwithCC\salesorder.csv",
        'quote': r"C:\Users\User\Documents\DVwithCC\Quote.csv",
        'quotedetail': r"C:\Users\User\Documents\DVwithCC\quotedetail.csv"
    }
    
    for name, path in datasets_config.items():
        if os.path.exists(path):
            df, total_rows = load_csv_efficiently(path, name)
            if df is not None:
                loaded_datasets[name] = df
                
                # Calculate stats for each dataset
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                data_stats[name] = {
                    'loaded_rows': len(df),
                    'total_rows': total_rows,
                    'columns': len(df.columns),
                    'numeric_columns': len(numeric_cols),
                    'column_names': list(df.columns)[:20],  # First 20 columns
                    'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
                }
        else:
            print(f"Warning: {name} file not found at {path}")
    
    print(f"\nLoaded datasets: {list(loaded_datasets.keys())}")
    print(f"Total memory usage: {sum(df.memory_usage(deep=True).sum() for df in loaded_datasets.values()) / 1024**2:.2f} MB")

@app.get("/")
def read_root():
    return {"message": "Multi-CSV Data Analysis API", "datasets": list(loaded_datasets.keys())}

@app.get("/api/datasets-info")
async def get_datasets_info():
    """Get information about all loaded datasets"""
    return {
        "loaded": len(loaded_datasets) > 0,
        "datasets": data_stats,
        "available_for_analysis": list(loaded_datasets.keys())
    }

@app.post("/api/analyze")
async def analyze_data(request: AnalysisRequest):
    """Analyze data across multiple datasets with streaming support"""
    try:
        async def generate():
            # Determine which datasets to use
            if request.datasets:
                datasets_to_use = {k: v for k, v in loaded_datasets.items() if k in request.datasets}
            else:
                # Use all loaded datasets by default
                datasets_to_use = loaded_datasets
            
            if not datasets_to_use:
                yield f"data: {json.dumps({'error': 'No datasets available'})}\n\n"
                return
            
            steps = [
                {"step": "parsing_query", "message": "Understanding your question..."},
                {"step": "loading_data", "message": f"Analyzing {len(datasets_to_use)} dataset(s): {', '.join(datasets_to_use.keys())}..."},
                {"step": "analyzing_data", "message": "Processing data patterns..."},
                {"step": "generating_visualizations", "message": "Creating visualizations..."},
                {"step": "extracting_insights", "message": "Generating recommendations..."},
            ]
            
            for step in steps:
                await asyncio.sleep(0.5)
                
                if step["step"] == "analyzing_data":
                    analysis = await perform_multi_dataset_analysis(request.query, datasets_to_use)
                    yield f"data: {json.dumps({'step': step['step'], 'analysis': analysis})}\n\n"
                elif step["step"] == "generating_visualizations":
                    visualizations = generate_visualizations_from_datasets(request.query, datasets_to_use)
                    print(f"[STREAMING] Sending {len(visualizations)} visualizations")
                    yield f"data: {json.dumps({'step': step['step'], 'visualizations': visualizations})}\n\n"
                elif step["step"] == "extracting_insights":
                    recommendations = generate_recommendations_from_datasets(request.query, datasets_to_use)
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

async def perform_multi_dataset_analysis(query: str, datasets: Dict[str, pd.DataFrame]):
    """Analyze across multiple datasets"""
    from intelligent_query_processor import process_data_query
    
    # Determine which dataset is most relevant for the query
    query_lower = query.lower()
    
    # Smart dataset selection based on query keywords
    if 'quote' in query_lower and 'detail' in query_lower and 'quotedetail' in datasets:
        primary_dataset = datasets['quotedetail']
        dataset_name = 'quotedetail'
    elif 'quote' in query_lower and 'quote' in datasets:
        primary_dataset = datasets['quote']
        dataset_name = 'quote'
    elif 'order' in query_lower and 'salesorder' in datasets:
        primary_dataset = datasets['salesorder']
        dataset_name = 'salesorder'
    else:
        # Use the largest dataset as primary
        primary_dataset = max(datasets.values(), key=len)
        dataset_name = [k for k, v in datasets.items() if v is primary_dataset][0]
    
    # Process query with the primary dataset
    query_result = process_data_query(query, primary_dataset)
    
    if "answer" in query_result:
        # Add context about which dataset was used
        answer = query_result["answer"]
        answer += f"\n\n(Analysis based on {dataset_name} dataset with {len(primary_dataset):,} records)"
        
        return {
            "summary": answer,
            "dataset_used": dataset_name,
            "metrics": query_result.get("metrics", {}),
            "available_datasets": list(datasets.keys())
        }
    
    # Fallback analysis
    return {
        "summary": f"Analyzed {len(datasets)} datasets with {sum(len(df) for df in datasets.values()):,} total records",
        "datasets_info": {name: f"{len(df):,} records" for name, df in datasets.items()},
        "metrics": {}
    }

def generate_visualizations_from_datasets(query: str, datasets: Dict[str, pd.DataFrame]):
    """Generate visualizations from the most relevant dataset"""
    from intelligent_query_processor import process_data_query
    
    # Determine primary dataset
    query_lower = query.lower()
    if 'quote' in query_lower and 'detail' in query_lower and 'quotedetail' in datasets:
        primary_dataset = datasets['quotedetail']
    elif 'quote' in query_lower and 'quote' in datasets:
        primary_dataset = datasets['quote']
    elif 'order' in query_lower and 'salesorder' in datasets:
        primary_dataset = datasets['salesorder']
    else:
        primary_dataset = max(datasets.values(), key=len)
    
    # Get visualizations from query processor
    query_result = process_data_query(query, primary_dataset)
    
    visualizations = []
    if "visualizations" in query_result:
        visualizations = query_result["visualizations"]
    elif "visualization" in query_result:
        visualizations = [query_result["visualization"]]
    
    # Clean up any non-serializable data
    for viz in visualizations:
        if 'data' in viz:
            for item in viz['data']:
                for key, value in item.items():
                    if hasattr(value, 'isoformat'):
                        item[key] = value.isoformat()
                    elif pd.isna(value):
                        item[key] = None
                    elif not isinstance(value, (str, int, float, bool, type(None))):
                        item[key] = str(value)
    
    return visualizations

def generate_recommendations_from_datasets(query: str, datasets: Dict[str, pd.DataFrame]):
    """Generate intelligent recommendations based on multi-dataset analysis"""
    from intelligent_query_processor import process_data_query
    
    # Get the primary dataset
    query_lower = query.lower()
    if 'quote' in query_lower and 'detail' in query_lower and 'quotedetail' in datasets:
        primary_dataset = datasets['quotedetail']
        dataset_name = 'Quote Details'
    elif 'quote' in query_lower and 'quote' in datasets:
        primary_dataset = datasets['quote']
        dataset_name = 'Quotes'
    elif 'order' in query_lower and 'salesorder' in datasets:
        primary_dataset = datasets['salesorder']
        dataset_name = 'Sales Orders'
    else:
        primary_dataset = max(datasets.values(), key=len)
        dataset_name = 'Combined Data'
    
    query_result = process_data_query(query, primary_dataset)
    
    if "recommendations" in query_result:
        return query_result["recommendations"]
    
    # Generate context-aware recommendations
    recommendations = []
    
    # Add dataset-specific insights
    if len(datasets) > 1:
        recommendations.append(f"💡 Analyzing {dataset_name} from {len(datasets)} available datasets")
    
    # Add data quality insights
    null_percentage = (primary_dataset.isnull().sum().sum() / (len(primary_dataset) * len(primary_dataset.columns))) * 100
    if null_percentage > 20:
        recommendations.append(f"⚠️ High data incompleteness detected ({null_percentage:.1f}% null values)")
    
    # Add cross-dataset recommendations
    if len(datasets) > 1:
        recommendations.append("🔗 Consider cross-referencing with other datasets for deeper insights")
    
    if not recommendations:
        recommendations = [
            f"📊 Analyzed {len(primary_dataset):,} records from {dataset_name}",
            "✅ Data processing completed successfully",
            "💡 Try asking about specific metrics or time periods"
        ]
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)