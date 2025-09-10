"""
Unified FastAPI backend that serves both API and Next.js frontend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import asyncio
from typing import List, Dict, Any
import os
from pathlib import Path
from intelligent_sqlite_processor import process_sqlite_query, test_sqlite_connection, get_database_stats

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

# Check database connection on startup
print("=" * 60)
print("[STARTUP] Unified AI Data Analysis Application")
print("=" * 60)

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

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": db_status}

@app.post("/api/analyze")
async def analyze_data(request: QueryRequest):
    """
    Analyze data based on user query using SQLite database
    Returns Server-Sent Events stream
    """
    async def generate():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Processing your query...'})}\n\n"
            await asyncio.sleep(0.1)
            
            # Process the query using SQLite
            result = await asyncio.to_thread(
                process_sqlite_query,
                request.query
            )
            
            if result["success"]:
                # Send the complete result
                yield f"data: {json.dumps({'type': 'complete', 'data': result})}\n\n"
            else:
                # Send error
                yield f"data: {json.dumps({'type': 'error', 'error': result.get('error', 'Unknown error')})}\n\n"
                
        except Exception as e:
            print(f"[ERROR] Query processing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/stats")
async def get_stats():
    """Get database statistics"""
    try:
        stats = get_database_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datasets-info")
async def get_datasets_info():
    """Get information about loaded datasets"""
    try:
        stats = get_database_stats()
        datasets = []
        total_rows = 0
        
        for table_name, table_info in stats.items():
            if isinstance(table_info, dict):
                datasets.append({
                    "name": table_name,
                    "rows": table_info['row_count'],
                    "columns": len(table_info['columns']),
                    "sample_columns": table_info['columns'][:5]  # First 5 columns as sample
                })
                total_rows += table_info['row_count']
        
        return {
            "datasets": datasets,
            "totalRows": total_rows,
            "status": "ready",
            "backend": "SQLite Database"
        }
    except Exception as e:
        print(f"Error getting datasets info: {e}")
        return {
            "datasets": [],
            "totalRows": 0,
            "status": "error",
            "error": str(e)
        }

@app.post("/api/test-query")
async def test_query(request: QueryRequest):
    """Test endpoint for immediate query processing"""
    try:
        result = process_sqlite_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve Next.js frontend
# Path to the built Next.js app
FRONTEND_PATH = Path(__file__).parent.parent / "frontend"
NEXT_BUILD_PATH = FRONTEND_PATH / ".next"
NEXT_STATIC_PATH = NEXT_BUILD_PATH / "static"
PUBLIC_PATH = FRONTEND_PATH / "public"

# Mount static files from Next.js build
if NEXT_STATIC_PATH.exists():
    app.mount("/_next/static", StaticFiles(directory=str(NEXT_STATIC_PATH)), name="next-static")

if PUBLIC_PATH.exists():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_PATH)), name="public")

# Serve the Next.js app HTML for all non-API routes
@app.get("/{full_path:path}")
async def serve_nextjs(full_path: str):
    """Catch-all route to serve Next.js pages"""
    # Don't serve Next.js for API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # For the root path or any other path, serve the Next.js index
    index_path = FRONTEND_PATH / "out" / "index.html"
    
    # If static export exists, use it
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # Otherwise, return a simple HTML that loads the app
    return FileResponse(str(FRONTEND_PATH / "public" / "index.html"))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"[INFO] Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)