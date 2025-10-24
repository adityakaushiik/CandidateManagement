from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.config import get_settings
from utils.logger import logger

# Create Base class for declarative models
Base = declarative_base()


class Database:

    def __init__(self):
        self.settings = get_settings()
        self.postgres = None
        self.client = None
        self.mongo = None
        self.engine = None

    async def init_postgres(self):
        """Initialize PostgreSQL connection"""
        if not self.settings.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in the environment variables.")

        self.engine = create_engine(
            self.settings.DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1200,  # Recycle connections every 20 minutes
            pool_pre_ping=True,  # Check connection validity before use
            connect_args={
                "connect_timeout": 10,  # PostgreSQL connection timeout
                "application_name": "CandidateManagementApp",
            },
        )
        self.postgres = sessionmaker(bind=self.engine)
        logger.info("Connected to PostgreSQL database.")

    async def init_mongo(self):
        """Initialize MongoDB connection"""
        self.client = AsyncIOMotorClient(self.settings.MONGODB_URL)
        self.mongo = self.client[self.settings.MONGODB_NAME]
        logger.info(f"Connected to {self.settings.MONGODB_NAME}")

    async def close(self):
        """Close all database connections"""
        if self.client:
            self.client.close()
        if self.engine:
            self.engine.dispose()

        logger.info(f"Database connection closed.")


db = Database()


async def get_db():
    try:
        yield db
    finally:
        pass
