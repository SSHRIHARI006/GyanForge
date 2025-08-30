# 🚀 GyanForge Render Deployment Guide

This guide will help you deploy the complete GyanForge application on Render with backend API, frontend, database, and Redis cache.

## 📋 What Will Be Deployed

### Services on Render:
1. **Backend API** - Python FastAPI application
2. **Frontend** - React application (static site)
3. **PostgreSQL Database** - Managed database service
4. **Redis Cache** - For caching and performance

## 🔧 Prerequisites

1. **Render Account** - Sign up at [render.com](https://render.com)
2. **GitHub Repository** - Your code should be pushed to GitHub
3. **API Keys** - Have your Gemini and Pinecone API keys ready

## 🚀 Quick Deploy Method

### Option 1: One-Click Deploy

1. **Fork the Repository** (if you haven't already)
2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub account
   - Select the `GyanForge` repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=gyanforge-data
   ```

4. **Deploy** - Click "Apply" and wait for deployment

### Option 2: Manual Service Creation

#### Step 1: Create Database
1. Go to Render Dashboard → "New" → "PostgreSQL"
2. Name: `gyanforge-db`
3. Database Name: `gyanforge`
4. User: `gyanforge_user`
5. Create and note the connection string

#### Step 2: Create Redis Cache
1. Go to Render Dashboard → "New" → "Redis"
2. Name: `gyanforge-redis`
3. Plan: Free
4. Create and note the connection string

#### Step 3: Deploy Backend API
1. Go to Render Dashboard → "New" → "Web Service"
2. Connect your GitHub repository
3. **Configuration**:
   ```
   Name: gyanforge-backend
   Runtime: Python 3
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables**:
   ```env
   PYTHONPATH=/opt/render/project/src/backend
   PYTHONUNBUFFERED=1
   ENVIRONMENT=production
   DATABASE_URL=[your_postgresql_connection_string]
   REDIS_URL=[your_redis_connection_string]
   SECRET_KEY=[generate_random_secret]
   GEMINI_API_KEY=your_gemini_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=gyanforge-data
   CORS_ORIGINS=https://gyanforge-frontend.onrender.com
   ```

5. **Health Check Path**: `/health`

#### Step 4: Deploy Frontend
1. Go to Render Dashboard → "New" → "Static Site"
2. Connect your GitHub repository
3. **Configuration**:
   ```
   Name: gyanforge-frontend
   Build Command: cd frontend && npm ci && npm run build
   Publish Directory: frontend/build
   ```

4. **Environment Variables**:
   ```env
   REACT_APP_API_URL=https://gyanforge-backend.onrender.com
   REACT_APP_ENV=production
   ```

5. **Redirects/Rewrites**: Add a rewrite rule for SPA routing:
   ```
   /* → /index.html (200)
   ```

## 🔧 Configuration Details

### Backend Configuration

The backend will automatically:
- Set up the database tables on first run
- Connect to Redis for caching
- Serve API endpoints at `/api/v1/`
- Provide health checks at `/health`

### Frontend Configuration

The frontend will:
- Build as a static React application
- Connect to the backend API automatically
- Handle client-side routing
- Serve the application at the root domain

### Database Configuration

**PostgreSQL** will be used instead of SQLite for production:
- Automatic connection through `DATABASE_URL`
- Tables created automatically on startup
- Persistent data storage
- Better performance for production

## 🌐 Access Your Application

After deployment, your application will be available at:

- **Frontend**: `https://gyanforge-frontend.onrender.com`
- **Backend API**: `https://gyanforge-backend.onrender.com`
- **API Documentation**: `https://gyanforge-backend.onrender.com/docs`

## 🔑 Required Environment Variables

### Backend Service:
```env
# Database (auto-provided by Render)
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port

# Security
SECRET_KEY=your-random-secret-key-here

# AI Services (Required)
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=gyanforge-data

# Application
ENVIRONMENT=production
CORS_ORIGINS=https://gyanforge-frontend.onrender.com
```

### Frontend Service:
```env
REACT_APP_API_URL=https://gyanforge-backend.onrender.com
REACT_APP_ENV=production
```

## 💰 Render Pricing

### Free Tier Includes:
- **Web Services**: 750 hours/month per service
- **PostgreSQL**: 1GB storage, 1 million queries
- **Redis**: 25MB memory
- **Static Sites**: Unlimited bandwidth

### Paid Plans:
- **Starter ($7/month per service)**: Always-on, no sleep
- **Standard ($25/month per service)**: More resources, better performance

## 🚨 Important Notes

### Free Tier Limitations:
1. **Services sleep after 15 minutes** of inactivity
2. **Cold start delay** when waking up (~30 seconds)
3. **Limited resources** (512MB RAM, 0.1 CPU)

### Production Recommendations:
1. **Use Starter plan** for always-on services
2. **Monitor resource usage** in Render dashboard
3. **Set up custom domain** for professional appearance
4. **Configure monitoring** and alerts

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check build logs in Render dashboard
   - Verify all dependencies in requirements.txt/package.json
   - Ensure correct Python/Node versions

2. **Environment Variables**:
   - Double-check all required variables are set
   - Verify API keys are valid
   - Check database connection strings

3. **CORS Issues**:
   - Ensure `CORS_ORIGINS` includes your frontend URL
   - Check both HTTP and HTTPS variants

4. **Database Connection**:
   - Verify `DATABASE_URL` is correctly formatted
   - Check PostgreSQL service is running
   - Review connection logs

### Debugging Commands:
```bash
# Check service logs
# Available in Render dashboard under "Logs"

# Test backend health
curl https://gyanforge-backend.onrender.com/health

# Test frontend
curl https://gyanforge-frontend.onrender.com
```

## 📊 Monitoring

### Built-in Monitoring:
- Service uptime and response times
- Resource usage (CPU, memory)
- Error rates and logs
- Database connection status

### Health Checks:
- Backend: `/health` endpoint
- Automatic restart on failures
- Email notifications for downtime

## 🔄 Updates and Deployment

### Automatic Deployments:
- **Auto-deploy on Git push** (enabled by default)
- **Manual deployments** from Render dashboard
- **Rollback capability** to previous versions

### Best Practices:
1. **Test locally** before pushing
2. **Use environment branches** for staging
3. **Monitor logs** during deployment
4. **Keep dependencies updated**

---

Your GyanForge application is now ready for professional deployment on Render! 🎓✨
