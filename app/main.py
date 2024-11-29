from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import whatsapp, instagram, templates
from app.core.config import settings

app = FastAPI(
    title="Meta Messaging API",
    description="API for WhatsApp and Instagram messaging",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(instagram.router, prefix="/api/instagram", tags=["Instagram"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])

@app.get("/")
async def root():
    return {"message": "Welcome to Meta Messaging API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
