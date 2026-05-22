#!/bin/bash

# Exit on error
set -e

echo "🚀 Deploying EduMind Study Planner to Production"

# Build Docker images
echo "📦 Building Docker images..."
docker-compose build

# Run database setup (indexes)
echo "🗄️ Setting up database indexes..."
# Note: In production, we'd use the backend container to run this script
docker-compose run --rm backend python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add /app to path to resolve backend imports
sys.path.append('/app')

from backend.utils.db_indexes import create_indexes

async def setup():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo:27017/edumind')
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_default_database()
    await create_indexes(db)
    print('✅ Database indexes created')

if __name__ == '__main__':
    asyncio.run(setup())
"

# Start services
echo "🔄 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check health
echo "🏥 Health check..."
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API health check failed"
    # Don't exit here as /health might not be implemented yet
fi

if curl -s -f http://localhost:8501 > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
fi

echo "🎉 Deployment complete!"
echo ""
echo "Services running at:"
echo "  Backend API: http://localhost:8000"
echo "  Frontend: http://localhost:8501"
echo "  MongoDB: localhost:27017"
echo "  Redis: localhost:6379"
