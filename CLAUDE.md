# AI Data Analysis Chatbot - Development Documentation

**Repository:** https://github.com/yatendra3192/ai-data-chatbot  
**Live Demo:** https://adaptable-liberation.up.railway.app  
**Last Updated:** September 10, 2025  
**Current Session:** Successfully deployed to Railway with all fixes applied

## Overview
An intelligent data analysis chatbot application that uses OpenAI's GPT models to dynamically analyze data from SQLite database and generate multiple visualizations. The app features a purple gradient chat interface with real-time data analysis capabilities on 1.4+ million rows of CRM data.

## Architecture
- **Backend**: FastAPI with Server-Sent Events (SSE) for streaming responses
- **Frontend**: Next.js with TypeScript (served by backend in production)
- **Database**: SQLite (465MB database with 1.4M+ rows)
- **AI Model**: GPT-4-turbo (with GPT-3.5 fallback)
- **Data Processing**: SQL queries via SQLite
- **Visualizations**: Recharts (dynamic charts)
- **Deployment**: Railway Cloud Platform (automatic CI/CD from GitHub)

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
1. **main_unified.py** (PRODUCTION)
   - Unified FastAPI server that serves both API and frontend
   - Handles all API endpoints and static file serving
   - Fixed streaming response structure (type: 'complete')
   - Database path handling for both local and Docker/Railway

2. **intelligent_sqlite_processor.py**
   - Uses GPT-4-turbo (fallback to GPT-3.5)
   - Generates SQL queries for SQLite
   - Creates multiple visualizations
   - Handles JSON extraction from LLM responses

3. **main_sqlite.py** (DEVELOPMENT ONLY)
   - Standalone API server for local development
   - No frontend serving
   - Endpoints: `/analyze`, `/stats`, `/api/datasets-info`
   - SSE streaming for responses

4. **database/import_csv_to_sqlite.py**
   - Imports CSV files to SQLite
   - Chunk-based processing (5000 rows/batch)
   - Creates indexes for performance

5. **download_database.py**
   - Downloads database from external sources
   - Handles Google Drive large file downloads
   - Progress tracking for large downloads

### Frontend
1. **lib/api/dataAnalysis.ts**
   - Uses `/api/analyze` endpoint in production
   - Handles SSE streaming with proper error handling

2. **lib/hooks/useDataAnalysis.ts** (CRITICAL FIX)
   - Fixed type vs status mismatch (data.type === 'complete')
   - Handles nested response structure (data.data)
   - Properly processes streaming responses

3. **components/Layout/DatasetStatus.tsx**
   - Shows loaded datasets from SQLite
   - Fixed to match backend response structure
   - Displays row counts and table information

4. **components/Visualization/ChartGrid.tsx**
   - Renders multiple dynamic charts
   - Handles various chart types from backend

5. **components/Chat/ChatInterface.tsx**
   - Chat UI with message history
   - Handles loading states and error messages

## Running the Application

### Local Development
```bash
# Backend with unified server (serves both API and frontend)
cd ai-data-chatbot/backend
python -m uvicorn main_unified:app --host 0.0.0.0 --port 8000

# OR for API-only development
python -m uvicorn main_sqlite:app --host 0.0.0.0 --port 8000

# Frontend development mode (optional, for hot reload)
cd ai-data-chatbot/frontend
npm run dev
```

Access at: 
- Unified server: http://localhost:8000
- Frontend dev: http://localhost:3000

### Production (Railway)
- **URL**: https://adaptable-liberation.up.railway.app
- **Auto-deploy**: Push to main branch triggers deployment
- **Server**: Unified backend serves both API and frontend

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
- **PRODUCTION DEPLOYED**: Live at https://adaptable-liberation.up.railway.app
- Full database (465MB) successfully deployed
- Unified server architecture working

⚠️ **Recent Fixes Applied (Sept 10, 2025)**:
- Fixed streaming response type/status mismatch in useDataAnalysis.ts
- Resolved Railway volume mount conflicts by moving to /railway directory
- Fixed nested response data structure (data.data)
- Database download from external sources working
- Frontend properly displaying query results and visualizations

🐛 **Known Issues (Resolved)**:
- ~~Volume mount conflict at /app/backend/database~~ → Fixed by moving to /railway
- ~~Frontend not displaying data~~ → Fixed type/status mismatch
- ~~Container startup failures~~ → Fixed with new Dockerfile structure
- ~~Database not persisting~~ → Included in Docker image

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

## Railway Deployment Details

### Dockerfile Configuration
```dockerfile
# Key changes for Railway deployment:
WORKDIR /railway  # Moved from /app to avoid volume conflicts
# Multi-stage build for optimized size
# Frontend built and served by backend
# Database included in image (no volume needed)
```

### Railway Settings
- **Project**: adaptable-liberation
- **GitHub Repo**: https://github.com/yatendra3192/ai-data-chatbot
- **Auto Deploy**: Enabled on main branch
- **Build Command**: Docker (automatic)
- **Start Command**: Defined in Dockerfile
- **Port**: Automatically detected (8000)
- **Volume**: Not needed (database in image)

### Deployment Process
1. Push to GitHub main branch
2. Railway automatically detects changes
3. Builds Docker image with database included
4. Deploys to production URL
5. Zero-downtime deployment

## Benefits Over CSV Approach
- **10-100x faster queries** on large datasets
- **Minimal memory usage** (vs 1.5GB for CSV)
- **Instant startup** (no CSV loading time)
- **Full dataset analysis** (all 1.4M rows)
- **Advanced SQL features** (JOINs, aggregations, indexes)

## Deployment Troubleshooting Guide

### Common Railway Issues & Solutions

1. **Container fails to start - Volume mount error**
   - **Error**: "The volume is mounted to a directory that is overriding the container's entrypoint"
   - **Solution**: Move app to /railway directory in Dockerfile
   - **Status**: FIXED in current deployment

2. **Frontend not displaying data**
   - **Issue**: Streaming response shows type: 'complete' but frontend checks status: 'complete'
   - **Solution**: Update useDataAnalysis.ts to check data.type === 'complete'
   - **File**: frontend/lib/hooks/useDataAnalysis.ts:48
   - **Status**: FIXED

3. **Database not found in production**
   - **Issue**: Database path differs between local and Railway
   - **Solution**: Check for /railway directory existence in main_unified.py
   - **Status**: FIXED with path detection logic

4. **API endpoints 404**
   - **Issue**: Frontend calling wrong endpoint
   - **Solution**: Ensure frontend uses /api/analyze in production
   - **Status**: FIXED

### Quick Debugging Commands
```bash
# Check Railway logs
railway logs

# Test API health
curl https://adaptable-liberation.up.railway.app/api/health

# Test query endpoint
curl -X POST https://adaptable-liberation.up.railway.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

## Development Roadmap for Tomorrow

### Immediate Tasks (Day 1 Priority)
1. **Test Core Functionality**
   - [ ] Test 5-10 different query types to ensure stability
   - [ ] Verify all chart types render correctly
   - [ ] Check error handling for malformed queries
   - [ ] Test with edge cases (empty results, large datasets)

2. **User Experience Improvements**
   - [ ] Add loading animation during query processing
   - [ ] Implement query suggestions/examples dropdown
   - [ ] Add "Copy to Clipboard" for SQL queries
   - [ ] Show query execution time

3. **Performance Optimization**
   - [ ] Add indexes to frequently queried columns
   - [ ] Implement basic query result caching (in-memory)
   - [ ] Optimize chart rendering for large datasets
   - [ ] Add query timeout handling

### Week 1 Goals
1. **Enhanced Analytics**
   - [ ] Add trend analysis capabilities
   - [ ] Implement year-over-year comparisons
   - [ ] Add statistical summaries to results
   - [ ] Create dashboard view with KPIs

2. **Data Export Features**
   - [ ] CSV export for query results
   - [ ] Chart export as PNG/SVG
   - [ ] Generate PDF reports
   - [ ] Implement scheduled reports

3. **Query Management**
   - [ ] Save favorite queries
   - [ ] Query history with re-run capability
   - [ ] Share query links
   - [ ] Query templates for common analyses

### Technical Debt & Improvements
1. **Code Quality**
   - [ ] Add unit tests for backend endpoints
   - [ ] Implement integration tests
   - [ ] Add TypeScript strict mode
   - [ ] Set up linting and formatting

2. **Documentation**
   - [ ] API documentation with Swagger
   - [ ] Component documentation
   - [ ] Deployment guide
   - [ ] Contributing guidelines

3. **Infrastructure**
   - [ ] Docker containerization
   - [ ] CI/CD pipeline setup
   - [ ] Environment-based configuration
   - [ ] Logging and monitoring

## Known Issues & Bugs

### High Priority
- [ ] Large result sets (>10k rows) can slow down chart rendering
- [ ] No graceful handling when OpenAI API rate limit is hit
- [ ] Memory usage grows with repeated queries (no cleanup)

### Medium Priority
- [ ] Chart colors are not consistent across renders
- [ ] No validation for SQL injection in generated queries
- [ ] SSE connection doesn't reconnect on failure

### Low Priority
- [ ] Dark mode toggle doesn't persist
- [ ] Mobile responsive design needs work
- [ ] No keyboard shortcuts for common actions

## Development Tips

### Quick Commands
```bash
# Start both servers
cd ai-data-chatbot/backend && python -m uvicorn main_sqlite:app --reload &
cd ai-data-chatbot/frontend && npm run dev

# Check database stats
cd ai-data-chatbot/backend
python -c "from intelligent_sqlite_processor import get_database_stats; import json; print(json.dumps(get_database_stats(), indent=2))"

# Test a query directly
curl -X POST http://localhost:8000/test-query \
  -H "Content-Type: application/json" \
  -d '{"query": "top 5 customers by revenue"}'
```

### Performance Monitoring
- Backend logs: Check uvicorn output for query times
- Frontend: Use Chrome DevTools Performance tab
- Database: Use SQLite EXPLAIN QUERY PLAN

### Testing Queries
1. Simple aggregations: "Total revenue by month"
2. Complex JOINs: "Customer orders with product details"
3. Time-series: "Sales trend over last 12 months"
4. Comparisons: "Top products this year vs last year"
5. Statistical: "Average order value distribution"

## Architecture Decisions

### Why SQLite?
- Fast queries on 1.4M+ rows
- No separate database server needed
- Portable and easy to distribute
- Built-in full-text search capabilities

### Why SSE over WebSockets?
- Simpler implementation
- Better for one-way streaming
- Works through proxies/firewalls
- Auto-reconnection in browsers

### Why GPT-4-turbo?
- Best balance of performance and cost
- Excellent SQL generation
- Good at understanding business context
- Reliable JSON output formatting

## Important Notes
- Database file is gitignored (465MB)
- CSV files are gitignored (>100MB)
- Environment variables in .env (not in repo)
- Two servers run simultaneously (ports 8000, 3000)
- GitHub repo at: https://github.com/yatendra3192/ai-data-chatbot