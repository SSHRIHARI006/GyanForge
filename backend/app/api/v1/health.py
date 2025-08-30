from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from datetime import datetime
import psutil
import os

from app.db.session import get_session

router = APIRouter()

@router.get("/health")
async def health_check(session: Session = Depends(get_session)):
    """
    Comprehensive health check endpoint for monitoring
    """
    try:
        # Check database connectivity
        result = session.exec(text("SELECT 1")).first()
        db_status = "healthy" if result else "unhealthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check environment variables
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL', 'GOOGLE_API_KEY']
    env_status = {}
    for var in required_env_vars:
        env_status[var] = "set" if os.getenv(var) else "missing"
    
    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": {
            "status": db_status,
            "connection": "ok" if db_status == "healthy" else "failed"
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        },
        "environment": env_status,
        "uptime": datetime.utcnow().isoformat()
    }
    
    return health_data

@router.get("/health/simple")
async def simple_health_check():
    """Simple health check for load balancers"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.get("/health/ready")
async def readiness_check(session: Session = Depends(get_session)):
    """Readiness check for Kubernetes/deployment systems"""
    try:
        # Test database connection
        session.exec(text("SELECT 1")).first()
        
        # Check required environment variables
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        for var in required_vars:
            if not os.getenv(var):
                return {"status": "not_ready", "reason": f"Missing {var}"}
        
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}

@router.get("/health/live")
async def liveness_check():
    """Liveness check for container orchestration"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
