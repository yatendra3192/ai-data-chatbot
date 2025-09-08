# AI Data Analysis Chatbot

An intelligent data analysis chatbot that uses OpenAI's GPT-4 to dynamically analyze data from SQLite database and generate multiple visualizations. Features a purple gradient chat interface with real-time data analysis on 1.4+ million rows of CRM data.

**Repository:** https://github.com/yatendra3192/ai-data-chatbot

**Last Updated:** September 8, 2025

## Features

- **Intelligent Query Processing**: Uses LLM to dynamically generate SQL queries from natural language
- **SQLite Database**: Fast queries on 1.4M+ rows with minimal memory usage
- **Multiple Chart Generation**: AI automatically generates 4-5 appropriate chart types per query
- **Dynamic Visualizations**: Charts update based on actual query results
- **Real-time Streaming**: Server-Sent Events (SSE) for smooth response streaming
- **Smart Recommendations**: Data-driven insights based on actual analysis

## Architecture

- **Backend**: FastAPI with SSE streaming
- **Frontend**: Next.js + TypeScript + Tailwind CSS + Recharts
- **Database**: SQLite (465MB, 1.4M+ rows)
- **AI Model**: GPT-4-turbo (with GPT-3.5 fallback)
- **Data Processing**: Direct SQL queries (no CSV loading)

## Current Status

✅ **Working**:
- SQLite database with 1.4M+ rows (465MB)
- Backend server with SQL query generation
- Frontend displaying dataset status
- Multiple chart generation (4-5 per query)
- SSE streaming for real-time updates

⚠️ **Recent Fixes**:
- Switched from GPT-5 to GPT-4-turbo (GPT-5 not available)
- Fixed frontend endpoint from `/api/analyze` to `/analyze`
- Added JSON extraction from LLM responses
- Reduced SQLite chunk size to avoid "too many variables" error

## Database Details

- **Database**: `backend/database/crm_analytics.db` (465MB)
- **Tables**:
  - `salesorder`: 60,481 rows
  - `quote`: 141,461 rows 
  - `quotedetail`: 1,237,446 rows
- **Total**: 1,439,388 rows
- **Performance**: Sub-second query times

## Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/yatendra3192/ai-data-chatbot.git
cd ai-data-chatbot
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Database Setup

**Option A: Using Pre-built Database**
- Download the SQLite database file (465MB) from [releases/database] (if available)
- Place it in `backend/database/crm_analytics.db`

**Option B: Build from CSV Files**
1. Obtain the CSV files:
   - salesorder.csv (118MB+)
   - Quote.csv
   - quotedetail.csv
2. Place them in appropriate directories
3. Run the import script:
```bash
cd backend/database
python import_csv_to_sqlite.py
```

## Running the Application

### Backend (SQLite version)

```bash
cd ai-data-chatbot/backend
python -m uvicorn main_sqlite:app --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`

### Frontend

```bash
cd ai-data-chatbot/frontend
npm run dev
```

Dashboard available at: `http://localhost:3000`

## Usage

### Test Queries

Try these natural language queries:
- "What are the top 5 customers by revenue?"
- "Show monthly sales trends"
- "Which products generate the most revenue?"
- "Show customer distribution by city"
- "What's the average order value by status?"

### How It Works

1. **Query Processing**: GPT-4 converts natural language to SQL
2. **Database Query**: SQLite executes optimized queries on 1.4M+ rows
3. **Visualization**: AI generates 4-5 appropriate chart types
4. **Insights**: Data-driven recommendations based on results

## Key Files

### Backend
- **`intelligent_sqlite_processor.py`**: GPT-4 query processor
- **`main_sqlite.py`**: FastAPI server with SSE
- **`database/crm_analytics.db`**: SQLite database (465MB)
- **`database/import_csv_to_sqlite.py`**: CSV importer

### Frontend
- **`lib/api/dataAnalysis.ts`**: API client (uses `/analyze`)
- **`lib/hooks/useDataAnalysis.ts`**: SSE stream handler
- **`components/Layout/DatasetStatus.tsx`**: Dataset info display
- **`components/Dashboard/ChartRenderer.tsx`**: Dynamic charts

## Technical Details

### GPT-4 Integration
```python
# Uses GPT-4-turbo with fallback to GPT-3.5
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[...],
    temperature=0.3,
    max_tokens=3000
)
```

### SQL Query Generation
- LLM generates optimized SQLite queries
- Uses appropriate indexes for performance
- Handles JOINs across multiple tables
- Date functions with strftime

### Chart Generation
- 4-5 visualizations per query
- Types: bar, pie, line, area, scatter, radar
- Data-specific chart selection
- Recharts for rendering

## Benefits Over CSV Approach

- **10-100x faster queries** on large datasets
- **Minimal memory usage** (vs 1.5GB for CSV in memory)
- **Instant startup** (no CSV loading time)
- **Full dataset analysis** (all 1.4M rows available)
- **Advanced SQL features** (JOINs, aggregations, indexes)

## API Endpoints

- `POST /analyze`: Analyze data with SSE streaming
- `GET /stats`: Database statistics
- `GET /api/datasets-info`: Dataset information for frontend
- `GET /health`: Health check with database status
- `POST /test-query`: Debug endpoint for testing

## Performance Metrics

- Query speed: 0.023-0.885 seconds (most under 0.1s)
- Memory usage: Minimal (no CSV loading)
- Startup time: Instant
- Database size: 465MB on disk
- Total rows: 1,439,388 across 3 tables

## Troubleshooting

### Common Issues

1. **"GPT-5 not available" error**:
   - Already fixed: Uses GPT-4-turbo instead

2. **"Not returning results"**:
   - Check backend is running on port 8000
   - Verify frontend uses `/analyze` (not `/api/analyze`)

3. **Database errors**:
   - Ensure `backend/database/crm_analytics.db` exists
   - Run import script if missing

4. **Multiple background processes**:
   - Check with `/bashes` command
   - Kill old processes if needed

## Project Status

### ✅ Completed Features
- SQLite database with 1.4M+ rows integrated
- FastAPI backend with SSE streaming
- Next.js frontend with purple gradient UI
- GPT-4-turbo integration for SQL generation
- Multiple dynamic chart generation
- Real-time data analysis capabilities
- GitHub repository setup and deployment

### 🚀 Upcoming Improvements (Priority Order)

#### Phase 1: Core Functionality Enhancement
1. **Query Optimization**
   - Add query result caching for frequently asked questions
   - Implement query optimization for complex JOINs
   - Add query execution time limits

2. **Error Handling & Resilience**
   - Improve error messages for failed queries
   - Add database connection retry logic
   - Implement graceful fallbacks for API failures

3. **User Experience**
   - Add loading spinners during query processing
   - Implement query history/saved queries
   - Add ability to export charts as images/PDF

#### Phase 2: Advanced Features
1. **Data Export**
   - CSV export for query results
   - Excel export with formatting
   - PDF reports with charts and insights

2. **Advanced Analytics**
   - Time-series forecasting
   - Anomaly detection
   - Comparative analysis tools

3. **Performance**
   - Implement Redis caching
   - Add database indexing optimization
   - Query parallelization for multiple charts

#### Phase 3: Enterprise Features
1. **Security & Authentication**
   - User authentication system
   - Role-based access control
   - Query audit logging

2. **Scalability**
   - Multi-database support
   - Horizontal scaling capabilities
   - Load balancing for API requests

3. **Integration**
   - REST API for external systems
   - Webhook support for automated reports
   - Integration with BI tools

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.