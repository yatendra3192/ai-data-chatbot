# Deployment Guide for Railway

This guide will help you deploy the AI Data Chatbot application to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Railway CLI installed (optional but recommended)
3. Your OpenAI API key

## Deployment Steps

### Method 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create a new Railway project**
   - Go to https://railway.app/new
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select your repository: `ai-data-chatbot`

3. **Configure environment variables**
   In Railway dashboard, go to Variables and add:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   PORT=8000
   NEXT_PUBLIC_API_URL=https://your-app-name.railway.app
   CORS_ORIGINS=https://your-app-name.railway.app
   NODE_ENV=production
   PYTHON_ENV=production
   ```

4. **Deploy**
   - Railway will automatically detect the configuration and start deployment
   - The build process will:
     - Install Python dependencies
     - Install Node.js dependencies
     - Build the Next.js frontend
     - Start the backend server

### Method 2: Deploy using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize a new project**
   ```bash
   railway init
   ```

4. **Add environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=your_actual_openai_api_key_here
   railway variables set PORT=8000
   railway variables set NODE_ENV=production
   railway variables set PYTHON_ENV=production
   ```

5. **Deploy**
   ```bash
   railway up
   ```

## Configuration Files Explained

### `railway.json`
Defines build and deployment configuration for Railway platform.

### `nixpacks.toml`
Specifies the build process using Nixpacks (Railway's default builder).

### `Dockerfile`
Alternative deployment method using Docker containers.

### `.env.example`
Template for environment variables - copy to `.env` for local development.

## Database Setup

The SQLite database will be created automatically on first run if it doesn't exist. However, for production:

1. **Option 1: Pre-built Database**
   - Include the `crm_analytics.db` file in your repository (if size permits)
   - Place it in `backend/database/`

2. **Option 2: Build on Deploy**
   - The database will be created from CSV files on first run
   - Ensure CSV files are accessible or modify the import script

3. **Option 3: Use Railway PostgreSQL** (Recommended for production)
   - Add a PostgreSQL database to your Railway project
   - Modify the backend code to use PostgreSQL instead of SQLite

## Post-Deployment

1. **Access your application**
   - Railway will provide a URL like: `https://your-app-name.railway.app`
   - The API will be available at the same URL

2. **Monitor logs**
   - Use Railway dashboard to view logs
   - Or use CLI: `railway logs`

3. **Update deployment**
   - Push changes to GitHub (if using GitHub integration)
   - Or use: `railway up` (if using CLI)

## Troubleshooting

### Common Issues:

1. **"Module not found" errors**
   - Check that all dependencies are in `requirements.txt` and `package.json`
   - Ensure the build commands in `nixpacks.toml` are correct

2. **CORS errors**
   - Update `CORS_ORIGINS` environment variable with your Railway URL
   - Ensure frontend is using correct API URL

3. **Database not found**
   - Check if database file exists in `backend/database/`
   - Verify the import script runs successfully

4. **Port binding issues**
   - Railway automatically sets the PORT environment variable
   - Ensure your app uses `process.env.PORT` or `$PORT`

## Performance Optimization

1. **Use PostgreSQL for production**
   - SQLite may have limitations with concurrent users
   - Railway provides easy PostgreSQL integration

2. **Enable caching**
   - Consider adding Redis for query result caching
   - Railway supports Redis add-ons

3. **Scale horizontally**
   - Use Railway's scaling features for high traffic
   - Separate frontend and backend into different services

## Security Considerations

1. **Never commit `.env` files**
   - Use Railway's environment variables instead

2. **Secure your API**
   - Consider adding authentication
   - Implement rate limiting

3. **Database security**
   - Use PostgreSQL with proper credentials for production
   - Don't expose database directly

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/yatendra3192/ai-data-chatbot/issues