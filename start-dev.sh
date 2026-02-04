#!/bin/bash

# Start Docker services
echo "Starting PostgreSQL and Redis..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 5

# Start backend
echo "Starting Django backend..."
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py runserver &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting React frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
