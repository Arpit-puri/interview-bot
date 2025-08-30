from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from .constants import DATABASE_NAME

load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

class Database:
    client: AsyncIOMotorClient = None
    database = None
    
    @classmethod
    async def connect_db(cls):
        """Create database connection."""
        cls.client = AsyncIOMotorClient(MONGODB_URL)
        cls.database = cls.client[DATABASE_NAME]
        print("✅ Connected to MongoDB.")
        
    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            print("✅ Disconnected from MongoDB.")
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database."""
        if cls.database is None:
            raise RuntimeError("Database not connected. Call connect_db() first.")
        return cls.database[collection_name]

# Database instance
db = Database()
