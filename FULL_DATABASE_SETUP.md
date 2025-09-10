# Full Database Setup for Railway Deployment

## Option 1: Upload to Cloud Storage (Recommended)

### Step 1: Upload your database to a cloud service
Choose one of these options:

#### A. Google Drive
1. Upload `crm_analytics.db` (465MB) to Google Drive
2. Make it publicly accessible (right-click → Share → Anyone with link)
3. Get the direct download link:
   - Original link: `https://drive.google.com/file/d/FILE_ID/view`
   - Convert to: `https://drive.google.com/uc?export=download&id=FILE_ID`

#### B. Dropbox
1. Upload to Dropbox
2. Get sharing link
3. Change `?dl=0` to `?dl=1` at the end of the URL

#### C. GitHub Releases (if repo is public)
1. Go to your GitHub repo
2. Create a new Release
3. Attach the database file
4. Get the direct download URL

#### D. AWS S3 / Google Cloud Storage
1. Upload to bucket
2. Make publicly readable
3. Get the direct URL

### Step 2: Set Railway Environment Variable
1. Go to your Railway project: https://railway.com/project/52178ea8-e659-4363-be34-a17b26a552b5
2. Click on your service
3. Go to "Variables" tab
4. Add new variable:
   - Name: `DATABASE_URL`
   - Value: Your direct download URL from Step 1

### Step 3: Redeploy
Railway will automatically redeploy and download your full database.

---

## Option 2: Use Railway Volumes (Persistent Storage)

### Step 1: Create a Volume
1. In Railway dashboard, go to your service
2. Click "Settings" → "Volumes"
3. Create a new volume:
   - Mount path: `/app/backend/database`
   - Size: 1GB

### Step 2: Upload Database Manually
You'll need to SSH into the container or use Railway CLI to upload the database.

---

## Option 3: Use External Database Service

### PostgreSQL on Railway
1. Add a PostgreSQL service to your Railway project
2. Migrate SQLite to PostgreSQL using a migration script
3. Update backend to use PostgreSQL

Benefits:
- Better for production
- Handles concurrent connections better
- Built-in backups

---

## Option 4: Git LFS (Large File Storage)

### Step 1: Install Git LFS
```bash
git lfs install
```

### Step 2: Track the database file
```bash
cd ai-data-chatbot
git lfs track "backend/database/crm_analytics.db"
git add .gitattributes
git add backend/database/crm_analytics.db
git commit -m "Add full database with Git LFS"
git push origin main
```

Note: GitHub free tier allows 1GB storage and 1GB bandwidth per month.

---

## Current Implementation

The app now has a smart database initialization:

1. **First Priority**: Downloads full database from `DATABASE_URL` if set
2. **Fallback**: Creates sample database with 13,000 records
3. **Auto-detection**: If database is < 10MB, tries to download full version

### To use your full database:

1. Upload your `crm_analytics.db` file to any cloud storage
2. Get a direct download URL
3. Add `DATABASE_URL` environment variable in Railway
4. Redeploy - the app will automatically download and use your full database

---

## Verification

After deployment, check the logs in Railway:
- Should show "Database exists: 465.XX MB" if full database is loaded
- Will show "Database exists: ~5 MB" if using sample database

You can test with queries like:
- "How many total records are in the database?"
- "Show me sales data for all 60,000+ orders"
- "Analyze all 1.2 million quote details"

---

## Important Notes

- The database download happens only once on container start
- If using Railway's free tier, be aware of resource limits
- Consider using PostgreSQL for production deployments
- The sample database (13,000 records) is sufficient for demo purposes