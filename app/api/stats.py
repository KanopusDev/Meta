
from fastapi import APIRouter
from app.utils.db import get_message_stats

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats():
    stats = await get_message_stats()
    return {
        "total_messages": stats.get("total", 0),
        "whatsapp_messages": stats.get("whatsapp", 0),
        "instagram_messages": stats.get("instagram", 0),
        "recent_messages": stats.get("recent", [])
    }