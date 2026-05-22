#!/bin/bash

echo "Setting up EduMind Study Planner..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Redis (Ubuntu/Debian)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y redis-server
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # MacOS
    brew install redis
    brew services start redis
fi

# Copy environment file
cp backend/.env.example backend/.env

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: uvicorn backend.app:app --reload"
echo "3. Run celery: celery -A backend.workers.celery_app worker --loglevel=info"
