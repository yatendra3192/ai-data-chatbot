# Railway Deployment Instructions

## Project URL
https://railway.com/project/52178ea8-e659-4363-be34-a17b26a552b5

## Step 1: Login to Railway CLI
```bash
railway login
```
Follow the browser prompt to authenticate.

## Step 2: Link to Project
```bash
cd ai-data-chatbot
railway link
```
Select "adaptable-liberation" when prompted.

## Step 3: Set Environment Variables
```bash
# Set OpenAI API Key
railway variables set OPENAI_API_KEY=your-api-key-here

# Set Python version
railway variables set PYTHON_VERSION=3.9

# Set Node version
railway variables set NODE_VERSION=18

# Set port
railway variables set PORT=8000
```

## Step 4: Deploy
```bash
railway up
```

## Alternative: Direct Deployment via GitHub

1. Go to https://railway.com/project/52178ea8-e659-4363-be34-a17b26a552b5
2. Click "New Service" → "GitHub Repo"
3. Select your repository: yatendra3192/ai-data-chatbot
4. Railway will auto-deploy from your main branch

## Service Configuration

Railway will automatically:
- Detect the Dockerfile and use it for building
- Set up the service with the configuration in railway.json
- Expose the application on a public URL

## Environment Variables to Set in Railway Dashboard

Navigate to your project settings and add:

```
OPENAI_API_KEY=sk-proj-...
PYTHON_VERSION=3.9
NODE_VERSION=18
PORT=8000
```

## Monitoring

After deployment:
- Check build logs: `railway logs`
- View deployment status: `railway status`
- Open deployed app: `railway open`

## Database Note

The SQLite database (465MB) needs to be included in the deployment. Make sure:
1. The database file exists at `backend/database/crm_analytics.db`
2. It's not in .gitignore for deployment (or use Git LFS)

## Troubleshooting

If deployment fails:
1. Check logs: `railway logs`
2. Verify all environment variables are set
3. Ensure database file is included
4. Check Dockerfile is working: `docker build -t test .`