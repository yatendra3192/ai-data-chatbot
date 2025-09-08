from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import os
from pathlib import Path

from backend.config.settings import settings
from backend.langgraph.workflow import DataAnalysisWorkflow
from backend.data.csv_processor import CSVProcessor

app = FastAPI(title="AI Data Analyst API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
workflow = DataAnalysisWorkflow()
csv_processor = CSVProcessor()

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
            async for event in workflow.run(request.query, request.data_file):
                yield f"data: {json.dumps(event)}\n\n"
        
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

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and process CSV file
    """
    # Validate file
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Check file size
    file_size = 0
    contents = await file.read()
    file_size = len(contents) / (1024 * 1024)  # Convert to MB
    
    if file_size > settings.MAX_CSV_SIZE_MB:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds {settings.MAX_CSV_SIZE_MB}MB limit"
        )
    
    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Process CSV
    try:
        result = await csv_processor.process_csv(str(file_path))
        return {
            "filename": file.filename,
            "path": str(file_path),
            "rows": result["total_rows"],
            "columns": result["columns"],
            "sample": result["sample"],
            "statistics": result["statistics"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )