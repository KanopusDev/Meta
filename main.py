from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
from app.utils.db import db
import logging.config
from app.core.logging_config import LOGGING_CONFIG
from app.api import whatsapp, instagram, template_routes, stats
from app.core.config import settings
from app.middleware.auth import auth_middleware

app = FastAPI(
    title="Meta Messaging API",
    description="API for WhatsApp and Instagram messaging",
    version="1.0.0"
)

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Additional middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Metrics
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(instagram.router, prefix="/api/instagram", tags=["Instagram"])
app.include_router(template_routes.router, prefix="/api/templates", tags=["Templates"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])

@app.on_event("startup")
async def startup_event():
    try:
        await db.connect()
        logger.info("Application startup completed")
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    await db.close()
    logger.info("Application shutdown completed")

# Add authentication middleware
app.middleware("http")(auth_middleware)

# Add request validation middleware
@app.middleware("http")
async def validate_request(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return JSONResponse(
                status_code=400,
                content={"detail": "Content-Type must be application/json"}
            )
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
