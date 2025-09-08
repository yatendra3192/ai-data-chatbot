# AI Data Analysis Chatbot - Development Documentation

**Repository:** https://github.com/yatendra3192/ai-data-chatbot  
**Last Updated:** September 8, 2025  
**Current Session:** Project setup completed, ready for enhancements

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