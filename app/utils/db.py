import motor.motor_asyncio
from pymongo.errors import ConnectionFailure, OperationFailure
from app.core.config import settings
import logging
from datetime import datetime
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.DATABASE_URL,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=100,
                minPoolSize=20
            )
            self.db = self.client.meta_messaging
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

db = Database()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def save_message(message: dict, message_id: str) -> bool:
    try:
        result = await db.db.messages.insert_one({
            "message_id": message_id,
            "recipient": message.recipient,
            "content": message.dict(),
            "created_at": datetime.utcnow(),
            "status": "sent"
        })
        return bool(result.inserted_id)
    except OperationFailure as e:
        logger.error(f"Failed to save message: {e}")
        raise

async def get_message_history(phone_number: str, limit: int = 100) -> List[dict]:
    try:
        cursor = db.db.messages.find(
            {"recipient": phone_number},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    except OperationFailure as e:
        logger.error(f"Failed to fetch message history: {e}")
        raise

async def update_message_status(message_id: str, status: str) -> bool:
    try:
        result = await db.db.messages.update_one(
            {"message_id": message_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except OperationFailure as e:
        logger.error(f"Failed to update message status: {e}")
        raise
