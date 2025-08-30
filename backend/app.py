from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import db
from routes import session_routes, chat_routes, auth_route

# Create FastAPI app
app = FastAPI(
    title="Interview Bot API",
    description="AI-powered interview bot with MongoDB backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database events
@app.on_event("startup")
async def startup_db_client():
    await db.connect_db()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_db()

# Include routers
app.include_router(auth_route.router)
app.include_router(session_routes.router)
app.include_router(chat_routes.router)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Interview Bot API is running! 🚀"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for monitoring and debugging."""
    import time
    from datetime import datetime
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Interview Bot API",
        "version": "1.0.0",
        "uptime": time.time(),  # Unix timestamp for uptime calculation
        "checks": {
            "database": "unknown",
            "ai_service": "unknown",
            "memory": "unknown"
        }
    }
    
    # Check database connection
    try:
        if db.database is not None:
            # Test database connectivity
            await db.database.command("ping")
            health_status["checks"]["database"] = "healthy"
        else:
            health_status["checks"]["database"] = "disconnected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check AI service (OpenRouter API key)
    try:
        from services.ai_service import ai_service
        if ai_service.api_key:
            health_status["checks"]["ai_service"] = "configured"
        else:
            health_status["checks"]["ai_service"] = "no_api_key"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["ai_service"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent_used": memory.percent
        }
        
        # Mark as degraded if memory usage is high
        if memory.percent > 90:
            health_status["status"] = "degraded"
            health_status["checks"]["memory"]["warning"] = "High memory usage"
    except ImportError:
        health_status["checks"]["memory"] = "psutil_not_installed"
    except Exception as e:
        health_status["checks"]["memory"] = f"error: {str(e)}"
    
    # Overall status determination
    if health_status["status"] == "healthy":
        health_status["message"] = "All systems operational"
    elif health_status["status"] == "degraded":
        health_status["message"] = "Some systems have issues"
    else:
        health_status["status"] = "unhealthy"
        health_status["message"] = "Critical systems are down"
    
    return health_status
