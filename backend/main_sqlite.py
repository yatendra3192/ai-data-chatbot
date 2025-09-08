"""
FastAPI backend with SQLite database for improved performance
No more loading CSVs into memory - direct SQL queries!
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import List, Dict, Any
import os
from intelligent_sqlite_processor import process_sqlite_query, test_sqlite_connection, get_database_stats

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

# No need to load CSVs anymore! SQLite handles everything
print("=" * 60)
print("[STARTUP] AI Data Analysis Backend with SQLite Database")
print("=" * 60)

# Check database connection on startup
db_status = test_sqlite_connection()
if db_status['connected']:
    print("[SUCCESS] Connected to SQLite database")
    print(f"[INFO] Database stats:")
    for table, info in db_status['stats'].items():
        if isinstance(info, dict):
            print(f"   {table}: {info['row_count']:,} rows")
        else:
            print(f"   Database size: {info:.2f} MB")
else:
    print(f"[ERROR] Database connection failed: {db_status['error']}")
    print("   Please run: python database/import_csv_to_sqlite.py")

print("=" * 60)

@app.get("/")
async def root():
    return {"message": "AI Data Analysis API with SQLite Database"}

@app.get("/health")
async def health():
    """Health check endpoint with database status"""
    db_status = test_sqlite_connection()
    return {
        "status": "healthy" if db_status['connected'] else "degraded",
        "database": db_status
    }

@app.get("/stats")
async def stats():
    """Get database statistics"""
    return get_database_stats()

@app.get("/api/datasets-info")
async def datasets_info():
    """Get dataset information in frontend-compatible format"""
    stats = get_database_stats()
    
    datasets = {}
    for table_name in ['salesorder', 'quote', 'quotedetail']:
        if table_name in stats:
            datasets[table_name] = {
                "loaded_rows": stats[table_name]['row_count'],
                "total_rows": stats[table_name]['row_count'],  # All rows are available in SQLite
                "memory_usage": f"{stats[table_name].get('estimated_size_mb', 0):.2f} MB"
            }
    
    return {
        "loaded": True,
        "datasets": datasets,
        "available_for_analysis": list(datasets.keys())
    }

async def generate_sse_response(query: str):
    """Generate Server-Sent Events for streaming response"""
    
    # Send initial status
    yield f"data: {json.dumps({'status': 'processing', 'message': 'Analyzing your query with SQLite database...'})}\n\n"
    await asyncio.sleep(0.1)
    
    try:
        # Process query using SQLite
        result = process_sqlite_query(query)
        
        # Send the complete result
        yield f"data: {json.dumps({'status': 'complete', **result})}\n\n"
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        yield f"data: {json.dumps({'status': 'error', 'error': error_msg})}\n\n"

@app.post("/analyze")
async def analyze(request: QueryRequest):
    """
    Analyze data based on natural language query using SQLite database
    Returns Server-Sent Events stream
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Check database connection
    db_status = test_sqlite_connection()
    if not db_status['connected']:
        raise HTTPException(
            status_code=503, 
            detail=f"Database not available: {db_status.get('error', 'Unknown error')}"
        )
    
    return StreamingResponse(
        generate_sse_response(request.query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.post("/test-query")
async def test_query(request: QueryRequest):
    """Test endpoint for debugging queries"""
    try:
        result = process_sqlite_query(request.query)
        return {
            "success": True,
            "query": request.query,
            "sql_generated": result.get('sql_query', 'N/A'),
            "visualizations_count": len(result.get('visualizations', [])),
            "row_count": result.get('row_count', 0),
            "recommendations": result.get('recommendations', [])
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("\n[INFO] Starting server at http://localhost:8000")
    print("[INFO] API docs available at http://localhost:8000/docs")
    print("\n[INFO] Benefits of SQLite Database:")
    print("   - Instant startup (no CSV loading)")
    print("   - 10-100x faster queries")
    print("   - Minimal memory usage")
    print("   - Full dataset analysis (780K+ rows)")
    print("   - Complex JOINs and aggregations")
    uvicorn.run(app, host="0.0.0.0", port=8000)