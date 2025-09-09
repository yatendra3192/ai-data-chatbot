# Railway Deployment Guide

## Deployment Status ✅
The application is configured for Railway deployment. The build succeeds but requires environment variables to be set.

## Required Environment Variables

You need to set these environment variables in your Railway project:

1. **OPENAI_API_KEY** (Required)
   - Your OpenAI API key
   - Get it from: https://platform.openai.com/api-keys

2. **CORS_ORIGINS** (Optional)
   - Comma-separated list of allowed origins
   - Default: `http://localhost:3000`
   - Example: `https://your-frontend.railway.app,http://localhost:3000`

3. **NEXT_PUBLIC_API_URL** (Optional)
   - Backend API URL for the frontend
   - Default: `http://localhost:8000`
   - Example: `https://your-backend.railway.app`

## How to Set Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the "Variables" tab
4. Click "New Variable"
5. Add each variable:
   - Name: `OPENAI_API_KEY`
   - Value: `sk-proj-...` (your actual API key)
6. The deployment will automatically restart

## Deployment Configuration

### Backend (Python/FastAPI)
- **Framework**: FastAPI with uvicorn
- **Python Version**: 3.11
- **Start Command**: Configured in nixpacks.toml
- **Port**: Uses Railway's PORT environment variable

### Frontend (Next.js)
- **Framework**: Next.js 15.5.2
- **Build**: Production build with Turbopack
- **Output**: Standalone mode

### Database
- **Type**: SQLite (embedded)
- **Location**: `/app/backend/database/crm_analytics.db`
- **Note**: Database file needs to be created on first deployment

## First Deployment Setup

After setting environment variables:

1. The app will deploy automatically
2. If the database doesn't exist, you'll need to:
   - SSH into the container (if Railway allows)
   - Or modify the code to auto-create the database on startup

## Troubleshooting

### Build Failures
- Check that all TypeScript errors are fixed
- Ensure package.json dependencies are correct

### Runtime Failures
- Verify OPENAI_API_KEY is set correctly
- Check Railway logs for specific errors
- Ensure database file exists or is created

### CORS Issues
- Set CORS_ORIGINS to include your frontend URL
- Include both http and https versions if needed

## Files Involved in Deployment

- `nixpacks.toml` - Build configuration
- `Procfile` - Start command
- `railway.json` - Railway-specific settings
- `runtime.txt` - Python version
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `frontend/next.config.ts` - Next.js configuration

## Monitoring

Check deployment status at:
- Railway Dashboard: https://railway.app/dashboard
- Logs: Available in Railway dashboard
- Metrics: CPU, Memory, Network usage in Railway

## Support

For issues specific to:
- Railway: https://docs.railway.app/
- This app: Check the GitHub repository issues