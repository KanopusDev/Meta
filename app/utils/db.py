import aiosqlite
import json
import logging
import os
from datetime import datetime
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._test_mode = False
        self.health_status = False
        
        # Create data directory if not exists
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        if settings.is_production:
            self.db_path = settings.DATABASE_URL
        else:
            self.db_path = os.path.join(self.data_dir, 'messages.db')

    def enable_test_mode(self):
        self._test_mode = True
        self.db_path = ":memory:"

    async def connect(self):
        try:
            if not self._test_mode:
                # Ensure directory exists and is writable
                db_dir = os.path.dirname(self.db_path)
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                
                if not os.access(db_dir, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {db_dir}")

            self.conn = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            self.health_status = True
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            self.health_status = False
            logger.error(f"Database connection failed: {str(e)}", exc_info=True)
            raise

    async def _create_tables(self):
        async with self.conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    recipient TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent'
                )
            """)
            await self.conn.commit()

    async def close(self):
        if hasattr(self, 'conn'):
            await self.conn.close()
            logger.info("Database connection closed")

    async def clear_test_data(self):
        if self._test_mode:
            async with self.conn.cursor() as cur:
                await cur.execute("DELETE FROM messages")
                await self.conn.commit()

    async def check_health(self):
        try:
            async with self.conn.cursor() as cur:
                await cur.execute("SELECT 1")
                return True
        except:
            return False

db = Database()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def save_message(message: dict, message_id: str) -> bool:
    try:
        async with db.conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO messages (message_id, recipient, content, status)
                VALUES (?, ?, ?, ?)
                """,
                (message_id, message.recipient, json.dumps(message.dict()), "sent")
            )
            await db.conn.commit()
            return True
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise

async def get_message_history(phone_number: str, limit: int = 100) -> List[dict]:
    try:
        async with db.conn.cursor() as cur:
            await cur.execute(
                """
                SELECT message_id, content, created_at, status
                FROM messages 
                WHERE recipient = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (phone_number, limit)
            )
            rows = await cur.fetchall()
            return [
                {
                    "message_id": row[0],
                    "content": json.loads(row[1]),
                    "created_at": row[2],
                    "status": row[3]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Failed to fetch message history: {e}")
        raise

async def update_message_status(message_id: str, status: str) -> bool:
    try:
        async with db.conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE messages
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE message_id = ?
                """,
                (status, message_id)
            )
            await db.conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to update message status: {e}")
        raise

async def get_message_stats():
    """Get messaging statistics from the database"""
    async with db.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM messages")
        whatsapp = await conn.fetchval("SELECT COUNT(*) FROM messages WHERE platform = 'whatsapp'")
        instagram = await conn.fetchval("SELECT COUNT(*) FROM messages WHERE platform = 'instagram'")
        recent = await conn.fetch(
            """
            SELECT * FROM messages 
            ORDER BY created_at DESC 
            LIMIT 10
            """
        )
        return {
            "total": total,
            "whatsapp": whatsapp,
            "instagram": instagram,
            "recent": [dict(msg) for msg in recent]
        }

async def save_template(template_data: dict):
    """Save template to database"""
    async with db.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO templates (name, category, language_code, components)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            template_data["name"],
            template_data["category"],
            template_data["language_code"],
            template_data["components"]
        )
