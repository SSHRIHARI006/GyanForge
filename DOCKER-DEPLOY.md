# 🐳 Deploy GyanForge to Render using Docker (Free)

This guide shows how to deploy GyanForge to Render using Docker containers, which often bypasses payment requirements.

## 🎯 **Why Docker on Render?**

✅ **Often free** - Docker deployments sometimes don't require payment details
✅ **Consistent environment** - Same container works everywhere  
✅ **Easier configuration** - Everything bundled in the container
✅ **Better performance** - Optimized container setup

## 🚀 **Step-by-Step Docker Deployment:**

### **Step 1: Prepare Repository**
Your repository now has:
- ✅ `Dockerfile` (root level - for backend)
- ✅ `render.yaml` (Docker configuration)
- ✅ All code ready

### **Step 2: Deploy to Render**

#### **Option A: Blueprint Deployment (Recommended)**
1. **Go to [render.com](https://render.com)**
2. **Sign in with GitHub** (try without payment details first)
3. **Click "New" → "Blueprint"**
4. **Select your repository**: `SSHRIHARI006/GyanForge`
5. **Render detects**: `render.yaml` with Docker configuration

#### **Option B: Manual Docker Service**
If blueprint doesn't work:
1. **Click "New" → "Web Service"**
2. **Connect GitHub** → Select `SSHRIHARI006/GyanForge`
3. **Configure**:
   ```
   Name: gyanforge-backend
   Runtime: Docker
   Dockerfile Path: ./Dockerfile
   ```

### **Step 3: Set Environment Variables**
In Render dashboard, add these environment variables:

```env
SECRET_KEY=3974950aa80601d1ad6dbf599fac7365197947fa24e828cbc8753da0c2049874
GEMINI_API_KEY=AIzaSyB-Isr6koIa-y7v_X9dsnxLECx_jwB-1ZM
PINECONE_API_KEY=pcsk_ZMLXS_A8tH79otW9BNxRJvoprJ8p3sJRhxxKDfCayS9Mff6MrhXz1wAvmMPkeCikChnMU
PINECONE_INDEX_NAME=gyanforge-data
DATABASE_URL=sqlite:///./gyanforge.db
ENVIRONMENT=production
```

### **Step 4: Deploy Frontend Separately**
1. **Create new "Static Site"** in Render
2. **Same repository**: `SSHRIHARI006/GyanForge`
3. **Configuration**:
   ```
   Build Command: cd frontend && npm ci && npm run build
   Publish Directory: frontend/build
   ```
4. **Environment Variables**:
   ```env
   REACT_APP_API_URL=https://gyanforge-backend.onrender.com
   REACT_APP_ENV=production
   ```

## 🎛️ **Docker Configuration Explained:**

### **Dockerfile Features:**
- ✅ **Multi-stage build** for optimization
- ✅ **Health checks** for monitoring
- ✅ **Environment variables** ready
- ✅ **Port 8000** exposed for Render
- ✅ **Production optimized**

### **Benefits of This Setup:**
- **Faster builds** - Docker caching
- **Consistent deployments** - Same environment everywhere
- **Better resource usage** - Optimized container
- **Health monitoring** - Built-in health checks

## 💡 **Alternative Free Docker Hosting:**

If Render still requires payment, try these **100% free Docker options**:

### **1. Railway (Recommended)**
```bash
# Deploy with Railway CLI
npx @railway/cli login
npx @railway/cli deploy
```

### **2. Fly.io (Free tier)**
```bash
# Install flyctl and deploy
curl -L https://fly.io/install.sh | sh
flyctl launch
flyctl deploy
```

### **3. DigitalOcean App Platform (Free tier)**
- Connect GitHub repository
- Select Docker deployment
- Deploy with free credits

## 🔧 **Testing Docker Locally:**

Before deploying, test the Docker setup locally:

```bash
# Build the Docker image
cd /home/shrihari/Desktop/GyanForge
docker build -t gyanforge-backend .

# Run the container
docker run -p 8000:8000 \
  -e SECRET_KEY=3974950aa80601d1ad6dbf599fac7365197947fa24e828cbc8753da0c2049874 \
  -e GEMINI_API_KEY=AIzaSyB-Isr6koIa-y7v_X9dsnxLECx_jwB-1ZM \
  -e PINECONE_API_KEY=pcsk_ZMLXS_A8tH79otW9BNxRJvoprJ8p3sJRhxxKDfCayS9Mff6MrhXz1wAvmMPkeCikChnMU \
  gyanforge-backend

# Test the API
curl http://localhost:8000/health
```

## 📊 **Expected Results:**

### **After Deployment:**
- **Backend URL**: `https://gyanforge-backend.onrender.com`
- **Frontend URL**: `https://gyanforge-frontend.onrender.com`
- **API Docs**: `https://gyanforge-backend.onrender.com/docs`
- **Health Check**: `https://gyanforge-backend.onrender.com/health`

### **Performance:**
- **Build Time**: ~5-8 minutes (Docker build)
- **Cold Start**: ~10-15 seconds
- **Response Time**: Fast (containerized)

## 🔍 **Troubleshooting:**

### **Common Issues:**
1. **Build fails**: Check Dockerfile syntax
2. **Health check fails**: Verify `/health` endpoint
3. **Environment variables**: Ensure all required vars are set
4. **Port issues**: Docker exposes port 8000

### **Debug Commands:**
```bash
# Check container logs
docker logs <container-id>

# Shell into container
docker exec -it <container-id> /bin/bash

# Test health endpoint
curl http://localhost:8000/health
```

---

🎯 **Try the Docker deployment on Render - it has the best chance of working without payment details!**
