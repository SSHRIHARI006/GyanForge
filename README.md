# GyanForge - Complete Production Setup Guide

GyanForge is a comprehensive AI-powered learning platform that provides personalized educational content, interactive quizzes, and assignment generation. This guide covers the complete production deployment setup.

## 🚀 Features

- **AI-Powered Learning Modules**: Generate personalized learning content using Google's Gemini AI
- **Interactive Learning Experience**: YouTube video integration, content display, and real-time chat interface
- **Intelligent Quiz System**: Adaptive quizzes with instant feedback and performance tracking
- **Assignment Generation**: LaTeX-based assignment creation and download
- **Dark Mode UI**: Modern, responsive interface with consistent dark theme
- **JWT Authentication**: Secure user authentication and session management
- **Real-time Chat**: AI tutor chatbot for interactive learning assistance

## 🛠 Tech Stack

### Frontend
- **React 19.1.0** - Modern UI framework
- **React Router** - Client-side routing
- **Tailwind CSS 3.3.0** - Utility-first styling with dark mode
- **Axios** - HTTP client for API communication
- **Lucide React** - Modern icon library

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLModel** - Modern SQL database ORM
- **PostgreSQL** - Primary database
- **JWT Authentication** - Secure token-based auth
- **Google Gemini AI** - Content generation
- **Langchain** - AI integration framework

## 📁 Project Structure

```
GyanForge/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React context providers
│   │   ├── services/        # API service layer
│   │   └── App.js          # Main application
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app entry
│   └── requirements.txt    # Backend dependencies
└── README.md              # This file
```

## 🚀 Production Deployment

### Prerequisites

- **Node.js 18+** and npm/yarn
- **Python 3.9+** and pip
- **PostgreSQL 12+**
- **Google Cloud Project** with Gemini API access
- **Domain name** and SSL certificate (recommended)

### 1. Environment Configuration

#### Backend Environment (.env)
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/gyanforge_db

# Security
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google AI
GOOGLE_API_KEY=your-google-gemini-api-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Environment
ENVIRONMENT=production
```

#### Frontend Environment (.env.production)
```bash
REACT_APP_API_BASE_URL=https://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
```

### 2. Database Setup

```bash
# Install PostgreSQL and create database
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb gyanforge_db
sudo -u postgres createuser gyanforge_user
sudo -u postgres psql -c "ALTER USER gyanforge_user PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gyanforge_db TO gyanforge_user;"
```

### 3. Backend Deployment

```bash
# Clone and setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

# Start production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Frontend Deployment

```bash
# Setup frontend
cd frontend
npm install

# Build for production
npm run build

# Serve with nginx or deploy to CDN
# The build folder contains the production-ready files
```

### 5. Production Server Configuration

#### Nginx Configuration
```nginx
# API Server
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend/build;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6. SSL Configuration (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Process Management (systemd)

#### Backend Service (/etc/systemd/system/gyanforge-api.service)
```ini
[Unit]
Description=GyanForge API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/backend/venv/bin
ExecStart=/path/to/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable gyanforge-api
sudo systemctl start gyanforge-api
sudo systemctl status gyanforge-api
```

## 🔧 Development Setup

### Quick Start
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
cp .env.development.example .env.development.local  # Edit with your values
npm start
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔐 Security Features

- **JWT Token Authentication**: Secure user sessions
- **Password Hashing**: bcrypt with salt
- **CORS Protection**: Configurable origin validation
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error boundaries and logging
- **Rate Limiting**: API rate limiting (configurable)

## 📊 Monitoring and Logging

### Production Logging
```python
# Add to backend/app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('gyanforge.log', maxBytes=10485760, backupCount=5),
            logging.StreamHandler()
        ]
    )
```

### Health Check Endpoint
```python
# Add to backend/app/api/v1/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check `ALLOWED_ORIGINS` in backend .env
   - Verify frontend API base URL

2. **Database Connection**
   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure user permissions

3. **AI API Errors**
   - Verify Google API key is valid
   - Check API quotas and limits
   - Review error logs

4. **Authentication Issues**
   - Verify JWT secret key is set
   - Check token expiration settings
   - Clear browser localStorage if needed

### Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates installed
- [ ] Nginx configuration tested
- [ ] Services enabled and running
- [ ] Logs monitoring setup
- [ ] Backup strategy implemented
- [ ] Domain DNS configured
- [ ] Security headers configured
- [ ] Performance monitoring setup

## 📈 Performance Optimization

### Frontend
- Build optimization with webpack
- CDN for static assets
- Image optimization
- Code splitting and lazy loading

### Backend
- Database connection pooling
- Redis caching (optional)
- API response caching
- Database query optimization

## 🔄 Updates and Maintenance

### Deployment Updates
```bash
# Backend updates
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
sudo systemctl restart gyanforge-api

# Frontend updates
git pull origin main
npm install
npm run build
# Deploy new build files
```

### Database Backups
```bash
# Create backup
pg_dump -h localhost -U gyanforge_user gyanforge_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql -h localhost -U gyanforge_user gyanforge_db < backup_file.sql
```

## 📞 Support

For issues and questions:
- Check logs: `sudo journalctl -u gyanforge-api -f`
- Review error boundaries in frontend
- Check API documentation at `/docs`
- Monitor system resources and database performance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎯 Production Ready**: This setup provides a complete, scalable, and secure deployment of GyanForge suitable for production use with proper monitoring, security, and performance optimizations.
