# AI Data Analysis Chatbot - Project Documentation

## Overview
An intelligent data analysis chatbot application that uses OpenAI's GPT models to dynamically analyze data from SQLite database and generate multiple visualizations. The app features a purple gradient chat interface with real-time data analysis capabilities on 1.4+ million rows of CRM data.

## Architecture
- **Backend**: FastAPI with Server-Sent Events (SSE) for streaming responses
- **Frontend**: Next.js with TypeScript
- **Database**: SQLite (465MB database with 1.4M+ rows)
- **AI Model**: GPT-4-turbo (with GPT-3.5 fallback)
- **Data Processing**: SQL queries via SQLite
- **Visualizations**: Recharts (dynamic charts)

## Key Features
1. **Intelligent Query Processing**: Uses LLM to dynamically generate SQL queries based on natural language
2. **Database-Powered Analysis**: SQLite database with 1.4M+ rows for instant queries
3. **LLM-Driven Multiple Chart Generation**: GPT-4 intelligently determines appropriate chart types
4. **Dynamic Recommendations**: Data-driven insights based on actual query results
5. **Real-time Streaming**: Uses SSE for smooth response streaming
6. **Performance**: Sub-second query response times on large datasets

## Database Details
- **SQLite Database**: `backend/database/crm_analytics.db` (465MB)
- **Tables**:
  - `salesorder`: 60,481 rows
  - `quote`: 141,461 rows
  - `quotedetail`: 1,237,446 rows
- **Total**: 1,439,388 rows

## Performance Metrics
- Query speed: 0.023-0.885 seconds (most under 0.1s)
- Memory usage: Minimal (no CSV loading)
- Startup time: Instant
- Database size: 465MB on disk

## Critical Files

### Backend
1. **intelligent_sqlite_processor.py**
   - Uses GPT-4-turbo (fallback to GPT-3.5)
   - Generates SQL queries for SQLite
   - Creates multiple visualizations
   - Handles JSON extraction from LLM responses

2. **main_sqlite.py**
   - Main FastAPI server for SQLite backend
   - No CSV loading - direct database queries
   - Endpoints: `/analyze`, `/stats`, `/api/datasets-info`
   - SSE streaming for responses

3. **database/import_csv_to_sqlite.py**
   - Imports CSV files to SQLite
   - Chunk-based processing (5000 rows/batch)
   - Creates indexes for performance

### Frontend
1. **lib/api/dataAnalysis.ts**
   - Updated to use `/analyze` endpoint (not `/api/analyze`)
   - Handles SSE streaming

2. **components/Layout/DatasetStatus.tsx**
   - Shows loaded datasets from SQLite
   - Displays row counts and memory usage

## Running the Application

### Backend (SQLite)
```bash
cd ai-data-chatbot/backend
python -m uvicorn main_sqlite:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd ai-data-chatbot/frontend
npm run dev
```

Access at: http://localhost:3000

## Test Queries
- "What are the top 5 customers by revenue?"
- "Show monthly sales trends"
- "Which products generate the most revenue?"
- "Show customer distribution by city"
- "What's the average order value by status?"

## Current Status & Issues
✅ **Working**:
- SQLite database created and populated (1.4M rows)
- Backend server running with SQLite
- Frontend displaying dataset status
- API endpoints configured correctly

⚠️ **Recent Fix Applied**:
- Changed from GPT-5 to GPT-4-turbo (GPT-5 not available)
- Added fallback to GPT-3.5 if GPT-4 fails
- Fixed frontend endpoint from `/api/analyze` to `/analyze`
- Added JSON extraction from LLM responses

## Environment Variables
```
OPENAI_API_KEY=sk-proj-... (in .env file)
```

## Database Setup
If you need to recreate the database:
```bash
cd ai-data-chatbot/backend/database
python import_csv_to_sqlite.py
```

This will import:
- `C:\Users\User\Documents\DVwithCC\salesorder.csv`
- `C:\Users\User\Documents\DVwithCC\Quote.csv`
- `C:\Users\User\Documents\DVwithCC\quotedetail.csv`

## Benefits Over CSV Approach
- **10-100x faster queries** on large datasets
- **Minimal memory usage** (vs 1.5GB for CSV)
- **Instant startup** (no CSV loading time)
- **Full dataset analysis** (all 1.4M rows)
- **Advanced SQL features** (JOINs, aggregations, indexes)

## Next Steps for Tomorrow
1. Test query functionality with the fixed GPT-4 integration
2. Verify visualizations are being generated correctly
3. Consider adding query caching for frequently asked questions
4. Add error handling for database connection issues
5. Optimize SQL queries for complex aggregations

## Known Issues to Address
- GPT-5 model not available (using GPT-4-turbo instead)
- Some complex queries may need optimization
- Consider adding progress indicators for long-running queries

## Important Notes
- Always ensure SQLite database exists before starting backend
- The app now uses SQL queries instead of pandas operations
- All 1.4M rows are available for analysis
- Multiple background processes may be running - check with `/bashes` command