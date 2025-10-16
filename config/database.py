from motor.motor_asyncio import AsyncIOMotorClient

from config.config import get_settings


class Database:
    client: AsyncIOMotorClient = None
    database = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    settings = get_settings()
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.database = db.client[settings.MONGODB_NAME]
    print(f"Connected to MongoDB")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("Closed MongoDB connection")


def get_database():
    """Get database instance"""
    return db.database
