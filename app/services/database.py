from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    database = None

async def get_database():
    return Database.database

async def get_collection(collection_name: str):
    database = await get_database()
    return database[collection_name]

async def init_db():
    """Initialize database connection"""
    try:
        Database.client = AsyncIOMotorClient(
            os.getenv("DATABASE_URL"),
            server_api=ServerApi('1')
        )
        
        # Test the connection
        Database.client.admin.command('ping')
        print("✅ Connected to MongoDB!")
        
        # Get database
        db_name = os.getenv("DATABASE_URL").split("/")[-1]
        Database.database = Database.client[db_name]
        
        # Create indexes for better performance
        await create_indexes()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = await get_database()
        
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("username", unique=True)
        
        # Inventory items indexes
        await db.inventory_items.create_index("sku", unique=True)
        await db.inventory_items.create_index("category")
        await db.inventory_items.create_index("status")
        
        # Transactions indexes
        await db.transactions.create_index("inventory_item_id")
        await db.transactions.create_index("created_at")
        
        print("✅ Database indexes created successfully")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")

async def close_db():
    """Close database connection"""
    if Database.client:
        Database.client.close()
        print("✅ Database connection closed")
