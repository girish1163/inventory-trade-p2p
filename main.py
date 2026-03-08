from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routers import auth, inventory
from app.services.mongodb_db import db

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MongoDB connection
    connected = await db.connect()
    if not connected:
        print("⚠️  Running without database connection")
    yield
    # Cleanup can be added here if needed

app = FastAPI(
    title="Inventory Management System",
    description="A comprehensive inventory management API built with FastAPI and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])

# Serve static files (React build)
app.mount("/static", StaticFiles(directory="client/build/static"), name="static")

@app.get("/")
async def root():
    return {"message": "Inventory Management System API is running...", "database": "MongoDB"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "MongoDB"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
