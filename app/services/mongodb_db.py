from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pymongo import ASCENDING, DESCENDING
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from bson import ObjectId
import json

load_dotenv()

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://69ad03997f876f9874464515@cluster.mongodb.net/inventory_management_fastapi?retryWrites=true&w=majority")
        # Extract database name from URL or use default
        if "/inventory_management_fastapi" in self.mongodb_url:
            self.db_name = "inventory_management_fastapi"
        else:
            self.db_name = self.mongodb_url.split("/")[-1].split("?")[0]
    
    async def connect(self):
        """Initialize MongoDB connection"""
        try:
            self.client = AsyncIOMotorClient(
                self.mongodb_url,
                server_api=ServerApi('1'),
                tlsAllowInvalidCertificates=True  # Add this if using MongoDB Atlas with connection issues
            )
            
            # Test the connection
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas!")
            
            # Get database
            self.database = self.client[self.db_name]
            
            # Create indexes for better performance
            await self.create_indexes()
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            print("⚠️  Make sure your MongoDB Atlas connection string is correct")
            return False
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("username", unique=True)
            
            # Inventory items indexes
            await self.database.inventory_items.create_index("sku", unique=True)
            await self.database.inventory_items.create_index("category")
            await self.database.inventory_items.create_index("status")
            
            # Transactions indexes
            await self.database.transactions.create_index("inventory_item_id")
            await self.database.transactions.create_index("created_at")
            
            print("✅ Database indexes created successfully")
            
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection"""
        return self.database[collection_name]
    
    async def find_all(self, collection_name: str, query: Dict = None) -> List[Dict[str, Any]]:
        """Find all documents in a collection"""
        try:
            collection = self.get_collection(collection_name)
            if query is None:
                query = {}
                
            cursor = collection.find(query)
            documents = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['id'] = str(doc['_id'])
                    del doc['_id']
            
            return documents
        except Exception as e:
            print(f"❌ Error finding documents in {collection_name}: {e}")
            return []
    
    async def find_one(self, collection_name: str, query: Dict) -> Optional[Dict[str, Any]]:
        """Find one document in a collection"""
        try:
            collection = self.get_collection(collection_name)
            document = await collection.find_one(query)
            
            if document:
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']
                return document
            
            return None
        except Exception as e:
            print(f"❌ Error finding document in {collection_name}: {e}")
            return None
    
    async def find_by_id(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Find a document by ID"""
        try:
            collection = self.get_collection(collection_name)
            document = await collection.find_one({"_id": ObjectId(document_id)})
            
            if document:
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']
                return document
            
            return None
        except Exception as e:
            print(f"❌ Error finding document {document_id} in {collection_name}: {e}")
            return None
    
    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert one document into a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error inserting document in {collection_name}: {e}")
            return None
    
    async def update_one(self, collection_name: str, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update one document in a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error updating document {document_id} in {collection_name}: {e}")
            return False
    
    async def delete_one(self, collection_name: str, document_id: str) -> bool:
        """Delete one document from a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = await collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ Error deleting document {document_id} in {collection_name}: {e}")
            return False
    
    async def find_one_and_update(self, collection_name: str, query: Dict, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document and update it"""
        try:
            collection = self.get_collection(collection_name)
            document = await collection.find_one_and_update(
                query,
                {"$set": update_data},
                return_document=True
            )
            
            if document:
                if '_id' in document:
                    document['id'] = str(document['_id'])
                    del document['_id']
                return document
            
            return None
        except Exception as e:
            print(f"❌ Error finding and updating document in {collection_name}: {e}")
            return None
    
    async def count_documents(self, collection_name: str, query: Dict = None) -> int:
        """Count documents in a collection"""
        try:
            collection = self.get_collection(collection_name)
            if query is None:
                query = {}
            return await collection.count_documents(query)
        except Exception as e:
            print(f"❌ Error counting documents in {collection_name}: {e}")
            return 0

# Global instance
db = MongoDB()

async def get_db():
    """Get database instance"""
    return db
